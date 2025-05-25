from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot_app.db.common.tasks import TaskTable
from bot_app.states.admin.base import AddTaskStates
from bot_app.db.common.chats import ChatsTable
from bot_app.misc import router
from bot_app.markups.admin.base import get_admin_main_kb, get_cancel_new_task_kb
from aiogram.utils.keyboard import InlineKeyboardBuilder
from urllib.parse import quote
from datetime import timedelta, datetime
import re


@router.callback_query(lambda c: c.data == "admin_add_task")
async def start_add_task(call: CallbackQuery, state: FSMContext):
    await call.answer()
    chats = await ChatsTable.get_all_active()

    if not chats:
        return await call.message.edit_text("⚠️ Нет активных чатов. Сначала активируйте хотя бы один.",
                                            reply_markup=get_admin_main_kb())

    builder = InlineKeyboardBuilder()
    for chat in chats:
        title = chat["title"] or "Без названия"
        builder.button(
            text=title,
            callback_data=f"admin_add_task_chat__{chat['chat_id']}__{quote(title)}"
        )
    builder.button(text="🔙 Назад", callback_data="admin_back_to_main")
    builder.adjust(1)

    await state.set_state(AddTaskStates.choosing_chat)
    await call.message.edit_text("💬 Выберите чат, для которого будет задание:", reply_markup=builder.as_markup())


@router.callback_query(lambda c: c.data.startswith("admin_add_task_chat__"))
async def choose_chat_for_task(call: CallbackQuery, state: FSMContext):
    await call.answer()
    parts = call.data.split("__", maxsplit=2)
    chat_id = int(parts[1])
    chat_title = parts[2]

    await state.update_data(chat_id=chat_id, chat_title=chat_title)
    await state.set_state(AddTaskStates.entering_title)

    await call.message.edit_text("✏️ Введите название задания:", reply_markup=get_cancel_new_task_kb())


@router.message(AddTaskStates.entering_title)
async def enter_task_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddTaskStates.entering_type)

    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 Ссылка", callback_data="task_type__url")
    builder.button(text="🤖 Бот", callback_data="task_type__bot")
    builder.button(text="📣 Канал", callback_data="task_type__channel")
    builder.button(text="👥 Группа", callback_data="task_type__group")
    builder.button(text="🔙 Назад", callback_data="admin_add_task_back_title")
    builder.adjust(2, 1)

    await message.answer("📌 Выберите тип задания:", reply_markup=builder.as_markup())


@router.callback_query(lambda c: c.data.startswith("task_type__"))
async def choose_task_type(call: CallbackQuery, state: FSMContext):
    await call.answer()
    task_type = call.data.split("__")[1]
    await state.update_data(task_type=task_type)
    await state.set_state(AddTaskStates.entering_target_url)

    await call.message.edit_text("🔗 Вставьте ссылку/цель:", reply_markup=get_cancel_new_task_kb())


@router.message(AddTaskStates.entering_target_url)
async def enter_target_url(message: types.Message, state: FSMContext):
    await state.update_data(target_url=message.text.strip())
    await state.set_state(AddTaskStates.entering_button_text)
    await message.answer("💬 Текст кнопки:", reply_markup=get_cancel_new_task_kb())


@router.message(AddTaskStates.entering_button_text)
async def enter_button_text(message: types.Message, state: FSMContext):
    await state.update_data(button_text=message.text.strip())
    await state.set_state(AddTaskStates.entering_manual_duration)

    builder = InlineKeyboardBuilder()
    for d in [1, 2, 3, 4, 7]:
        builder.button(text=f"{d} д", callback_data=f"task_expire__{d}")
    builder.button(text="✍ Ввести вручную", callback_data="task_expire__manual")
    builder.button(text="🔙 Назад", callback_data="admin_add_task_back_button")
    builder.adjust(4, 1, 1)

    await message.answer("⏱️ Укажите время действия задания:", reply_markup=builder.as_markup())


