from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from io import BytesIO
from fastapi import HTTPException, UploadFile, File
from decimal import Decimal
from app.alchemy.db_depends import get_db
from app.models.temperature import Temperature
from app.schemas.temperature import CreateTemperature, UpdateTemperature
from app.models.brand import Brand
from app.models.stack import Stack
from app.models.warehouse import Warehouse
import numpy as np

router = APIRouter(prefix="/temperature", tags=["temperature"])

@router.post("/")
async def create_temperature(db: Annotated[AsyncSession, Depends(get_db)], create_temperature: CreateTemperature):
    await db.execute(insert(Temperature).values(**create_temperature.dict()))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.get("/")
async def get_all_temperatures(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Temperature).limit(1000))
    temperatures = result.scalars().all()
    return temperatures

@router.get("/{temperature_id}")
async def get_temperature_by_id(temperature_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Temperature).where(Temperature.id == temperature_id))
    temperature = result.scalars().first()
    return temperature

@router.put("/update/{temperature_id}")
async def update_temperature(temperature_id: int, db: Annotated[AsyncSession, Depends(get_db)], update_temperature: UpdateTemperature):
    await db.execute(update(Temperature).where(Temperature.id == temperature_id).values(**{k: v for k, v in update_temperature.dict().items() if v is not None}))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Successful'
    }

@router.delete("/delete/{temperature_id}")
async def delete_temperature(temperature_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    await db.execute(delete(Temperature).where(Temperature.id == temperature_id))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Successful'
    } 

@router.post("/upload-csv")
async def upload_csv(db: Annotated[AsyncSession, Depends(get_db)], file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка разбора CSV: {e}")
    
    # 2) Переименовать колонки под удобные имена
    df = df.rename(columns={
        'Склад': 'warehouse_name',
        'Штабель': 'stack_number',
        'Марка': 'brand_name',
        'Максимальная температура': 'max_temperature',
        'Пикет': 'picket',
        'Дата акта': 'act_date',
        'Смена': 'shift',
    })

    # 3) Проверить, что все колонки присутствуют
    required_columns = ['warehouse_name', 'stack_number', 'brand_name', 'max_temperature', 'picket', 'act_date', 'shift']
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Отсутствуют обязательные колонки: {missing_columns}")
    
    # 4) Преобразование столбца к datetime и затем к date
    df['act_date'] = pd.to_datetime(df['act_date']).dt.date
    df['max_temperature'] = df['max_temperature'].astype(float).apply(Decimal)

    # 5) Заменить NaN на пустую строку во всех строковых столбцах
    df['picket'] = df['picket'].fillna('')

    # 6) Заменить NaN на None в числовых столбцах
    df['shift'] = df['shift'].apply(lambda x: int(x) if pd.notnull(x) else None)

    # 7) Для каждой строки находим brand_id и stack_id и создаём объект Temperature
    temperatures_to_add = []
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
        
        shift_value = int(row.shift) if pd.notna(row.shift) else None
        temperature = Temperature(
            brand_id=brand_id,
            stack_id=stack_id,
            max_temperature=row.max_temperature,
            picket=row.picket,
            act_date=row.act_date,
            shift=shift_value
        )
        temperatures_to_add.append(temperature)

    # 8) Сохраняем все записи пачкой
    db.add_all(temperatures_to_add)
    await db.commit()

    return {"status": "ok", "inserted": len(temperatures_to_add)}
