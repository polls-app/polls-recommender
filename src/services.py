import numpy as np
from uuid import UUID
from hashlib import md5

from fastapi import Depends

from schemas import VectorizePollSchema, RecommendationDTO
from repositories import PollRepository
from dependencies import get_text2vec_model
from core.recsys_config import LANG_CODES, CATEGORIES, WEIGHTS


class RecommendationService:
    def __init__(self, poll_repo: PollRepository = Depends()):
        self.poll_repo = poll_repo

    async def get_personalized_recommendations(self, user_id: UUID) -> list[RecommendationDTO]:
        passed_polls = await self.poll_repo.get_polls_passed_by_user(user_id)
        embeddings, excluded_polls = [], []

        for poll in passed_polls:
            embeddings.append(poll.embedding)
            excluded_polls.append(poll.id)

        user_vector = np.mean(embeddings, axis=0).tolist()
        return await self.poll_repo.get_similar_polls(user_vector, excluded_polls)


class PollVectorizer:
    def __init__(self):
        self.model = get_text2vec_model()
        self.lang_vocab = LANG_CODES
        self.cat_vocab = CATEGORIES
        self.weights = np.array(WEIGHTS, dtype=np.float32)

    @staticmethod
    def one_hot(values: list[str], vocabulary: list[str]) -> np.ndarray:
        """Converts a list of values to a one-hot encoded vector based on the given vocabulary."""
        vocab_index = {v: i for i, v in enumerate(vocabulary)}
        result = np.zeros(len(vocabulary), dtype=np.float32)
        for val in values:
            idx = vocab_index.get(val)
            if idx is not None:
                result[idx] = 1.0
        return result

    @staticmethod
    def hash_feature(value: str, num_bins: int) -> int:
        """Hashes a string value into a fixed number of bins using MD5."""
        h = md5(value.encode('utf-8')).hexdigest()
        return int(h, 16) % num_bins

    def feature_hashing(self, tags: list[str], num_bins: int = 128) -> np.ndarray:
        """Applies feature hashing to a list of tags."""
        vector = np.zeros(num_bins, dtype=np.float32)
        for tag in tags:
            idx = self.hash_feature(tag, num_bins)
            vector[idx] += 1.0
        return vector

    def vectorize_poll(self, poll_data: VectorizePollSchema) -> list[float]:
        """Vectorizes poll data into a single weighted feature vector."""
        if poll_data.category not in CATEGORIES or poll_data.lang_code not in LANG_CODES:
            raise ValueError("Invalid category or language code")
        
        vectors = [
            np.array(self.model.encode(poll_data.title), dtype=np.float32),
            np.array(self.model.encode(poll_data.description), dtype=np.float32),
            self.one_hot([poll_data.lang_code], self.lang_vocab),
            self.one_hot([poll_data.category], self.cat_vocab),
            self.feature_hashing(poll_data.tags, num_bins=16)
        ]

        weighted_vectors = [vec * w for vec, w in zip(vectors, self.weights)]
        combined_vector = np.concatenate(weighted_vectors)

        return combined_vector.tolist()
