import asyncio

from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Dict

from bot_app.db.common.chats import ChatsTable


class ChatActiveMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict], Awaitable],
        event: Message,
        data: Dict
    ) -> Awaitable:
        chat = event.chat

        if chat.type in ("group", "supergroup"):
            is_active = await ChatsTable.is_active(chat.id)
            if not is_active:
                return await asyncio.sleep(0)

        return await handler(event, data)