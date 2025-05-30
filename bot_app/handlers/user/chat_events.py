from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus

from bot_app.db.user.base import UserTable, UserChatLinkTable
from bot_app.markups.user.base import get_start_button
from bot_app.misc import bot, router
from bot_app.db.common.chats import ChatsTable
from bot_app.utils.logger import log_chat_event


@router.chat_member()
async def on_user_joined(event: ChatMemberUpdated):
    chat = event.chat
    user = event.new_chat_member.user

    if user.is_bot:
        return

    if event.new_chat_member.status != ChatMemberStatus.MEMBER:
        return

    is_active = await ChatsTable.is_active(chat.id)
    if not is_active:
        return

    try:
        await UserTable.add_user(user.id, user.username, user.full_name)
        await UserChatLinkTable.add_link(user.id, chat.id)

        await bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=user.id,
            permissions={
                "can_send_messages": False,
                "can_send_media_messages": False,
                "can_send_other_messages": False,
                "can_add_web_page_previews": False,
            }
        )
        await UserChatLinkTable.set_restricted(chat.id, user.id)
        log_chat_event(chat.id, chat.title, f"🔒 Ограничен {user.full_name} ({user.id}) при входе")

        await bot.send_message(
            chat_id=chat.id,
            text=f"👋 Чтобы писать в чате — откройте бота и выполните задание:",
            reply_markup=await get_start_button(chat.id)
        )
        log_chat_event(chat.id, chat.title, f"📨 {user.full_name} ({user.id}) направлен в бота")

    except Exception as e:
        log_chat_event(chat.id, chat.title, f"⚠️ Ошибка при ограничении {user.id}: {e}")

