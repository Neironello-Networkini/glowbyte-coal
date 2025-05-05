from fastapi import APIRouter
from sqlalchemy import extract
from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session
from app.alchemy.db_depends import get_db
from app.models.predict import Predict
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, File, UploadFile
import pandas as pd
from io import BytesIO
from decimal import Decimal
from app.models.predict import Predict
from app.models.brand import Brand
from app.models.stack import Stack
from app.models.warehouse import Warehouse

router = APIRouter(prefix="/predict", tags=["predict"])

@router.get("/{year}/{month}")
async def get_predict(year: int, month: int, db: Annotated[AsyncSession, Depends(get_db)]):    
    # Get all predictions for given year and month
    predictions = await db.execute(
        select(
            Predict,
            Stack.name.label('stack_name'),
            Warehouse.name.label('warehouse_name'),
            Brand.name.label('brand_name')
        )
        .join(Stack, Predict.stack_id == Stack.id)
        .join(Warehouse, Stack.warehouse_id == Warehouse.id)
        .join(Brand, Predict.brand_id == Brand.id)
        .filter(
            extract('year', Predict.date) == year,
            extract('month', Predict.date) == month
        )
    )
    
    # Convert results to list of dictionaries with all needed fields
    results = []
    for predict, stack_name, warehouse_name, brand_name in predictions:
        result = {
            "id": predict.id,
            "date": predict.date,
            "weight": predict.weight,
            "stack_id": predict.stack_id,
            "stack_name": stack_name,
            "warehouse_name": warehouse_name,
            "brand_name": brand_name
        }
        results.append(result)
    
    return results


@router.get("/stack/{stack_id}/{year}/{month}")
async def get_predict_by_stack_and_month(
    stack_id: int, 
    year: int, 
    month: int, 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Get predictions for specific stack in given year and month
    predictions = await db.execute(
        select(
            Predict,
            Stack.name.label('stack_name'),
            Warehouse.name.label('warehouse_name'),
            Brand.name.label('brand_name')
        )
        .join(Stack, Predict.stack_id == Stack.id)
        .join(Warehouse, Stack.warehouse_id == Warehouse.id)
        .join(Brand, Predict.brand_id == Brand.id)
        .filter(
            Predict.stack_id == stack_id,
            extract('year', Predict.date) == year,
            extract('month', Predict.date) == month
        )
    )

    # Convert results to list of dictionaries
    results = []
    for predict, stack_name, warehouse_name, brand_name in predictions:
        result = {
            "id": predict.id,
            "date": predict.date,
            "weight": predict.weight,
            "stack_id": predict.stack_id,
            "stack_name": stack_name,
            "warehouse_name": warehouse_name,
            "brand_name": brand_name
        }
        results.append(result)

    return results


@router.get("/{year}/{month}/{day}")
async def get_predict_by_date(year: int, month: int, day: int, db: Annotated[AsyncSession, Depends(get_db)]):    
    # Get all predictions for given year, month and day with related stack, warehouse and brand info
    predictions = await db.execute(
        select(
            Predict,
            Stack.name.label('stack_name'),
            Warehouse.name.label('warehouse_name'),
            Brand.name.label('brand_name')
        )
        .join(Stack, Predict.stack_id == Stack.id)
        .join(Warehouse, Stack.warehouse_id == Warehouse.id)
        .join(Brand, Predict.brand_id == Brand.id)
        .filter(
            extract('year', Predict.date) == year,
            extract('month', Predict.date) == month,
            extract('day', Predict.date) == day
        )
    )
    
    # Convert results to list of dictionaries with all needed fields
    results = []
    for predict, stack_name, warehouse_name, brand_name in predictions:
        result = {
            "id": predict.id,
            "date": predict.date,
            "weight": predict.weight,
            "stack_id": predict.stack_id,
            "stack_name": stack_name,
            "warehouse_name": warehouse_name,
            "brand_name": brand_name
        }
        results.append(result)
    
    return results


@router.get("/{stack_id}")
async def get_predict_by_stack_id(stack_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    predictions = await db.execute(select(Predict).filter(
        Predict.stack_id == stack_id
    ))
    predictions = predictions.scalars().all()
    return predictions

@router.post("/upload-csv")
async def upload_csv(db : Annotated[AsyncSession, Depends(get_db)], file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка разбора CSV: {e}")
    
    # 2) Переименовать колонки под удобные имена
    df = df.rename(columns={
        'Дата начала':     'date',
        'Груз':            'brand_name', # нужен id марки
        'Вес по акту, тн':  'weight', 
        'Склад':            'warehouse_name',
        'Штабель':          'stack_number' # нужен id штабеля
    })

    # 3) Проверить наличие всех необходимых колонок
    required_columns = ['date', 'brand_name', 'weight', 'warehouse_name', 'stack_number']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Отсутствуют необходимые колонки: {missing_columns}")  
    
    # 4) Преобразовать даты и числовые поля
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['weight'] = df['weight'].astype(float).apply(Decimal)

    # 5) Для каждой строки находим brand_id и stack_id и создаём объект Predict
    predicts_to_add = []
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
        predict = Predict(
            date=row.date,
            brand_id=brand_id,
            stack_id=stack_id,
            weight=row.weight
        )
        predicts_to_add.append(predict)
    
    # 6) Сохраняем все записи пачкой
    db.add_all(predicts_to_add)
    await db.commit()

    return {"status": "ok", "inserted": len(predicts_to_add)}
