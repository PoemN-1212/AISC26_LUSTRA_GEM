"""
LLM Client for GEM Advisor (Dual-Engine: Gemini Flash & Ollama Qwen Local).
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
"""

import os
import re
import json
import urllib.request
from typing import Optional, Dict, Any


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
    - Ưu tiên mô hình cực nhanh và chuẩn xác: gemini-3.5-flash-lite / gemini-2.5-flash
    - Cơ chế chuyển mạch dự phòng mượt mà sang Ollama Qwen 2.5 local (11434)
    """

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
                self._gemini_client = genai.Client(api_key=self.gemini_key)
            except Exception:
                self._gemini_client = None
        return self._gemini_client

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 2048) -> str:
        """Thực thi gọi LLM với cơ chế fallback tự động."""
        # 1. Thử gọi Gemini Flash trước (độ trễ < 1.5s, định dạng chuẩn)
        client = self._get_gemini_client()
        if client:
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception:
                pass

        # 2. Thử gọi Ollama Qwen local
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }
            req = urllib.request.Request(
                f"{self.ollama_base_url}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=40) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                output = res_data.get("response", "").strip()
                if output:
                    return output
        except Exception:
            pass

        return ""
