from functools import lru_cache
from sentence_transformers import SentenceTransformer

from core.recsys_config import SENTENCE_TRANSFORMER_MODEL


@lru_cache
def get_text2vec_model() -> SentenceTransformer:
    return SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
