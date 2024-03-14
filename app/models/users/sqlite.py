import aiosqlite
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.dependencies import admin_config as ADMIN_USER

DATABASE_URL = "sqlite+aiosqlite:///app/models/users/users.db"
DATABASE_URL_SQLITE = "app/models/users/users.db"
Base = declarative_base()


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with aiosqlite.connect(DATABASE_URL_SQLITE) as conn:
        values = (
            ADMIN_USER["UUID"],
            ADMIN_USER["email"],
            ADMIN_USER["hashed_pw"],
            ADMIN_USER["is_active"],
            ADMIN_USER["is_superuser"],
            ADMIN_USER["is_verified"],
        )
        await conn.execute(
            "INSERT OR IGNORE INTO main.user (id, email, hashed_password, is_active, is_superuser, "
            "is_verified) VALUES(?, ?, ?, ?, ?, ?)",
            values,
        )
        await conn.commit()


async def get_async_session_maker():
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session_maker)):
    yield SQLAlchemyUserDatabase(session, User)
