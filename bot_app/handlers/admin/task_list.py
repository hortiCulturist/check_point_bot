from urllib.parse import unquote

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot_app.db.common.tasks import TaskTable
from bot_app.markups.admin.base import get_admin_main_kb, get_tasks_chats_kb, get_tasks_list_kb, get_task_duration_kb, \
    get_cancel_kb, get_tasks_buttons_kb, get_task_action_kb
from bot_app.misc import router
from bot_app.states.admin.base import TaskStates
import re
from datetime import timedelta, datetime


@router.callback_query(lambda c: c.data == "admin_tasks")
async def show_tasks_chats(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("📂 Выберите чат:", reply_markup=await get_tasks_chats_kb())


@router.callback_query(lambda c: c.data == "admin_back_main")
async def back_to_main_menu(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("👑 Админ-панель:", reply_markup=get_admin_main_kb())


@router.callback_query(lambda c: c.data.startswith("admin_tasks_chat__"))
async def show_tasks_for_chat(call: CallbackQuery):
    await call.answer()
    parts = call.data.split("__", maxsplit=2)
    chat_id = int(parts[1])
    chat_title = unquote(parts[2]) if len(parts) > 2 else "Канал"

    tasks = await TaskTable.get_tasks_by_chat(chat_id)
    if not tasks:
        return await call.message.edit_text("ℹ️ В этом чате нет заданий.")

    await call.message.edit_text(
        "📝 Задания для чата:",
        reply_markup=get_tasks_buttons_kb(tasks)
    )


@router.callback_query(lambda c: c.data.startswith("admin_task_actions__"))
async def task_actions(call: CallbackQuery):
    await call.answer()
    task_id = int(call.data.split("__")[1])
    task = await TaskTable.get_task(task_id)

    if not task:
        return await call.message.answer("❌ Задание не найдено.")

    await call.message.edit_text(
        f"📂 Управление заданием: {task['title'] or 'ID ' + str(task_id)}",
        reply_markup=get_task_action_kb(task)
    )


@router.callback_query(lambda c: c.data.startswith("admin_activate_menu__"))
async def show_activate_menu(call: CallbackQuery):
    await call.answer()
    task_id = int(call.data.split("__")[1])
    await call.message.edit_text(
        "⏱ Выберите длительность задания:",
        reply_markup=get_task_duration_kb(task_id)
    )


@router.callback_query(lambda c: c.data.startswith("admin_task_activate__"))
async def activate_task_with_duration(call: CallbackQuery):
    await call.answer()
    _, task_id, days = call.data.split("__")
    task_id = int(task_id)
    days = int(days)

    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(days=days)

    await TaskTable.set_task_expiration(task_id, expires_at)
    await TaskTable.activate_task(task_id)

    await call.message.edit_text("✅ Задание активировано!")


@router.callback_query(lambda c: c.data.startswith("admin_task_manual__"))
async def manual_task_input(call: CallbackQuery, state: FSMContext):
    await call.answer()
    task_id = int(call.data.split("__")[1])

    await state.update_data(task_id=task_id)
    await state.set_state(TaskStates.waiting_for_duration_input)

    try:
        await call.message.delete()
    except Exception:
        pass

    await call.message.answer(
        "⏱️ Введите время в формате: `10m`, `2h`, `3d`.",
        reply_markup=get_cancel_kb(),
        parse_mode="Markdown"
    )


@router.callback_query(lambda c: c.data == "admin_back_to_duration")
async def back_to_duration_menu(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    task_id = data.get("task_id")

    from bot_app.markups.admin.base import get_task_duration_kb
    await call.message.edit_text(
        "⏱ Выберите длительность задания:",
        reply_markup=get_task_duration_kb(task_id)
    )
    await state.clear()


@router.message(TaskStates.waiting_for_duration_input)
async def process_manual_duration_input(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()

    match = re.fullmatch(r"(\d+)([mhd])", text)
    if not match:
        return await message.answer("❌ Неверный формат. Введите как `10m`, `2h`, `3d`.")

    value, unit = int(match[1]), match[2]
    delta = {"m": timedelta(minutes=value), "h": timedelta(hours=value), "d": timedelta(days=value)}[unit]
    expires_at = datetime.utcnow() + delta

    data = await state.get_data()
    task_id = data.get("task_id")

    await TaskTable.set_task_expiration(task_id, expires_at)
    await TaskTable.activate_task(task_id)

    await message.answer("✅ Время задания установлено.", reply_markup=get_admin_main_kb())
    await state.clear()


@router.callback_query(lambda c: c.data.startswith("admin_task_delete__"))
async def delete_task(call: CallbackQuery):
    await call.answer()
    task_id = int(call.data.split("__")[1])

    task = await TaskTable.get_task(task_id)
    if not task:
        return await call.message.edit_text("❌ Задание не найдено.")

    await TaskTable.delete_task(task_id)

    await call.message.edit_text(f"🗑 Задание «{task['title']}» удалено.")

