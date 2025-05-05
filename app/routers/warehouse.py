from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.alchemy.db_depends import get_db
from app.models.warehouse import Warehouse
from app.schemas.warehouse import CreateWarehouse, UpdateWarehouse

router = APIRouter(prefix="/warehouse", tags=["warehouse"])

@router.post("/")
async def create_warehouse(db: Annotated[AsyncSession, Depends(get_db)], create_warehouse: CreateWarehouse):
    await db.execute(insert(Warehouse).values(**create_warehouse.dict()))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.get("/")
async def get_all_warehouses(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Warehouse))
    warehouses = result.scalars().all()
    return warehouses

@router.get("/{warehouse_id}")
async def get_warehouse_by_id(warehouse_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id))
    warehouse = result.scalars().first()
    return warehouse

@router.put("/update/{warehouse_id}")
async def update_warehouse(warehouse_id: int, db: Annotated[AsyncSession, Depends(get_db)], update_warehouse: UpdateWarehouse):
    await db.execute(update(Warehouse).where(Warehouse.id == warehouse_id).values(**{k: v for k, v in update_warehouse.dict().items() if v is not None}))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Successful'
    }

@router.delete("/delete/{warehouse_id}")
async def delete_warehouse(warehouse_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    await db.execute(delete(Warehouse).where(Warehouse.id == warehouse_id))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Successful'
    }
