from aiogram.utils.keyboard import InlineKeyboardBuilder


def check_ready_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Я выполнил", callback_data="check_access")
    return builder.as_markup()
