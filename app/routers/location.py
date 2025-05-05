from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import insert, delete, select
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.alchemy.db import engine
from app.alchemy.db_depends import get_db
from app.models.location import Location
from app.schemas.location import CreateLocation

router = APIRouter(prefix="/location", tags=["location"])

@router.post("/")
async def create_location(db: Annotated[AsyncSession, Depends(get_db)], create_location: CreateLocation):
    await db.execute(delete(Location))
    await db.execute(insert(Location).values(latitude=create_location.latitude, longitude=create_location.longitude))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.get("/")
async def get_location(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Location))
    location = result.scalars().first()
    return location
    