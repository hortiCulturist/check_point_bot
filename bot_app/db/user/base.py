from bot_app.db.main import create_con
from bot_app.utils.logger import log_chat_event


class UserTable:
    @staticmethod
    async def add_user(user_id: int, username: str, full_name: str):
        con = await create_con()
        try:
            query = """
                INSERT INTO users (user_id, username, full_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO NOTHING;
            """
            result = await con.execute(query, user_id, username, full_name)
            if result == "INSERT 0 1":
                log_chat_event(user_id, "DB", f"👤 Пользователь зарегистрирован: {username or full_name}")
        except Exception as e:
            log_chat_event(user_id, "DB", f"❌ Ошибка при добавлении пользователя: {e}")
        finally:
            await con.close()


class UserChatLinkTable:
    @staticmethod
    async def add_link(user_id: int, chat_id: int):
        con = await create_con()
        try:
            query = """
                INSERT INTO user_chat_links (user_id, chat_id)
                VALUES ($1, $2)
                ON CONFLICT (user_id, chat_id) DO NOTHING;
            """
            result = await con.execute(query, user_id, chat_id)
            if result == "INSERT 0 1":
                log_chat_event(chat_id, "DB", f"🔗 Связь с пользователем {user_id} добавлена")
        except Exception as e:
            log_chat_event(chat_id, "DB", f"❌ Ошибка при добавлении связи user-chat: {e}")
        finally:
            await con.close()

    @staticmethod
    async def is_verified(chat_id: int, user_id: int) -> bool:
        con = await create_con()
        try:
            query = """
                SELECT is_verified FROM user_chat_links
                WHERE chat_id = $1 AND user_id = $2
            """
            result = await con.fetchrow(query, chat_id, user_id)
            return result and result.get("is_verified") is True
        except Exception as e:
            log_chat_event(chat_id, "DB", f"❌ Ошибка при проверке verified: {e}")
            return False
        finally:
            await con.close()

    @staticmethod
    async def set_verified(chat_id: int, user_id: int):
        con = await create_con()
        try:
            query = """
                UPDATE user_chat_links
                SET is_verified = TRUE
                WHERE chat_id = $1 AND user_id = $2;
            """
            await con.execute(query, chat_id, user_id)
            log_chat_event(chat_id, "DB", f"✅ Помечен как verified: {user_id}")
        except Exception as e:
            log_chat_event(chat_id, "DB", f"❌ Ошибка при set_verified: {e}")
        finally:
            await con.close()

    @staticmethod
    async def set_restricted(chat_id: int, user_id: int):
        con = await create_con()
        try:
            query = """
                UPDATE user_chat_links
                SET was_restricted = TRUE
                WHERE chat_id = $1 AND user_id = $2;
            """
            await con.execute(query, chat_id, user_id)
            log_chat_event(chat_id, "DB", f"🔒 Помечен как TRUE в was_restricted: {user_id}")
        except Exception as e:
            log_chat_event(chat_id, "DB", f"❌ Ошибка при set_restricted: {e}")
        finally:
            await con.close()

    @staticmethod
    async def set_unrestricted(chat_id: int, user_id: int):
        con = await create_con()
        try:
            query = """
                UPDATE user_chat_links
                SET was_restricted = FALSE
                WHERE chat_id = $1 AND user_id = $2;
            """
            await con.execute(query, chat_id, user_id)
            log_chat_event(chat_id, "DB", f"🔒 Помечен как FALSE в was_restricted: {user_id}")
        except Exception as e:
            log_chat_event(chat_id, "DB", f"❌ Ошибка при set_restricted: {e}")
        finally:
            await con.close()
