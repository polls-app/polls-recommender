from fastapi import FastAPI, Depends
from sqlalchemy import select

from core.database import get_db
from models.poll import Poll


app = FastAPI()


@app.get("/all-polls")
async def get_all_polls(db =  Depends(get_db)):
    result = await db.execute(select(Poll))
    polls = result.scalars().all()
    return polls