import asyncio

import aiocron
from aiogram import Bot

from bot_app.handlers.main import router
from bot_app.middlewares.access_control import AccessControlMiddleware
from bot_app.middlewares.base import ChatActiveMiddleware
from bot_app.misc import bot, dp
from bot_app.utils.cron import deactivate_expired_tasks

dp.message.middleware(ChatActiveMiddleware())
dp.message.middleware(AccessControlMiddleware())

dp.include_router(router)


async def print_start_info(bot: Bot):
    me = await bot.get_me()

    print("=" * 40)
    print("🤖 Бот запущен!")
    print(f"📛 Username: @{me.username}")
    print(f"🆔 ID: {me.id}")
    print(f"👤 Имя: {me.first_name}")
    print("=" * 40)


async def main():
    await print_start_info(bot)
    aiocron.crontab("*/1 * * * *")(deactivate_expired_tasks)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
