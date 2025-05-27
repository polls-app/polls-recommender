from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VectorizePollSchema(BaseModel):
    title: str
    description: str
    lang_code: str
    category: str
    tags: list[str]


class VectorData(BaseModel):
    vector: list[float]


class VectorizePollResponse(BaseModel):
    status: str
    data: VectorData
    message: str


class PollToComputeUserVector(BaseModel):
    id: UUID
    embedding: list[float]

    model_config = ConfigDict(from_attributes=True)


class OptionInRecommendationDTO(BaseModel):
    id: UUID
    content: str
    position: int
    is_correct: bool | None


class RecommendationDTO(BaseModel):
    id: UUID
    title: str
    options: list[OptionInRecommendationDTO]
    number_of_shares: int
    created_at: datetime
    author_avatar: str
    author_full_name: str
