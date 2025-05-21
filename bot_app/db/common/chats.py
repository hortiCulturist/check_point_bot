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
    async def add_chat(chat_id: int, title: str, added_by: int, raw_type: str):
        con = await create_con()

        chat_type = "channel" if raw_type == "channel" else "group"

        try:
            query = """
            INSERT INTO chats (chat_id, title, added_by, type)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (chat_id) DO NOTHING;
            """
            await con.execute(query, chat_id, title, added_by, chat_type)
        finally:
            await con.close()

    @staticmethod
    async def activate_chat(chat_id: int):
        con = await create_con()
        try:
            query = "UPDATE chats SET is_active = TRUE, mode = 'moderation' WHERE chat_id = $1;"
            await con.execute(query, chat_id)
        finally:
            await con.close()

    @staticmethod
    async def deactivate_chat(chat_id: int):
        con = await create_con()
        try:
            query = "UPDATE chats SET is_active = FALSE, mode = 'disabled' WHERE chat_id = $1;"
            await con.execute(query, chat_id)
        finally:
            await con.close()
