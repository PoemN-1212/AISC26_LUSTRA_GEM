"""
GEM Skill Extractor (Module trích xuất kỹ năng kết hợp Verifier)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
Hỗ trợ cả Qwen Local (qua Ollama) và Gemini Cloud fallback
"""

import os
import re
import sys
import json
import time
from typing import List, Dict, Any, Tuple, Optional
import urllib.request
from google import genai
from google.genai import types
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from gem_pipeline.extraction.prompts import (
    SYSTEM_PROMPT_EXTRACTION,
    build_extraction_prompt,
    build_student_prompt
)
from gem_pipeline.extraction.verifier import SkillExtractionVerifier, VerificationResult

load_dotenv()


class SkillExtractor:
    """
    Module phụ trách tương tác với LLM để trích xuất kỹ năng,
    hỗ trợ cả chế độ Baseline (chỉ dùng Prompt) và chế độ Verifier (Prompt + Kiểm định 5 bước).
    """

    def __init__(
        self,
        backend: str = "auto",                  # 'auto' | 'ollama' | 'gemini'
        ollama_model: str = "qwen2.5:7b",       # Mặc định qwen2.5:7b cho chất lượng cao nhất
        ollama_base_url: str = "http://localhost:11434",
        api_key: Optional[str] = None,
        gemini_models: Optional[List[str]] = None,
        use_few_shot: bool = True
    ):
        self.backend = os.getenv("LLM_BACKEND", backend).lower()
        self.ollama_model = os.getenv("OLLAMA_MODEL", ollama_model)
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", ollama_base_url)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.gemini_models = gemini_models or ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]
        self.use_few_shot = use_few_shot
        self.verifier = SkillExtractionVerifier()

    def _is_ollama_available(self) -> bool:
        """Kiểm tra tức thì xem Ollama server (cổng 11434) có đang bật không."""
        import socket
        try:
            with socket.create_connection(("127.0.0.1", 11434), timeout=0.3):
                return True
        except Exception:
            return False

    def _call_ollama(self, prompt: str) -> str:
        """Gọi Qwen qua Ollama Local API (hoàn toàn offline, không tốn API key)."""
        options = {
            "temperature": 0.1,
            "num_predict": 1024,
            "num_ctx": 4096,
            "stop": ["\n\n---", "<|im_end|>", "<|endoftext|>"]
        }
        # Cấu hình tối ưu GPU offload cho 7B trên card 4GB VRAM
        if "7b" in self.ollama_model.lower():
            options["num_gpu"] = int(os.getenv("OLLAMA_NUM_GPU", "16"))

        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": options
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.ollama_base_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                resp_text = result.get("response", "[]").strip()
                return resp_text
        except Exception as e:
            print(f"  ❌ Lỗi kết nối Ollama ({self.ollama_model}): {e}")
            return "[]"

    def _call_llm(self, prompt: str, max_retries: int = 3) -> str:
        """Gửi prompt tới LLM (tự động chọn Qwen Ollama nếu đang chạy, hoặc Gemini cloud)."""
        active_backend = self.backend
        if active_backend == "auto":
            active_backend = "ollama" if self._is_ollama_available() else "gemini"

        if active_backend == "ollama":
            raw_text = self._call_ollama(prompt)
            if raw_text and raw_text != "[]":
                return self._clean_json_fence(raw_text)
            if self.backend == "ollama":
                # Người dùng chỉ định rõ backend=ollama: giữ tính độc lập tuyệt đối, không fallback sang Gemini
                return self._clean_json_fence(raw_text or "[]")
            print("  ⚠ Chuyển sang Gemini cloud dự phòng do Ollama không phản hồi.")

        # Gọi Gemini Cloud
        if not self.client:
            raise ValueError("Cần khởi động Ollama (http://localhost:11434) hoặc thiết lập GEMINI_API_KEY trong .env!")

        for model_name in self.gemini_models:
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.1,
                            response_mime_type="application/json",
                        ),
                    )
                    return self._clean_json_fence(response.text.strip())
                except Exception as e:
                    err = str(e)
                    if any(code in err for code in ["429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE"]):
                        sleep_time = 3 * (attempt + 1)
                        print(f"  ⚠ LLM rate limited, chờ {sleep_time}s thử lại lần {attempt+1}...")
                        time.sleep(sleep_time)
                    else:
                        print(f"  ❌ Lỗi gọi Gemini ({model_name}): {err[:100]}")
                        break
        return "[]"

    @staticmethod
    def _clean_json_fence(raw_text: str) -> str:
        """Bỏ markdown code block json nếu có."""
        text = raw_text.strip()
        # Ưu tiên bắt toàn bộ JSON array [...]
        match_arr = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
        if match_arr:
            return match_arr.group(0).strip()

        # Bắt JSON object {...}
        match_obj = re.search(r"\{.*\}", text, re.DOTALL)
        if match_obj:
            return match_obj.group(0).strip()

        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def parse_candidates(self, raw_json_str: str) -> List[Dict[str, Any]]:
        """Parse và chuẩn hóa danh sách candidate từ chuỗi JSON của LLM."""
        data = None
        try:
            data = json.loads(raw_json_str)
        except Exception:
            # Fallback 1: Tự động đóng mảng nếu bị ngắt stream ở cuối (thiếu ']')
            trimmed = raw_json_str.strip()
            if trimmed.startswith("[") and not trimmed.endswith("]"):
                try:
                    last_brace = trimmed.rfind("}")
                    if last_brace != -1:
                        data = json.loads(trimmed[:last_brace + 1] + "\n]")
                except Exception:
                    pass

            # Fallback 2: Quét mọi JSON object {...} hoàn chỉnh nếu mảng bị vỡ
            if data is None:
                matches = re.findall(r"\{[^{}]+\}", raw_json_str)
                objs = []
                for m in matches:
                    try:
                        o = json.loads(m)
                        if isinstance(o, dict) and (o.get("skill") or o.get("evidence") or o.get("name")):
                            objs.append(o)
                    except Exception:
                        continue
                if objs:
                    data = objs

        try:
            raw_list = []
            if isinstance(data, list):
                raw_list = data
            elif isinstance(data, dict):
                # Trường hợp LLM bọc trong {"skills": [...]} hoặc trả về 1 object đơn lẻ
                for k in ["skills", "candidates", "data", "result", "items"]:
                    if k in data and isinstance(data[k], list):
                        raw_list = data[k]
                        break
                if not raw_list and (data.get("evidence") or data.get("skill") or data.get("name")):
                    raw_list = [data]

            valid = []
            for item in raw_list:
                if isinstance(item, dict):
                    skill_name = item.get("skill") or item.get("name") or item.get("technology") or ""
                    evidence_str = item.get("evidence") or skill_name
                    if skill_name or evidence_str:
                        valid.append({
                            "evidence": str(evidence_str or skill_name).strip(),
                            "skill": str(skill_name or evidence_str).strip(),
                            "type": str(item.get("type", "TECHNOLOGY")).strip().upper(),
                            "context": str(item.get("context", "required")).strip().lower()
                        })
                elif isinstance(item, str) and len(item.strip()) >= 2:
                    s = item.strip()
                    valid.append({
                        "evidence": s,
                        "skill": s,
                        "type": "TECHNOLOGY",
                        "context": "required"
                    })
            return valid
        except Exception:
            pass
        return []

    def extract_baseline(self, text: str, prompt_type: str = "guideline") -> List[Dict[str, Any]]:
        """
        Chế độ Baseline: Chỉ dùng Prompt LLM thuần, KHÔNG qua bước Verifier.
        prompt_type:
          - 'guideline': Teacher Prompt đầy đủ theo GEM Annotation Guideline (cho Golden Set).
          - 'student': Inference Prompt tự nhiên độc lập (cho Benchmark / Thực tế).
        """
        if prompt_type == "student":
            prompt = build_student_prompt(text)
        else:
            prompt = build_extraction_prompt(text, use_few_shot=self.use_few_shot)
        raw_json = self._call_llm(prompt)
        return self.parse_candidates(raw_json)

    def extract_with_verifier(
        self,
        text: str,
        prompt_type: str = "guideline"
    ) -> Tuple[List[VerificationResult], List[VerificationResult]]:
        """
        Chế độ GEM Pipeline: Kết hợp Prompt LLM + Verifier 5 lớp.
        Trả về 2 danh sách:
        1. accepted_skills: Danh sách các kỹ năng hợp lệ / đã chuẩn hóa ranh giới.
        2. rejected_skills: Danh sách các kỹ năng bị loại bỏ kèm lý do (ảo giác, chức danh, từ thừa...).
        """
        candidates = self.extract_baseline(text, prompt_type=prompt_type)
        verified_results = self.verifier.verify_document_skills(candidates, text)

        accepted = [r for r in verified_results if r.is_valid]
        rejected = [r for r in verified_results if not r.is_valid]
        return accepted, rejected
