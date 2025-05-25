import logging

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot_app.db.common.tasks import TaskTable
from bot_app.db.user.base import UserChatLinkTable, UserTable
from bot_app.misc import router
from bot_app.states.user.base import AccessFlow
from datetime import datetime

logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    text = message.text.strip()

    if text == "/start":
        await message.answer(
            "👋 Привет! Для использования бота присоединитесь к чату и нажмите кнопку внутри."
        )
        return

    if text.startswith("/start group__"):
        payload = text.removeprefix("/start ").strip()
        try:
            chat_id = int(payload.replace("group__", "-"))
        except ValueError:
            return await message.answer("⚠️ Неверный формат ссылки.")

        user = message.from_user
        user_id = user.id

        await UserTable.add_user(user_id, user.username, user.full_name)
        await UserChatLinkTable.add_link(user_id, chat_id)

        await state.update_data(
            chat_id=chat_id,
            user_id=user_id,
            start_time=datetime.utcnow().isoformat()
        )
        await state.set_state(AccessFlow.waiting_for_check)

        tasks = await TaskTable.get_active_tasks(chat_id)

        if tasks:
            from bot_app.markups.user.base import get_tasks_markup
            markup = get_tasks_markup(tasks)

            titles = "\n".join([f"🔹 {task['title']}" for task in tasks])
            text = f"📋 Выполните все задания:\n\n{titles}\n\n👉 Когда выполните, нажмите кнопку ниже."
        else:
            from bot_app.markups.user.base import check_ready_kb
            markup = check_ready_kb()
            text = "📋 У вас нет активных заданий. Просто нажмите кнопку ниже, чтобы получить доступ."

        await message.answer(text, reply_markup=markup)
        return

    await message.answer("❗️Команда не распознана.")
