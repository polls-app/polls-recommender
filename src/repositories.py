from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.database import get_db
from models import Poll, Option, Vote, User
from schemas import PollToComputeUserVector, RecommendationDTO, OptionInRecommendationDTO


class PollRepository():
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_polls_passed_by_user(self, user_id: UUID) -> list[PollToComputeUserVector]:
        subquery = (
            select(Option.poll_id)
            .join(Vote, Vote.option_id == Option.id)
            .where(Vote.user_id == user_id)
            .group_by(Option.poll_id)
        )
        
        query = select(Poll).where(Poll.id.in_(subquery))

        result = await self.db.execute(query)
        
        return PollRepository._models_to_dtos(result.scalars().all(), PollToComputeUserVector)

    
    async def get_similar_polls(self, user_vector: list[float], polls_to_exclude: list[UUID]) -> list[RecommendationDTO]:
        similar_polls = (
            select(Poll)
            .options(
                selectinload(Poll.options),
                selectinload(Poll.user).selectinload(User.profile),
                selectinload(Poll.shares)
            )
            .filter(~Poll.id.in_(polls_to_exclude))
            .order_by(Poll.embedding.cosine_distance(user_vector))
            .limit(5)
        )
        
        result = await self.db.execute(similar_polls)
        polls = result.scalars().all()
        
        return [RecommendationDTO(
            id=poll.id,
            title=poll.title,
            options=[OptionInRecommendationDTO(
                id=option.id,
                content=option.content,
                position=option.position,
                is_correct=option.is_correct
            ) for option in poll.options],
            number_of_shares=len(poll.shares),
            created_at=poll.created_at,
            author_avatar=poll.user.profile.avatar_path,
            author_full_name=f"{poll.user.profile.first_name} {poll.user.profile.last_name}"
        ) for poll in polls]

       
    @staticmethod
    def _models_to_dtos(models, dto_class):
        return [dto_class.model_validate(item) for item in models]
    