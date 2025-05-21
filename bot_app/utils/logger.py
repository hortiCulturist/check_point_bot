import os
from datetime import datetime


def log_chat_event(chat_id: int, title: str, message: str):
    title_safe = title.replace(" ", "_").replace("/", "_") or "Unnamed"
    log_dir = "logs/chats_logs"
    os.makedirs(log_dir, exist_ok=True)

    file_path = os.path.join(log_dir, f"{chat_id}_{title_safe}.log")
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{time}] {message}"

    # Печатаем в консоль
    print(f"🖨️  {chat_id} | {title} → {log_line}")

    # Записываем в файл
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
        