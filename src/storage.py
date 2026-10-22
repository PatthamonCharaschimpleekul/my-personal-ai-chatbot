import os
import json
import uuid
import time
from src.logger_config import logger

HISTORY_DIR = "chat_history"

def ensure_history_dir():
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

def save_chat(chat_id, messages, title=None):
    ensure_history_dir()
    if not title and messages:
        # ใช้ 30 ตัวแรกของ user message แรกเป็นหัวข้อ
        first_user_msg = next((m["content"] for m in messages if m["role"] == "user"), "New Chat")
        title = first_user_msg[:30] + "..."

    data = {
        "id": chat_id,
        "title": title or "Untitled Chat",
        "updated_at": time.time(),
        "messages": messages
    }

    file_path = os.path.join(HISTORY_DIR, f"{chat_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

def list_chats():
    ensure_history_dir()
    chats = []
    if not os.path.exists(HISTORY_DIR): return []
    for f_name in os.listdir(HISTORY_DIR):
        if f_name.endswith(".json"):
            try:
                with open(os.path.join(HISTORY_DIR, f_name), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    chats.append({
                        "id": data["id"],
                        "title": data["title"],
                        "updated_at": data["updated_at"]
                    })
            except:
                pass
    # เรียงตามเวลาล่าสุด
    return sorted(chats, key=lambda x: x["updated_at"], reverse=True)

def load_chat(chat_id):
    file_path = os.path.join(HISTORY_DIR, f"{chat_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None
