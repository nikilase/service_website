from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base


DATABASE_URL = "sqlite+aiosqlite:///./users.db"

Base = declarative_base()
"""Geiles Tutorial, vielen Dank dafür.
Nur leider funktioniert bei mir der sessionmaker um 11:53 nicht so ganz bzw. Pycharm meckert, dass die class_ einen falschen Typen besitzt. 
Es scheint als müsse man anstatt den sessionmaker aus sqlalchemy.orm lieber den async_sessionmaker aus sqlalchemy.ext.asyncio benutzen, dann gibts keine Warnung.
Ist so auch in dem example drin https://github.com/fastapi-users/fastapi-users/blob/master/examples/sqlalchemy/app/db.py

Gibts nen Grund, wieso du den sessionmanager aus sqlalchemy.orm benutzt hast?

Das ist natürlich meckern auf hohen Niveau, weil ansonsten hast du das hier echt super erklärt :D"""
class User(SQLAlchemyBaseUserTableUUID, Base):
	pass

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_db_and_tables():
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

async def get_async_session_maker():
	async with async_session_maker() as session:
		yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session_maker)):
	yield SQLAlchemyUserDatabase(session, User)
