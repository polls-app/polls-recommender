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
    author_avatar: str | None
    author_full_name: str

    @classmethod
    def model_validate(cls, poll):
        """Custom validation to handle Poll model conversion"""
        full_name = ""
        avatar_path = ""
        
        if poll.user and poll.user.profile:
            profile = poll.user.profile
            full_name = profile.first_name
            if profile.last_name:
                full_name += f" {profile.last_name}"
            avatar_path = profile.avatar_path or None
        
        return cls(
            id=poll.id,
            title=poll.title,
            options=[
                OptionInRecommendationDTO(
                    id=option.id,
                    content=option.content,
                    position=option.position,
                    is_correct=option.is_correct
                ) for option in poll.options
            ],
            number_of_shares=poll.number_of_shares,
            created_at=poll.created_at,
            author_avatar=avatar_path,
            author_full_name=full_name
        )
