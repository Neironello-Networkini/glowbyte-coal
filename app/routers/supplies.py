from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from decimal import Decimal

from app.alchemy.db_depends import get_db
from app.models.supplies import Supplies, SuppliesOut
from app.models.brand import Brand
from app.models.stack import Stack
from app.models.warehouse import Warehouse
from app.schemas.supplies import CreateSupplies, UpdateSupplies
import pandas as pd
from io import BytesIO

router = APIRouter(prefix="/supplies", tags=["supplies"])

def sanitize_supplies(supplies_list):
    for s in supplies_list:
        if isinstance(s.ship_weight, Decimal) and (s.ship_weight.is_nan() or s.ship_weight.is_infinite()):
            s.ship_weight = None
        if isinstance(s.warehouse_weight, Decimal) and (s.warehouse_weight.is_nan() or s.warehouse_weight.is_infinite()):
            s.warehouse_weight = None
    return supplies_list

@router.post("/")
async def create_supplies(db: Annotated[AsyncSession, Depends(get_db)], create_supplies: CreateSupplies):
    await db.execute(insert(Supplies).values(**create_supplies.dict()))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.get("/", response_model=list[SuppliesOut])
async def get_all_supplies(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Supplies).limit(1000))
    supplies = result.scalars().all()
    return sanitize_supplies(supplies)

@router.get("/{supplies_id}")
async def get_supplies_by_id(supplies_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Supplies).where(Supplies.id == supplies_id))
    supplies = result.scalars().first()
    return supplies

@router.put("/update/{supplies_id}")
async def update_supplies(supplies_id: int, db: Annotated[AsyncSession, Depends(get_db)], update_supplies: UpdateSupplies):
    await db.execute(update(Supplies).where(Supplies.id == supplies_id).values(**{k: v for k, v in update_supplies.dict().items() if v is not None}))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Successful'
    }

@router.delete("/delete/{supplies_id}")
async def delete_supplies(supplies_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    await db.execute(delete(Supplies).where(Supplies.id == supplies_id))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Successful'
    }

@router.post("/upload-csv")
async def upload_csv(
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...)
):
    try:
        # 1) Прочитать CSV в pandas
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка разбора CSV: {e}")
    
    # 2) Переименовать колонки под удобные имена
    df = df.rename(columns={
        'ВыгрузкаНаСклад': 'warehouse_date',
        'Наим. ЕТСНГ':     'brand_name', # нужен id марки
        'Штабель':         'stack_number', # нужен id штабеля
        'ПогрузкаНаСудно': 'ship_date',
        'На склад, тн':    'warehouse_weight',
        'На судно, тн':    'ship_weight',
        'Склад':           'warehouse_name'
    })

    # 3) Проверить, что все колонки присутствуют
    required_columns = ['warehouse_date', 'warehouse_name', 'stack_number', 'brand_name', 'warehouse_weight', 'ship_date', 'ship_weight']
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Отсутствуют обязательные колонки: {missing_columns}")

    # 3) Преобразовать даты и числовые поля
    df['warehouse_date'] = pd.to_datetime(df['warehouse_date'], format='%Y-%m-%d', ).dt.date
    df['ship_date'] = pd.to_datetime(df['ship_date'], format='%Y-%m-%d', ).dt.date

    df['warehouse_weight'] = df['warehouse_weight'].astype(float).apply(Decimal)
    df['ship_weight']      = df['ship_weight'].astype(float).apply(Decimal)


    # 4) Для каждой строки находим brand_id и stack_id и создаём объект Supplies
    supplies_to_add = []
    for row in df.itertuples(index=False):
        q_brand = await db.execute(
            select(Brand.id).where(Brand.name == str(row.brand_name))
        )
        brand_id = q_brand.scalar_one_or_none()
        if brand_id is None:
            raise HTTPException(
                status_code=400,
                detail=f"Не найдена марка '{row.brand_name}'"
            )

        # Найдём штабель по имени
        stmt = (
            select(Stack.id)
            .join(Stack.warehouse)  # JOIN warehouse ON stack.warehouse_id = warehouse.id
            .where(
                Stack.name == str(row.stack_number),
                Warehouse.name == str(row.warehouse_name)
            )
        )
        q_stack = await db.execute(stmt)

        stack_id = q_stack.scalar_one_or_none()
        if stack_id is None:
            raise HTTPException(
                status_code=400,
                detail=f"Не найден штабель '{row.stack_number, row.warehouse_name}'"
            )

        supplies = Supplies(
            brand_id=brand_id,
            stack_id=stack_id,
            warehouse_date=row.warehouse_date,
            warehouse_weight=row.warehouse_weight,
            ship_date=row.ship_date,
            ship_weight=row.ship_weight,
        )
        supplies_to_add.append(supplies)

    # 5) Сохраняем все записи пачкой
    db.add_all(supplies_to_add)
    await db.commit()

    return {"status": "ok", "inserted": len(supplies_to_add)}


        


