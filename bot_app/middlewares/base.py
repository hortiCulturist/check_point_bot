from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Dict

from database.tables.chats import ChatsTable  # предположим ты так назовешь


class ChatActiveMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict], Awaitable],
        event: Message,
        data: Dict
    ) -> Awaitable:
        chat = event.chat

        # проверяем, что это группа/супергруппа
        if chat.type in ("group", "supergroup"):
            is_active = await ChatsTable.is_active(chat.id)
            if not is_active:
                return  # не пропускаем дальше

        return await handler(event, data)