#!/usr/bin/env python3
import asyncio
import os
import sys
import json
import requests
import subprocess
from datetime import datetime

# Import existing modules
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts_archive"))
from database import get_db
from telethon import TelegramClient, utils
from telethon.tl.functions.messages import ImportChatInviteRequest
from llm_extractor import extract_with_llm, LM_STUDIO_URL
from thoughtful_curator import run_curation_for_item, setup_ai_client

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(DIR_PATH)

API_ID = 27784305
API_HASH = "4f3e696f0c035287a9716b07a78dfd18"
SESSION_PATH = os.path.join(PARENT_DIR, "telegram_sync.session")
CHANNELS_FILE = os.path.join(DIR_PATH, "scripts_archive", "channels.json")

def notify(message):
    print(message)
    subprocess.run(['osascript', '-e', f'display notification "{message}" with title "Chiang Mai Guide Update"'])

def is_llm_running():
    try:
        url = LM_STUDIO_URL.replace("/chat/completions", "/models")
        r = requests.get(url, timeout=5)
        return r.status_code == 200
    except:
        return False

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
    from deduplicator import process_and_save_entity, archive_past_events
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        channels = json.load(f)
    
    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    await client.start()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT msg_id FROM processed_messages")
    processed_set = set(row[0] for row in cursor.fetchall())
    conn.close()
    
    total_added = 0
    new_item_ids = []

    for ch in channels:
        try:
            entity = await resolve_entity(client, ch)
            if not entity:
                continue
            
            title = getattr(entity, "title", ch)
            ch_username = getattr(entity, "username", "") or ""
            
            async for msg in client.iter_messages(entity, limit=300):
                if msg.id in processed_set:
                    continue
                raw_text = (msg.message or "").strip()
                if not raw_text or len(raw_text) < 10:
                    continue
                
                extracted = extract_with_llm(raw_text, reply_context="")
                if extracted and extracted.get("has_entity"):
                    sender_name = utils.get_display_name(msg.sender) if msg.sender else "Система"
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
                        if saved_id not in new_item_ids:
                            new_item_ids.append(saved_id)
                
                conn = get_db()
                conn.cursor().execute("INSERT OR IGNORE INTO processed_messages (msg_id, channel, processed_at) VALUES (?, ?, ?)", (msg.id, str(ch), msg.date.isoformat()))
                conn.commit()
                conn.close()
                processed_set.add(msg.id)
                
        except Exception as e:
            print(f"Error on {ch}: {e}")
            
    await client.disconnect()
    
    # Run thoughtful curation on newly added items so they look beautiful!
    if new_item_ids:
        notify(f"Найдено {len(new_item_ids)} новых объектов. Запускаю курацию через LLM...")
        try:
            ai_client, model = setup_ai_client()
            for item_id in new_item_ids:
                run_curation_for_item(item_id, ai_client, model)
            notify("База успешно обновлена!")
        except Exception as e:
            notify(f"Ошибка курации: {e}")
    else:
        print("Нет новых объектов.")

def start_lm_studio_and_load_model():
    try:
        import time
        import subprocess
        print("Starting LM Studio server via CLI...")
        subprocess.run(['/Users/artartemev/.cache/lm-studio/bin/lms', 'server', 'start'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        print("Loading model prism-ml/bonsai-27b...")
        subprocess.run(['/Users/artartemev/.cache/lm-studio/bin/lms', 'load', 'prism-ml/bonsai-27b'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Failed to start LM Studio automatically: {e}")
        return False

def main():
    if not is_llm_running():
        print("LM Studio is not running on expected port. Attempting to start automatically via lms CLI...")
        start_lm_studio_and_load_model()
        if not is_llm_running():
            print("Chiang Mai Guide: Could not start local LLM automatically. Will try again later.")
            return
            
    print("LM Studio is running. Starting sync...")
    asyncio.run(sync_telegram_channels())


if __name__ == "__main__":
    main()
