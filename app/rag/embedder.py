from __future__ import annotations

from openai import OpenAI

from app.config import get_settings

settings = get_settings()


class OpenAIEmbedder:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model

    def embed_texts(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        embeddings: list[list[float]] = []

        for idx in range(0, len(texts), batch_size):
            batch = texts[idx : idx + batch_size]
            response = self.client.embeddings.create(
                model=self.model,
                input=batch,
            )
            embeddings.extend(item.embedding for item in response.data)

        return embeddings

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=[text],
        )
        return response.data[0].embedding