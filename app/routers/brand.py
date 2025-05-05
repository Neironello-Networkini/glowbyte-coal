from fastapi import APIRouter, Depends, status, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.alchemy.db import engine
from app.alchemy.db_depends import get_db
from app.models.brand import Brand
from app.schemas.brand import CreateBrand, UpdateBrand, DeleteBrand
import csv
from sqlalchemy.exc import IntegrityError  


router = APIRouter(prefix="/brand", tags=["brand"])

@router.post("/")
async def create_brand(db: Annotated[AsyncSession, Depends(get_db)], create_brand: CreateBrand):
    await db.execute(insert(Brand).values(name=create_brand.name))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get("/")
async def get_all_brands(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Brand))
    brands = result.scalars().all()
    return brands


@router.get("/{brand_id}")
async def get_brand_by_id(brand_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalars().first()
    return brand


@router.put("/update/{brand_id}")
async def update_brand(brand_id: int, db: Annotated[AsyncSession, Depends(get_db)], update_brand: UpdateBrand):
    await db.execute(update(Brand).where(Brand.id == brand_id).values(name=update_brand.name))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Successful' 
    }


@router.delete("/delete/{brand_id}")
async def delete_brand(brand_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    await db.execute(delete(Brand).where(Brand.id == brand_id))   
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Successful' 
    }

@router.post("/upload")
async def upload_brands(db: Annotated[AsyncSession, Depends(get_db)], file: UploadFile):
    try:
        content = await file.read()
        # Декодируем байты в строку
        text = content.decode('utf-8')
        # Читаем CSV
        reader = csv.DictReader(text.splitlines())
        brands_data = list(reader)
        
        
        for row in brands_data:
            try:
                brand_data = {
                    'name': row['brand']
                }
                await db.execute(insert(Brand).values(**brand_data))
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