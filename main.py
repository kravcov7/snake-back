from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import async_engine
from routers import auth

app = FastAPI()

AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.on_event("startup")
async def startup():
    await create_tables()


@app.on_event("shutdown")
async def shutdown():
    await async_engine.dispose()


app.include_router(auth.router)
