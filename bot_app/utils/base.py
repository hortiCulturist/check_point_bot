from bot_app.misc import redis
from bot_app.utils.logger import log_chat_event


async def invalidate_task_cache(chat_id: int):
    try:
        completed_keys = await redis.keys(f"completed:{chat_id}:*")
        verified_keys = await redis.keys(f"verified:{chat_id}:*")

        total_deleted = 0

        if completed_keys:
            await redis.delete(*completed_keys)
            total_deleted += len(completed_keys)
            log_chat_event(chat_id, "Redis", f"🧹 Удалено completed-кешей: {len(completed_keys)}")

        if verified_keys:
            await redis.delete(*verified_keys)
            total_deleted += len(verified_keys)
            log_chat_event(chat_id, "Redis", f"🧹 Удалено verified-кешей: {len(verified_keys)}")

        if total_deleted == 0:
            log_chat_event(chat_id, "Redis", f"ℹ️ Не найдено кешей для удаления")
    except Exception as e:
        log_chat_event(chat_id, "Redis", f"❌ Ошибка при удалении кеша: {e}")