@router.callback_query(lambda c: c.data.startswith("task_expire__"))
async def handle_duration_choice(call: CallbackQuery, state: FSMContext):
    await call.answer()
    key = call.data.split("__")[1]

    if key == "manual":
        await state.set_state(AddTaskStates.entering_manual_duration)
        await call.message.edit_text(
            "✍ Введите длительность вручную (например: `10m`, `2h`, `3d`):",
            parse_mode="Markdown",
            reply_markup=get_cancel_new_task_kb()
        )
        return

    days = int(key)
    expires_at = datetime.utcnow() + timedelta(days=days)

    data = await state.get_data()
    await TaskTable.add_task(
        chat_id=int(data["chat_id"]),
        title=data["title"],
        task_type=data["task_type"],
        url=data["target_url"],
        button_text=data["button_text"],
        expires_at=expires_at
    )

    await state.clear()
    await call.message.edit_text("✅ Задание успешно добавлено!", reply_markup=get_admin_main_kb())


@router.message(AddTaskStates.entering_manual_duration)
async def handle_manual_duration(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()
    match = re.fullmatch(r"(\d+)([mhd])", text)

    if not match:
        return await message.answer("❌ Неверный формат. Используйте `10m`, `2h`, `3d`.")

    value, unit = int(match[1]), match[2]
    delta = {"m": timedelta(minutes=value), "h": timedelta(hours=value), "d": timedelta(days=value)}[unit]
    expires_at = datetime.utcnow() + delta

    data = await state.get_data()
    await TaskTable.add_task(
        chat_id=int(data["chat_id"]),
        title=data["title"],
        task_type=data["task_type"],
        url=data["target_url"],
        button_text=data["button_text"],
        expires_at=expires_at
    )

    await state.clear()
    await message.answer("✅ Задание успешно добавлено!", reply_markup=get_admin_main_kb())








@router.callback_query(lambda c: c.data == "admin_back_to_main")
async def back_to_main_menu(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    await call.message.edit_text("👑 Админ-панель:", reply_markup=get_admin_main_kb())


@router.callback_query(lambda c: c.data == "admin_back_to_new_task")
async def back_to_choose_chat(call: CallbackQuery, state: FSMContext):
    await call.answer()
    chats = await ChatsTable.get_all_active()

    builder = InlineKeyboardBuilder()
    for chat in chats:
        title = chat["title"] or "Без названия"
        builder.button(
            text=title,
            callback_data=f"admin_add_task_chat__{chat['chat_id']}__{quote(title)}"
        )
    builder.button(text="🔙 Назад", callback_data="admin_back_to_main")
    builder.adjust(1)

    await state.set_state(AddTaskStates.choosing_chat)
    await call.message.edit_text("💬 Выберите чат, для которого будет задание:", reply_markup=builder.as_markup())


@router.callback_query(lambda c: c.data == "admin_add_task_back_title")
async def back_to_title_input(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AddTaskStates.entering_title)
    await call.message.edit_text("✏️ Введите название задания:", reply_markup=get_cancel_new_task_kb())


@router.callback_query(lambda c: c.data == "admin_add_task_back_button")
async def back_to_button_text(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AddTaskStates.entering_button_text)
    await call.message.edit_text("💬 Текст кнопки:", reply_markup=get_cancel_new_task_kb())


@router.callback_query(lambda c: c.data == "admin_back_to_duration")
async def back_to_duration_menu(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AddTaskStates.entering_manual_duration)

    builder = InlineKeyboardBuilder()
    for d in [1, 2, 3, 4, 7]:
        builder.button(text=f"{d} д", callback_data=f"task_expire__{d}")
    builder.button(text="✍ Ввести вручную", callback_data="task_expire__manual")
    builder.button(text="🔙 Назад", callback_data="admin_add_task_back_button")
    builder.adjust(4, 1, 1)

    await call.message.edit_text("⏱️ Укажите время действия задания:", reply_markup=builder.as_markup())