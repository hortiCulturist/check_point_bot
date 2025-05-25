from bot_app.db.common.tasks import TaskTable
from bot_app.db.main import create_con
from bot_app.utils.logger import log_chat_event


async def deactivate_expired_tasks():
    print("CRON запущен")
    try:
        rows = await TaskTable.deactivate_expired_tasks()

        for row in rows:
            chat_id = row["chat_id"]
            title = row["title"]
            task_id = row["id"]
            log_chat_event(chat_id, "Bot", f"⏰ Задание ID {task_id} ({title}) было автоматически отключено")

    except Exception as e:
        log_chat_event(0, "System", f"❌ Ошибка в cron-задаче: {e}")
