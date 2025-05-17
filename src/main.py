from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1.vectorizations import vectorizations_router
from dependencies.vectorizer import get_text2vec_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_text2vec_model()
    yield
    
app = FastAPI(title="Poll Recommender Service", lifespan=lifespan)

app.include_router(vectorizations_router)

