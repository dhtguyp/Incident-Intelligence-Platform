"""LLM provider boundary and Gemini implementation."""
from __future__ import annotations

import asyncio
import os
from typing import Protocol

from google import genai
from google.genai import types

from app.llm.models import IncidentAnalysis


class LLMProviderError(RuntimeError):
    pass


class LLMClient(Protocol):
    async def analyze_incident(self, prompt: str) -> str: ...


class GeminiLLMClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise LLMProviderError("GEMINI_API_KEY is required to analyze an incident.")
        self.client = genai.Client(api_key=key)
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    async def analyze_incident(self, prompt: str) -> str:
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=IncidentAnalysis,
                ),
            )
        except Exception as exc:
            raise LLMProviderError("Gemini incident analysis request failed.") from exc
        if not response.text:
            raise LLMProviderError("Gemini returned an empty incident analysis response.")
        return response.text
