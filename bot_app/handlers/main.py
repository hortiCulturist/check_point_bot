import logging

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot_app.markups.user.base import check_ready_kb
from bot_app.misc import router
from bot_app.states.user.base import AccessFlow

logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    text = message.text.strip()

    if text == "/start":
        await message.answer("Привет! Я готов к работе.")
        return

    if text.startswith("/start group__"):
        payload = text.split(" ", maxsplit=1)[-1]
        chat_id = int(payload.replace("group__", "-"))
        await state.update_data(chat_id=chat_id, user_id=message.from_user.id)
        await state.set_state(AccessFlow.waiting_for_check)

        await message.answer(
            f"📋 Задание для доступа к чату:\n(например: подпишитесь на канал)\n\nНажмите кнопку, когда выполните:",
            reply_markup=check_ready_kb()
        )
        return

    pass
