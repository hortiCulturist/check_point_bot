from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from urllib.parse import quote


def get_admin_main_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text="📄 Список заданий", callback_data="admin_tasks")
    builder.button(text="➕ Добавить задание", callback_data="admin_add_task")
    builder.button(text="💬 Мои группы", callback_data="admin_chats")
    builder.button(text="📊 Статистика❌", callback_data="admin_stats")
    builder.adjust(1)

    return builder.as_markup()


async def get_tasks_chats_kb() -> InlineKeyboardMarkup:
    from bot_app.db.common.tasks import TaskTable
    chats = await TaskTable.get_chats_with_tasks()

    builder = InlineKeyboardBuilder()

    if chats:
        for chat in chats:
            title_raw = chat["title"] or "Канал"
            try:
                title_encoded = quote(title_raw)
            except Exception:
                title_encoded = "Канал"

            builder.button(
                text=title_raw,
                callback_data=f"admin_tasks_chat__{chat['chat_id']}__{title_encoded}"
            )

        builder.adjust(1)  # каждая кнопка в своём ряду

    # Добавляем кнопку назад в последнем ряду
    builder.button(
        text="🔙 Назад",
        callback_data="admin_back_main"
    )
    builder.adjust(1)

    return builder.as_markup()


def get_tasks_list_kb(tasks: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for task in tasks:
        title = task['title'] or f"ID {task['id']}"
        title_with_id = f"{title} (ID {task['id']})"
        status = "✅" if task['is_active'] else "🚫"
        builder.button(
            text=f"{status} {title_with_id}",
            callback_data=f"admin_task_toggle__{task['id']}"
        )

    builder.button(text="🔙 Назад", callback_data="admin_tasks")
    builder.adjust(1)

    return builder.as_markup()


def get_task_duration_kb(task_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for d in [1, 2, 3, 4]:
        builder.button(
            text=f"{d}д",
            callback_data=f"admin_task_activate__{task_id}__{d}"
        )
    builder.button(
        text="7д",
        callback_data=f"admin_task_activate__{task_id}__7"
    )
    builder.button(
        text="✍ Ввести вручную",
        callback_data=f"admin_task_manual__{task_id}"
    )
    builder.button(
        text="🔙 Назад",
        callback_data="admin_tasks"
    )
    builder.adjust(4, 1, 1, 1)

    return builder.as_markup()


def get_cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="admin_back_to_duration")
    return builder.as_markup()


def get_cancel_new_task_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="admin_back_to_new_task")
    return builder.as_markup()


def get_tasks_buttons_kb(tasks: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for task in tasks:
        title = task["title"] or f"ID {task['id']}"
        status = "✅" if task["is_active"] else "🚫"
        builder.button(
            text=f"{status} {title}",
            callback_data=f"admin_task_actions__{task['id']}"
        )

    builder.button(text="🔙 Назад", callback_data="admin_tasks")
    builder.adjust(1)
    return builder.as_markup()


def get_task_action_kb(task: dict) -> InlineKeyboardMarkup:
    task_id = task["id"]
    builder = InlineKeyboardBuilder()

    if not task["is_active"]:
        builder.button(text="✅ Активировать", callback_data=f"admin_activate_menu__{task_id}")
    builder.button(text="🗑 Удалить", callback_data=f"admin_task_delete__{task_id}")
    builder.button(text="🔙 Назад", callback_data="admin_tasks")

    builder.adjust(1)
    return builder.as_markup()
