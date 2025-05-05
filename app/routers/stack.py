from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.alchemy.db_depends import get_db
from app.models.stack import Stack
from app.schemas.stack import CreateStack, UpdateStack
from typing import Annotated
import csv
from sqlalchemy.exc import IntegrityError
from app.models.warehouse import Warehouse
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/stack", tags=["stack"])

@router.post("/")
async def create_stack(db: Annotated[AsyncSession, Depends(get_db)], create_stack: CreateStack):
    warehouse = await db.execute(select(Warehouse.id).where(Warehouse.name == create_stack.warehouse))
    warehouse_id = warehouse.scalar_one_or_none()
    if not warehouse_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Склад не найден"
        )
    await db.execute(insert(Stack).values(
        name=create_stack.name,
        warehouse_id=warehouse_id
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.get("/")
async def get_all_stacks(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Stack).options(selectinload(Stack.warehouse)))
    stacks = result.scalars().all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "warehouse_id": s.warehouse_id,
            "warehouse_name": s.warehouse.name if s.warehouse else None
        }
        for s in stacks
    ]

@router.get("/{stack_id}")
async def get_stack_by_id(stack_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(Stack)
        .options(selectinload(Stack.warehouse))
        .where(Stack.id == stack_id)
    )
    stack = result.scalars().first()
    if not stack:
        return None
    return {
        "id": stack.id,
        "name": stack.name,
        "warehouse_id": stack.warehouse_id,
        "warehouse_name": stack.warehouse.name if stack.warehouse else None
    }


@router.put("/{stack_id}")
async def update_stack(stack_id: int, db: Annotated[AsyncSession, Depends(get_db)], update_stack: UpdateStack):
    stack = await db.execute(select(Stack).where(Stack.id == stack_id))
    await db.execute(update(Stack).where(Stack.id == stack_id).values(**update_stack.dict()))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Successful'
    }

@router.delete("/{stack_id}")
async def delete_stack(stack_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    await db.execute(delete(Stack).where(Stack.id == stack_id))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Successful'
    }

@router.post("/upload")
async def upload_stacks(db: Annotated[AsyncSession, Depends(get_db)], file: UploadFile):
    try:
        content = await file.read()
        # Декодируем байты в строку
        text = content.decode('utf-8')
        # Читаем CSV
        reader = csv.DictReader(text.splitlines())
        stacks_data = list(reader)
        
        # Получаем маппинг складов
        warehouses_result = await db.execute(select(Warehouse))
        warehouses = {w.name: w.id for w in warehouses_result.scalars().all()}
        
        for row in stacks_data:
            warehouse_id = warehouses.get(str(row['warehouse_name']))
            if not warehouse_id:
                continue
            try:
                stack_data = {
                    'name': row['stack'],
                    'warehouse_id': warehouse_id
                }
                await db.execute(insert(Stack).values(**stack_data))
                await db.commit()
            except IntegrityError:
                await db.rollback()
                continue
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

