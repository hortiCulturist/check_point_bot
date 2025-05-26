import os
from datetime import datetime


def log_chat_event(chat_id: int, title: str, message: str):
    title_safe = (title or "Unnamed").replace(" ", "_").replace("/", "_")
    # пока логи добавляем кучей просто в файлы по title
    log_dir = "logs/chats_logs"
    os.makedirs(log_dir, exist_ok=True)

    file_path = os.path.join(log_dir, f"{title_safe}.log")

    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{time}] [{chat_id}] {message}"

    print(f"🖨️  {title} | {chat_id} → {log_line}")

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")


# def log_chat_event(chat_id: int, title: str, message: str):
#     role = title.lower()
#
#     # определяем тип логов
#     if role in ("bot", "db", "redis"):
#         subdir = f"group_{chat_id}"
#         filename = f"{role}.log"
#     else:
#         subdir = f"group_{chat_id}/users"
#         filename = f"{title}.log" if title else "unknown_user.log"
#
#     log_dir = os.path.join("logs", "chats_logs", subdir)
#     os.makedirs(log_dir, exist_ok=True)
#
#     file_path = os.path.join(log_dir, filename)
#     time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     log_line = f"[{time}] {message}"
#
#     print(f"🖨️  {chat_id} | {title} → {log_line}")
#
#     with open(file_path, "a", encoding="utf-8") as f:
#         f.write(log_line + "\n")
