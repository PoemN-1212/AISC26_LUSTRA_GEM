"""
GEM Skill Extractor (Module trích xuất kỹ năng kết hợp Verifier)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
Hỗ trợ cả Qwen Local (qua Ollama) và Gemini Cloud fallback
"""

import os
import re
import json
import time
from typing import List, Dict, Any, Tuple, Optional
import urllib.request
from google import genai
from google.genai import types
from dotenv import load_dotenv

from gem_pipeline.extraction.prompts import SYSTEM_PROMPT_EXTRACTION, build_extraction_prompt
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
        ollama_model: str = "qwen2.5:3b",       # Mặc định qwen2.5:3b (hoặc qwen2.5:7b)
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
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 2048,
                "num_ctx": 2048
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.ollama_base_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
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
                        time.sleep(2 * (attempt + 1))
                    else:
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
        try:
            data = json.loads(raw_json_str)
            raw_list = []
            if isinstance(data, list):
                raw_list = data
            elif isinstance(data, dict):
                # Trường hợp LLM bọc trong {"skills": [...]} hoặc trả về 1 object đơn lẻ
                for k in ["skills", "candidates", "data", "result", "items"]:
                    if k in data and isinstance(data[k], list):
                        raw_list = data[k]
                        break
                if not raw_list and data.get("evidence"):
                    raw_list = [data]

            valid = []
            for item in raw_list:
                if isinstance(item, dict) and item.get("evidence"):
                    valid.append({
                        "evidence": str(item.get("evidence", "")).strip(),
                        "skill": str(item.get("skill", item.get("evidence", ""))).strip(),
                        "type": str(item.get("type", "TECHNOLOGY")).strip().upper(),
                        "context": str(item.get("context", "required")).strip().lower()
                    })
            return valid
        except Exception:
            pass
        return []

    def extract_baseline(self, text: str) -> List[Dict[str, Any]]:
        """
        Chế độ Baseline: Chỉ dùng Prompt LLM thuần, KHÔNG qua bước Verifier.
        Dùng để làm đối chứng đo lường hiệu năng (Baseline Evaluation).
        """
        prompt = build_extraction_prompt(text, use_few_shot=self.use_few_shot)
        raw_json = self._call_llm(prompt)
        return self.parse_candidates(raw_json)

    def extract_with_verifier(
        self,
        text: str
    ) -> Tuple[List[VerificationResult], List[VerificationResult]]:
        """
        Chế độ GEM Pipeline: Kết hợp Prompt LLM + Verifier 5 lớp.
        Trả về 2 danh sách:
        1. accepted_skills: Danh sách các kỹ năng hợp lệ / đã chuẩn hóa ranh giới.
        2. rejected_skills: Danh sách các kỹ năng bị loại bỏ kèm lý do (ảo giác, chức danh, từ thừa...).
        """
        candidates = self.extract_baseline(text)
        verified_results = self.verifier.verify_document_skills(candidates, text)

        accepted = [r for r in verified_results if r.is_valid]
        rejected = [r for r in verified_results if not r.is_valid]
        return accepted, rejected
