from datetime import datetime

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot_app.config import ADMIN_ID
from bot_app.db.common.task_completions import TaskCompletionTable
from bot_app.db.common.tasks import TaskTable
from bot_app.db.user.base import UserChatLinkTable
from bot_app.misc import bot, router
from bot_app.utils.logger import log_chat_event


@router.callback_query(lambda c: c.data == "check_access")
async def check_access(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    chat_id = data.get("chat_id")
    user_id = call.from_user.id

    start_time_str = data.get("start_time")
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str)
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        if elapsed < 15:
            return await call.message.answer("⏳ Не так быстро. Выполните задание.")

    try:
        tasks = await TaskTable.get_active_tasks(chat_id)
        for task in tasks:
            await TaskCompletionTable.mark_completed(user_id, chat_id, task["id"])

        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions={
                "can_send_messages": True,
                "can_send_media_messages": True,
                "can_send_other_messages": True,
                "can_add_web_page_previews": True,
            }
        )

        await UserChatLinkTable.set_unrestricted(chat_id, user_id)
        await UserChatLinkTable.set_verified(chat_id, user_id)

        await call.message.answer("✅ Доступ открыт! Можете писать в чате.")
        log_chat_event(chat_id, "Bot", f"🔓 Пользователь {user_id} получил доступ после выполнения заданий")
        await state.clear()

    except Exception as e:
        await call.message.answer("⚠️ Произошла ошибка при разблокировке.")
        log_chat_event(chat_id, "Bot", f"❌ Ошибка при разблокировке {user_id}: {e}")


@router.message()
async def catch_all(message: types.Message):
    if message.from_user.id in ADMIN_ID:
        return

    pass
