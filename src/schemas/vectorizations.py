from pydantic import BaseModel


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
