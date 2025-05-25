from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot_app.db.common.chats import ChatsTable
from bot_app.misc import router
from bot_app.markups.admin.base import get_admin_main_kb
from aiogram.utils.keyboard import InlineKeyboardBuilder


@router.callback_query(lambda c: c.data == "admin_chats")
async def show_admin_chats(call: CallbackQuery):
    await call.answer()
    chats = await ChatsTable.get_all()

    if not chats:
        return await call.message.edit_text("⚠️ Нет зарегистрированных групп.", reply_markup=get_admin_main_kb())

    builder = InlineKeyboardBuilder()
    for chat in chats:
        status = "✅ Включена" if chat["is_active"] else "🚫 Выключена"
        builder.button(
            text=f"{chat['title'] or 'Канал'} • {status}",
            callback_data=f"admin_toggle_chat__{chat['chat_id']}"
        )
    builder.button(text="🔙 Назад", callback_data="admin_back_to_main")
    builder.adjust(1)

    await call.message.edit_text("💬 Управление группами:", reply_markup=builder.as_markup())


@router.callback_query(lambda c: c.data.startswith("admin_toggle_chat__"))
async def toggle_chat_status(call: CallbackQuery):
    await call.answer()
    chat_id = int(call.data.split("__")[1])
    is_active = await ChatsTable.is_active(chat_id)

    if is_active:
        await ChatsTable.deactivate_chat(chat_id)
    else:
        await ChatsTable.activate_chat(chat_id)

    await call.message.edit_text("🔁 Статус группы обновлён. Открываю список заново...")
    await show_admin_chats(call)
