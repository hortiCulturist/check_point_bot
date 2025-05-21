from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot_app.misc import bot, router
from bot_app.utils.logger import log_chat_event


@router.callback_query(lambda c: c.data == "check_access")
async def check_access(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    chat_id = data.get("chat_id")
    user_id = call.from_user.id

    # Заглушка: даём доступ без проверки
    try:
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

        await call.message.answer("✅ Доступ открыт! Можете писать в чате.")
        log_chat_event(chat_id, "Bot", f"🔓 Пользователь {user_id} получил доступ по заглушке")
        await state.clear()

    except Exception as e:
        await call.message.answer("⚠️ Произошла ошибка при разблокировке.")
        log_chat_event(chat_id, "Bot", f"❌ Ошибка при разблокировке {user_id}: {e}")
