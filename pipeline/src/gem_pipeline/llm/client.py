"""
LLM Client for GEM Advisor (Dual-Engine: Gemini Flash & Ollama Qwen Local).
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
"""

import time
import os
import re
import json
import urllib.request
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


def clean_json_markdown(raw_text: str) -> str:
    """Loại bỏ markdown fences (```json ... ```) để parse JSON an toàn."""
    text = (raw_text or "").strip()
    if "```json" in text:
        text = text.split("```json", 1)[1]
    elif "```" in text:
        text = text.split("```", 1)[1]
    if "```" in text:
        text = text.split("```", 1)[0]
    return text.strip()


class GEMAdvisorLLM:
    """
    Client gọi LLM chuyên biệt cho GEM:
    - Ưu tiên mô hình cực nhanh: Google Gemini Flash
    - Circuit Breaker thông minh: Tự động ngắt kết nối Gemini khi hết quota (429) hoặc lỗi mạng, chuyển tức thì sang Ollama Qwen 2.5 local (0s overhead)
    - GPU offload cho Ollama local đảm bảo độ phản hồi 5-8s
    """

    _gemini_disabled_until: float = 0.0

    def __init__(
        self,
        gemini_key: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        ollama_model: Optional[str] = None,
    ):
        self.gemini_key = gemini_key or os.getenv("GEMINI_API_KEY")
        self.ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self._gemini_client = None

    def _get_gemini_client(self):
        if not self._gemini_client and self.gemini_key:
            try:
                from google import genai
                from google.genai import types
                self._gemini_client = genai.Client(
                    api_key=self.gemini_key,
                    http_options=types.HttpOptions(timeout=30000),
                )
            except Exception:
                self._gemini_client = None
        return self._gemini_client

    @classmethod
    def is_gemini_active(cls) -> bool:
        """Kiểm tra xem Gemini Cloud API có đang hoạt động và không bị ngắt mạch không."""
        return time.time() >= cls._gemini_disabled_until and bool(os.getenv("GEMINI_API_KEY"))

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 500) -> str:
        """Thực thi gọi LLM với cơ chế circuit-breaker và fallback tự động tốc độ cao."""
        now = time.time()

        # 1. Thử gọi Gemini nếu Circuit Breaker không đóng
        if now >= GEMAdvisorLLM._gemini_disabled_until:
            client = self._get_gemini_client()
            if client:
                try:
                    from google.genai import types
                    config = types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    )
                    candidate_models = [
                        os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest"),
                        "gemini-flash-lite-latest",
                        "gemini-3.5-flash-lite",
                        "gemini-3.8-flash",
                        "gemini-flash-latest",
                    ]
                    seen = set()
                    models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

                    for model_name in models_to_try:
                        try:
                            response = client.models.generate_content(
                                model=model_name,
                                contents=prompt,
                                config=config,
                            )
                            if response and response.text:
                                return response.text.strip()
                        except Exception as ex:
                            err_msg = str(ex).lower()
                            print(f"[GEMAdvisorLLM] Candidate {model_name} failed: {ex}")
                            if any(k in err_msg for k in ["503", "unavailable", "404", "not_found", "429", "quota", "resource_exhausted", "504", "deadline_exceeded", "timeout"]):
                                continue
                            else:
                                break

                    print(f"[GEMAdvisorLLM] All Gemini candidate models failed. Circuit Breaker activated for 10m, switching to Ollama.")
                    GEMAdvisorLLM._gemini_disabled_until = now + 600
                except Exception as ex:
                    print(f"[GEMAdvisorLLM] Gemini client exception: {ex}")
                    GEMAdvisorLLM._gemini_disabled_until = now + 600

        # 2. Thử gọi Ollama Qwen local có GPU offload
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "num_gpu": 16,
                    "num_ctx": 2048,
                },
            }
            req = urllib.request.Request(
                f"{self.ollama_base_url}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                output = res_data.get("response", "").strip()
                if output:
                    return output
        except Exception as o_err:
            print(f"[GEMAdvisorLLM] Ollama call error: {o_err}")

        return ""
