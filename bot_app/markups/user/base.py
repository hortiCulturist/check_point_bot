from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot_app.misc import bot


def check_ready_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Я выполнил", callback_data="check_access")
    return builder.as_markup()


async def get_start_button(chat_id: int):
    me = await bot.get_me()
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔓 Получить доступ",
        url=f"https://t.me/{me.username}?start=group__{abs(chat_id)}"
    )
    return builder.as_markup()


def get_tasks_markup(tasks: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for task in tasks:
        builder.button(
            text=task["button_text"],
            url=task["target_url"]
        )
        builder.adjust(1)

    builder.button(
        text="✅ Я выполнил",
        callback_data="check_access"
    )
    builder.adjust(1)

    return builder.as_markup()
