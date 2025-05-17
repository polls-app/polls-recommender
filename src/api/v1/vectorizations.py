from fastapi import APIRouter, Depends, HTTPException, status

from schemas.vectorizations import VectorizePollSchema, VectorizePollResponse
from services.vectorizer import PollVectorizer


vectorizations_router = APIRouter(
    prefix="/api/v1/vectorizations", tags=["vectorization"]
)

@vectorizations_router.post(
    "/poll",
    summary="Vectorize a poll",
    description="Takes structured poll data and returns a vector representation.",
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
