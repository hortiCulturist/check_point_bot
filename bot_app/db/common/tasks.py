from bot_app.db.main import create_con
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
            query = "DELETE FROM tasks WHERE id = $1;"
            await con.execute(query, task_id)
            log_chat_event(task_id, "DB", "🗑️ Задание удалено")
        except Exception as e:
            log_chat_event(task_id, "DB", f"❌ Ошибка при удалении задания: {e}")
        finally:
            await con.close()