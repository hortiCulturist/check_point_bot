from aiogram import types
from aiogram.filters import Command

from bot_app.misc import router


@router.message(Command("user"))
async def start_handler(message: types.Message):
    await message.answer("Привет user! Я готов к работе.")