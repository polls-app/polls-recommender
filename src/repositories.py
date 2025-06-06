from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
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
    
    async def get_polls_by_votes_paginated(
        self, 
        cursor: str | None, 
        limit: int = 5
    ) -> dict:
        """
        Get polls sorted by vote count with keyset pagination.
        Returns DTOs and pagination info
        """
        polls_data = await self._get_polls_by_votes_raw(cursor=cursor, limit=limit + 1)
        
        # Check if there are more results
        has_next = len(polls_data) > limit
        if has_next:
            polls_data = polls_data[:limit]
        
        # Convert to DTOs
        recommendations = self._models_to_dtos(polls_data, RecommendationDTO)
        
        # Generate next cursor if there are more results
        next_cursor = None
        if has_next and polls_data:
            last_poll = polls_data[-1]
            next_cursor = f"{last_poll.vote_count}_{last_poll.id}"
        
        return {
            "polls": recommendations,
            "next_cursor": next_cursor,
            "has_next": has_next
        }
    
    async def _get_polls_by_votes_raw(
        self, 
        cursor: str | None, 
        limit: int = 5
    ) -> list[Poll]:
        """
        Get polls sorted by vote count with keyset pagination
        """

        query = (
            select(Poll, func.count(func.distinct(Vote.user_id)).label('vote_count'))
            .join(Option, Poll.id == Option.poll_id)
            .outerjoin(Vote, Option.id == Vote.option_id)
            .group_by(Poll.id)
            .options(
                selectinload(Poll.options),
                selectinload(Poll.user).selectinload(User.profile),
                selectinload(Poll.shares)
            )
        )
        
        # Apply cursor-based pagination
        if cursor:
            try:
                cursor_vote_count, cursor_poll_id = cursor.split('_', 1)
                cursor_vote_count = int(cursor_vote_count)
                
                query = query.having(
                    or_(
                        func.count(func.distinct(Vote.user_id)) < cursor_vote_count,
                        and_(
                            func.count(func.distinct(Vote.user_id)) == cursor_vote_count,
                            Poll.id > cursor_poll_id
                        )
                    )
                )
            except (ValueError, AttributeError):
                raise ValueError("Invalid cursor format.")
        
        query = query.order_by(
            desc(func.count(func.distinct(Vote.user_id))),
            Poll.id
        )
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        polls_with_votes = []
        for row in rows:
            poll = row[0]
            vote_count = row[1]
            
            poll.vote_count = vote_count
            poll.number_of_shares = len(poll.shares) if poll.shares else 0
            polls_with_votes.append(poll)
        
        return polls_with_votes

       
    @staticmethod
    def _models_to_dtos(models, dto_class):
        return [dto_class.model_validate(item) for item in models]
    