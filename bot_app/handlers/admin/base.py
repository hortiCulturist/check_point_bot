from aiogram import types
from aiogram.filters import Command

from bot_app.misc import router


@router.message(Command("admin"))
async def start_handler(message: types.Message):
    await message.answer("Привет admin! Я готов к работе.")