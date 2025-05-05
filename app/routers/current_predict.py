from fastapi import APIRouter
from sqlalchemy import extract
from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session
from app.alchemy.db_depends import get_db
from app.models.current_predict import CurrentPredict
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/current_predict", tags=["current_predict"])

@router.get("/")
async def get_current_predict(db: Annotated[AsyncSession, Depends(get_db)]):    
    # Get all predictions for given year and month
    predictions = await db.execute(select(CurrentPredict))
    predictions = predictions.scalars().all()

    return predictions

@router.get("/{stack_id}")
async def get_current_predict_by_stack_id(stack_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    predictions = await db.execute(select(CurrentPredict).filter(
        CurrentPredict.stack_id == stack_id
    ))
    predictions = predictions.scalars().all()
    return predictions
