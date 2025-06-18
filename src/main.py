from typing import Literal
from contextlib import asynccontextmanager

from jose import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

from dependencies import get_text2vec_model
from repositories import PollRepository
from services import PollVectorizer, RecommendationService
from schemas import VectorizePollResponse, VectorizePollSchema, RecommendationDTO
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_text2vec_model()
    yield


app = FastAPI(title="Poll Recommender Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, settings.microservice_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


@app.post(
    "/api/v1/vectorizations/poll",
    summary="Vectorize a poll",
    description="Takes structured poll data and returns a vector representation.",
    tags=["vectorizations"],
    responses={
        200: {
            "description": "Vector retrieved successfully", "model": VectorizePollResponse
        },
        422: {
            "description": "Invalid poll data provided"
        },
    }
)
def vectorize_poll(
    poll_data: VectorizePollSchema,
    vectorizer: PollVectorizer = Depends()
    ):
    try:
        vector = vectorizer.vectorize_poll(poll_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    return {
        "status": "success",
        "data": {
            "vector": vector
        },
        "message": "Vector retrieved successfully"
        }


@app.get(
    "/api/v1/polls/completed",
    summary="Get polls passed by the user",
    tags=["polls"]
)
async def get_passed_polls_by_user_id(
    poll_repository: PollRepository = Depends(),
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for this endpoint",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    user_id = jwt.get_unverified_claims(token).get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: 'sub' claim is missing",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return await poll_repository.get_passed_polls_by_user_id(user_id)


@app.get(
        "/api/v1/polls",
        summary="Recommend polls",
        description="Returns personalized poll recommendations based on vote count, comments, and user preferences",
        tags=["recommendations"],
        responses={
            200: {"description": "Recommendations retrieved successfully", "model": RecommendationDTO},
            401: {"description": "Unauthorized"}
        }
)
async def recommend_polls(sort: Literal["best", "hot", "controversial"],
                          cursor: str | None = None,
                          limit: int = 5,
                          recommendation_service: RecommendationService = Depends(),
                          credentials: HTTPAuthorizationCredentials | None = Depends(security)
                          ):
     
    
    if sort == "best":
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for personalized recommendations",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token = credentials.credentials
        user_id = jwt.get_unverified_claims(token).get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: 'sub' claim is missing",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return await recommendation_service.get_personalized_recommendations(user_id)
    elif sort in ["hot", "controversial"]:
        try:
            result = await recommendation_service.get_sorted_polls(
                by=sort,
                cursor=cursor,
                limit=limit
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        return {
            "data": result["polls"],
            "pagination": {
                "next_cursor": result["next_cursor"],
                "has_next": result["has_next"],
                "limit": limit
            }
        }

    return {"message": "Temporarily not implemented"}
