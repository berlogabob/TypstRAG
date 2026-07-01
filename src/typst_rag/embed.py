from functools import lru_cache

from sentence_transformers import SentenceTransformer

from .config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_passages(texts: list[str]) -> list[list[float]]:
    vectors = model().encode(["passage: " + t for t in texts], batch_size=32, normalize_embeddings=True)
    return [v.tolist() for v in vectors]


def embed_query(query: str) -> list[float]:
    return model().encode("query: " + query, normalize_embeddings=True).tolist()
