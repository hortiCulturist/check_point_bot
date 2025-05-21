# bot_app/middlewares/access_control.py

from aiogram.types import Message
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Callable, Dict, Awaitable
from bot_app.misc import bot, redis
from bot_app.utils.logger import log_chat_event
from bot_app.db.common.chats import ChatsTable


class AccessControlMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict], Awaitable],
        message: Message,
        data: Dict
    ) -> Awaitable:

        if message.chat.type != "supergroup":
            return await handler(message, data)

        user_id = message.from_user.id
        chat_id = message.chat.id

        key = f"verified:{chat_id}:{user_id}"

        # Кэш проверен? Просто пропускаем
        if await redis.get(key):
            return await handler(message, data)

        # Проверим, активна ли группа
        if not await ChatsTable.is_active(chat_id):
            return await handler(message, data)

        # Проверка в БД (напр. user прошёл задание)
        if await ChatsTable.is_user_verified(chat_id, user_id):
            await redis.set(key, "1", ex=86400)  # 1 день
            return await handler(message, data)

        # Не прошёл — мутим и шлём в бота
        try:
            await bot.delete_message(chat_id, message.message_id)
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions={"can_send_messages": False}
            )
            # optionally send inline-кнопку
            log_chat_event(chat_id, "Bot", f"🔒 {user_id} ограничен до выполнения задания")
        except Exception as e:
            log_chat_event(chat_id, "Bot", f"❌ Ошибка при auto-муте: {e}")
