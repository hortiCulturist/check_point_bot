from typing import Callable, Dict, Awaitable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message

from bot_app.config import ADMIN_ID
from bot_app.db.common.chats import ChatsTable
from bot_app.db.common.task_completions import TaskCompletionTable
from bot_app.markups.user.base import get_start_button
from bot_app.misc import bot, redis
from bot_app.utils.logger import log_chat_event


class AccessControlMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict], Awaitable],
        message: Message,
        data: Dict
    ) -> Awaitable:

        if message.from_user.id in ADMIN_ID:
            return await handler(message, data)

        if message.chat.type != "supergroup":
            return await handler(message, data)

        user_id = message.from_user.id
        chat_id = message.chat.id

        if not await ChatsTable.is_active(chat_id):
            return await handler(message, data)

        cache_key = f"verified:{chat_id}:{user_id}"

        if await redis.get(cache_key):
            return await handler(message, data)

        completed = await TaskCompletionTable.has_completed_all(user_id, chat_id)

        if completed:
            await redis.set(cache_key, "1", ex=86400)  # Кеш на 24 часа
            return await handler(message, data)

        try:
            await bot.delete_message(chat_id, message.message_id)
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions={"can_send_messages": False}
            )

            await bot.send_message(
                chat_id=chat_id,
                text=f"👋 Чтобы писать в чате — откройте бота и выполните задание:",
                reply_markup=await get_start_button(chat_id)
            )

            log_chat_event(chat_id, "Bot", f"🔒 {user_id} ограничен до выполнения всех заданий")
        except Exception as e:
            log_chat_event(chat_id, "Bot", f"❌ Ошибка при auto-муте: {e}")
