from typing import Optional
from bot_app.db.main import create_con


class ChatsTable:
    @staticmethod
    async def is_active(chat_id: int) -> bool:
        con = await create_con()
        try:
            query = "SELECT is_active FROM chats WHERE chat_id = $1;"
            result = await con.fetchval(query, chat_id)
            return result is True
        finally:
            await con.close()

    @staticmethod
    async def add_chat(chat_id: int, title: str, added_by: int):
        con = await create_con()
        try:
            query = """
            INSERT INTO chats (chat_id, title, added_by, is_active)
            VALUES ($1, $2, $3, FALSE)
            ON CONFLICT (chat_id) DO NOTHING;
            """
            await con.execute(query, chat_id, title, added_by)
        finally:
            await con.close()

    @staticmethod
    async def activate_chat(chat_id: int):
        con = await create_con()
        try:
            query = "UPDATE chats SET is_active = TRUE WHERE chat_id = $1;"
            await con.execute(query, chat_id)
        finally:
            await con.close()

    @staticmethod
    async def deactivate_chat(chat_id: int):
        con = await create_con()
        try:
            query = "UPDATE chats SET is_active = FALSE WHERE chat_id = $1;"
            await con.execute(query, chat_id)
        finally:
            await con.close()
