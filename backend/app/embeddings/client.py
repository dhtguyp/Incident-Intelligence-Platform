"""Embedding provider boundary used by ingestion and later retrieval."""
from __future__ import annotations

import os
from typing import Protocol

from google import genai
from google.genai import types


class EmbeddingClient(Protocol):
    def embed(self, text: str, *, task_type: str) -> list[float]: ...


class GeminiEmbeddingClient:
    """Gemini text-embedding adapter with a 768-dimensional output."""

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is required to generate embeddings.")
        self.client = genai.Client(api_key=key)

    def embed(self, text: str, *, task_type: str) -> list[float]:
        response = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type.upper(),
                output_dimensionality=768,
            ),
        )
        return list(response.embeddings[0].values)
