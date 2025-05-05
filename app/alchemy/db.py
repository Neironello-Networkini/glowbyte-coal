from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase



engine = create_async_engine('postgresql+asyncpg://glowbyte_admin:mypass@localhost:5432/glowbyte_coal', echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass