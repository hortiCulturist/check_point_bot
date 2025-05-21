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
