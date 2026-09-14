import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chiangmai_guide.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            dietary_type TEXT DEFAULT "none",
            neighborhood TEXT DEFAULT "Other",
            description TEXT,
            location_url TEXT,
            venue_name TEXT DEFAULT "",
            opening_hours TEXT DEFAULT "",
            address TEXT DEFAULT "",
            phone_contact TEXT DEFAULT "",
            website TEXT DEFAULT "",
            latitude REAL DEFAULT 0.0,
            longitude REAL DEFAULT 0.0,
            event_date TEXT,
            event_status TEXT DEFAULT "none",
            event_iso_date TEXT DEFAULT NULL,
            registration_url TEXT DEFAULT "",
            registration_label TEXT DEFAULT "",

            mention_count INTEGER DEFAULT 1,
            photos_json TEXT DEFAULT "[]",
            created_at TEXT,
            updated_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            telegram_msg_id INTEGER,
            channel_username TEXT,
            sender_name TEXT,
            msg_date TEXT,
            review_text TEXT,
            reactions_text TEXT,
            source_link TEXT,
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_messages (
            msg_id INTEGER PRIMARY KEY,
            channel TEXT,
            processed_at TEXT
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized at:", DB_PATH)
