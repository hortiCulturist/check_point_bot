from bot_app.misc import redis
from bot_app.utils.logger import log_chat_event


async def invalidate_task_cache(chat_id: int):
    try:
        keys = await redis.keys(f"completed:{chat_id}:*")
        if keys:
            await redis.delete(*keys)
            log_chat_event(chat_id, "Redis", f"🧹 Кеш очищен для {len(keys)} пользователей")
        else:
            log_chat_event(chat_id, "Redis", f"ℹ️ Кеша не было для удаления")
    except Exception as e:
        log_chat_event(chat_id, "Redis", f"❌ Ошибка при удалении кеша: {e}")
