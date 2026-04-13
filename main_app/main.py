from fastapi import FastAPI
from .database import Base, engine
from .user.router import router as user_router

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(user_router, prefix="/user", tags=["user"])


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "head to https://localhost:8000/docs for the swagger ui"}
