import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

POSTGRES = {
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DB_NAME'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
}


async def create_con():
    """
    Создание обычного подключения к базе данных.
    """
    con = await asyncpg.connect(**POSTGRES)
    return con


async def create_dict_con():
    """
    Создание подключения для получения данных в виде словарей.
    """
    try:
        con = await asyncpg.connect(**POSTGRES)
        return con
    except Exception as e:
        print(f"Ошибка при подключении к PostgreSQL: {e}")
        return None
