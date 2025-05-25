from aiogram import types
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from bot_app.config import ADMIN_ID
from bot_app.markups.admin.base import get_admin_main_kb
from bot_app.misc import router


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_ID:
        pass

    await message.answer("👑 Админ-панель:", reply_markup=get_admin_main_kb())


@router.callback_query(lambda c: c.data == "admin_stats")
async def show_stats_unavailable(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "📊 Раздел статистики пока недоступен.\n\nВ разработке 🚧")
