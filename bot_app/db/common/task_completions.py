from bot_app.db.main import create_con
from bot_app.utils.logger import log_chat_event


class TaskCompletionTable:
    @staticmethod
    async def mark_completed(user_id: int, chat_id: int, task_id: int):
        con = await create_con()
        try:
            query = """
                INSERT INTO task_completions (user_id, chat_id, task_id)
                VALUES ($1, $2, $3)
                ON CONFLICT DO NOTHING;
            """
            await con.execute(query, user_id, chat_id, task_id)
            log_chat_event(chat_id, "DB", f"✅ Пользователь {user_id} завершил задание {task_id}")
        except Exception as e:
            log_chat_event(chat_id, "DB", f"❌ Ошибка при сохранении выполнения задания: {e}")
        finally:
            await con.close()

    @staticmethod
    async def has_completed(user_id: int, task_id: int):
        con = await create_con()
        try:
            query = """
                SELECT 1 FROM task_completions
                WHERE user_id = $1 AND task_id = $2
                LIMIT 1;
            """
            result = await con.fetchrow(query, user_id, task_id)
            return result is not None
        finally:
            await con.close()

    @staticmethod
    async def has_completed_all(user_id: int, chat_id: int):
        con = await create_con()
        try:
            query = """
                SELECT id FROM tasks
                WHERE chat_id = $1 AND is_active = true
            """
            task_ids = await con.fetch(query, chat_id)
            if not task_ids:
                return True

            required_ids = {row['id'] for row in task_ids}

            query = """
                SELECT task_id FROM task_completions
                WHERE user_id = $1 AND chat_id = $2
            """
            completed = await con.fetch(query, user_id, chat_id)
            completed_ids = {row['task_id'] for row in completed}

            return required_ids.issubset(completed_ids)
        finally:
            await con.close()

    @staticmethod
    async def get_completed_task_ids(user_id: int, chat_id: int) -> set[int]:
        con = await create_con()
        try:
            rows = await con.fetch(
                "SELECT task_id FROM task_completions WHERE user_id = $1 AND chat_id = $2",
                user_id, chat_id
            )
            return {row['task_id'] for row in rows}
        finally:
            await con.close()
