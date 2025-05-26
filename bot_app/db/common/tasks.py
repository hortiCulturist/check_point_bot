from datetime import datetime

from bot_app.db.main import create_con
from bot_app.misc import redis
from bot_app.utils.base import invalidate_task_cache
from bot_app.utils.logger import log_chat_event


class TaskTable:
    @staticmethod
    async def add_task(chat_id: int, title: str, task_type: str, url: str, button_text: str, expires_at=None):
        con = await create_con()
        try:
            query = """
                INSERT INTO tasks (chat_id, title, type, target_url, button_text, expires_at)
                VALUES ($1, $2, $3, $4, $5, $6);
            """
            await con.execute(query, chat_id, title, task_type, url, button_text, expires_at)
            log_chat_event(chat_id, "DB", f"🆕 Задание добавлено: {title}")

            await invalidate_task_cache(chat_id)

        except Exception as e:
            log_chat_event(chat_id, "DB", f"❌ Ошибка при добавлении задания: {e}")
        finally:
            await con.close()

    @staticmethod
    async def get_active_tasks(chat_id: int) -> list[dict]:
        con = await create_con()
        try:
            query = """
                SELECT * FROM tasks
                WHERE chat_id = $1 AND is_active = TRUE
                AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY id
            """
            rows = await con.fetch(query, chat_id)
            return [dict(row) for row in rows]
        finally:
            await con.close()

    @staticmethod
    async def deactivate_task(task_id: int):
        con = await create_con()
        try:
            query = "UPDATE tasks SET is_active = FALSE WHERE id = $1;"
            await con.execute(query, task_id)
            log_chat_event(task_id, "DB", "⛔ Задание деактивировано")
        except Exception as e:
            log_chat_event(task_id, "DB", f"❌ Ошибка при деактивации задания: {e}")
        finally:
            await con.close()

    @staticmethod
    async def delete_task(task_id: int):
        con = await create_con()
        try:
            query = "DELETE FROM tasks WHERE id = $1 RETURNING chat_id;"
            result = await con.fetchrow(query, task_id)
            if result:
                chat_id = result["chat_id"]
                await invalidate_task_cache(chat_id)
                log_chat_event(chat_id, "DB", "🗑️ Задание удалено")
        except Exception as e:
            log_chat_event(task_id, "DB", f"❌ Ошибка при удалении задания: {e}")
        finally:
            await con.close()

    @staticmethod
    async def deactivate_expired_tasks():
        con = await create_con()
        try:
            query = """
                UPDATE tasks
                SET is_active = FALSE
                WHERE expires_at IS NOT NULL
                  AND expires_at < NOW()
                  AND is_active = TRUE
                RETURNING chat_id, id, title
            """
            rows = await con.fetch(query)

            unique_chat_ids = {row["chat_id"] for row in rows}
            for chat_id in unique_chat_ids:
                await invalidate_task_cache(chat_id)
                log_chat_event(chat_id, "Redis", f"♻️ Кеш очищен (auto-деактивация заданий)")

            return rows
        finally:
            await con.close()

    @staticmethod
    async def get_chats_with_tasks() -> list[dict]:
        con = await create_con()
        try:
            query = """
                SELECT DISTINCT c.chat_id, c.title
                FROM tasks t
                JOIN chats c ON t.chat_id = c.chat_id
                ORDER BY c.title
            """
            rows = await con.fetch(query)
            return [dict(r) for r in rows]
        finally:
            await con.close()

    @staticmethod
    async def get_tasks_by_chat(chat_id: int) -> list[dict]:
        con = await create_con()
        try:
            query = "SELECT * FROM tasks WHERE chat_id = $1 ORDER BY id DESC"
            rows = await con.fetch(query, chat_id)
            return [dict(row) for row in rows]
        finally:
            await con.close()

    @staticmethod
    async def get_task(task_id: int) -> dict | None:
        con = await create_con()
        try:
            row = await con.fetchrow("SELECT * FROM tasks WHERE id = $1", task_id)
            return dict(row) if row else None
        finally:
            await con.close()

    @staticmethod
    async def activate_task(task_id: int):
        con = await create_con()
        try:
            await con.execute("UPDATE tasks SET is_active = TRUE WHERE id = $1", task_id)
            log_chat_event(task_id, "DB", f"✅ Задание активировано")
        finally:
            await con.close()

    @staticmethod
    async def set_task_expiration(task_id: int, expires_at: datetime):
        con = await create_con()
        try:
            query = """
                UPDATE tasks
                SET expires_at = $1
                WHERE id = $2;
            """
            await con.execute(query, expires_at, task_id)
            log_chat_event(task_id, "DB", f"⏰ Установлен срок действия: {expires_at}")
        except Exception as e:
            log_chat_event(task_id, "DB", f"❌ Ошибка при обновлении expires_at: {e}")
        finally:
            await con.close()
