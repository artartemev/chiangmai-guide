#!/usr/bin/env python3
import asyncio
import json
import os
import sys
import uvicorn
from database import init_db, get_db
from llm_extractor import extract_with_llm
from deduplicator import process_and_save_entity, archive_past_events
from telethon import TelegramClient, utils
from telethon.tl.functions.messages import ImportChatInviteRequest

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(DIR_PATH)

API_ID = 27784305
API_HASH = "4f3e696f0c035287a9716b07a78dfd18"
SESSION_PATH = os.path.join(PARENT_DIR, "telegram_sync.session")
CHANNELS_FILE = os.path.join(DIR_PATH, "channels.json")

async def resolve_entity(client, ch):
    ch_str = str(ch).strip()
    try:
        return await client.get_entity(ch_str)
    except Exception:
        pass
    if "+" in ch_str or "joinchat" in ch_str:
        invite_hash = ch_str.split("+")[-1].split("/")[-1]
        try:
            updates = await client(ImportChatInviteRequest(invite_hash))
            if updates and hasattr(updates, "chats") and updates.chats:
                return updates.chats[0]
        except Exception:
            pass
    async for dialog in client.iter_dialogs():
        uname = getattr(dialog.entity, "username", "") or ""
        if ch_str.lower() in dialog.name.lower() or (uname and uname.lower() == ch_str.lower()):
            return dialog.entity
    return None

async def sync_telegram_channels():
    print("🔄 Запуск сбора данных из каналов Чиангмая...")
    if not os.path.exists(CHANNELS_FILE):
        print("⚠️ Файл channels.json не найден.")
        return
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        channels = json.load(f)
    if not channels:
        print("⚠️ Список каналов в channels.json пуст.")
        return
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    await client.start()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT msg_id FROM processed_messages")
    processed_set = set(row[0] for row in cursor.fetchall())
    conn.close()
    total_added = 0
    for ch in channels:
        print(f"🔍 Сканирование чата/канала: {ch}...")
        try:
            entity = await resolve_entity(client, ch)
            if not entity:
                print(f"⚠️ Не удалось разрешить канал: {ch}")
                continue
            title = getattr(entity, "title", ch)
            ch_username = getattr(entity, "username", "") or ""
            async for msg in client.iter_messages(entity, limit=300):
                if msg.id in processed_set:
                    continue
                raw_text = (msg.message or "").strip()
                if not raw_text or len(raw_text) < 10:
                    continue
                
                reply_context = ""
                if msg.reply_to and getattr(msg.reply_to, "reply_to_msg_id", None):
                    try:
                        reply_msg = await client.get_messages(entity, ids=msg.reply_to.reply_to_msg_id)
                        if reply_msg and reply_msg.message:
                            reply_context = reply_msg.message.strip()
                    except Exception:
                        pass
                        
                extracted = extract_with_llm(raw_text, reply_context=reply_context)
                if extracted and extracted.get("has_entity"):
                    sender_name = "Система"
                    if msg.sender:
                        sender_name = utils.get_display_name(msg.sender)
                    msg_date = msg.date.strftime("%Y-%m-%d %H:%M:%S")
                    review_meta = {
                        "msg_id": msg.id,
                        "channel": title,
                        "sender": sender_name,
                        "date": msg_date,
                        "text": raw_text,
                        "reactions": "",
                        "source_link": f"https://t.me/{ch_username}/{msg.id}" if ch_username else ""
                    }
                    saved_id = process_and_save_entity(extracted, review_meta)
                    if saved_id:
                        total_added += 1
                conn = get_db()
                conn.cursor().execute("INSERT OR IGNORE INTO processed_messages (msg_id, channel, processed_at) VALUES (?, ?, ?)", (msg.id, str(ch), msg.date.isoformat()))
                conn.commit()
                conn.close()
                processed_set.add(msg.id)
        except Exception as e:
            print(f"⚠️ Ошибка при обработке канала {ch}: {e}")
    archive_past_events()
    await client.disconnect()
    print(f"✅ Синхронизация завершена! Добавлено/Обновлено мест и событий: {total_added}")

def main():
    init_db()
    if os.path.exists(SESSION_PATH):
        try:
            asyncio.run(sync_telegram_channels())
        except Exception as e:
            print(f"⚠️ Telegram sync skipped: {e}")
    else:
        print("ℹ️ Telegram session file not found. Running with existing database.")
    print("\n🌐 Запуск веб-портала Chiang Mai Guide по адресу: http://localhost:8088")
    from app import app
    uvicorn.run(app, host="0.0.0.0", port=8088)

if __name__ == "__main__":
    main()
