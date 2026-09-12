"""
Thin wrapper around sentence-transformers so the rest of the app doesn't need
to know which embedding model we're using or worry about re-loading it.

The model is loaded lazily and cached at module level - the first call pays
the (one-time) cost of loading weights, every call after is fast.
"""

from functools import lru_cache

from src.settings import settings


@lru_cache(maxsize=1)
def get_embedding_model():
    # Imported lazily: sentence-transformers pulls in torch, which is slow
    # to import and unnecessary for any code path that doesn't embed text.
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns one vector per input text, same order."""
    model = get_embedding_model()
    vectors = model.encode(texts, show_progress_bar=len(texts) > 50, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """Embed a single query string (e.g. a user's question)."""
    return embed_texts([text])[0]


def get_embedding_dimension() -> int:
    model = get_embedding_model()
    return model.get_embedding_dimension()