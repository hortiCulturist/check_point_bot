from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus
from asyncpg import PostgresError

from bot_app.db.common.chats import ChatsTable
from bot_app.misc import router, bot
from bot_app.utils.logger import log_chat_event


@router.my_chat_member()
async def handle_bot_promoted(event: ChatMemberUpdated):
    chat = event.chat
    me = await bot.get_me()

    if event.new_chat_member.user.id != me.id:
        return

    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status

    if old_status == ChatMemberStatus.ADMINISTRATOR and new_status != ChatMemberStatus.ADMINISTRATOR:
        log_chat_event(chat.id, chat.title, "⬇️ Бот снят с админки")

    elif new_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
        log_chat_event(chat.id, chat.title, "❌ Бот покинул или был удалён из группы")

    elif new_status == ChatMemberStatus.MEMBER:
        log_chat_event(chat.id, chat.title, "➕ Бот добавлен в группу как обычный участник")

    elif old_status != ChatMemberStatus.ADMINISTRATOR and new_status == ChatMemberStatus.ADMINISTRATOR:
        try:
            await ChatsTable.add_chat(chat.id, chat.title, event.from_user.id, chat.type)
            log_chat_event(chat.id, chat.title, "⬆️ Бот назначен админом")
            log_chat_event(chat.id, chat.title, "📦 Группа зарегистрирована в базе")
        except PostgresError as e:
            log_chat_event(chat.id, chat.title, f"❌ Ошибка при добавлении в базу: {e}")
