"""
VIDYA AI - SQLite Database Manager
Provides local persistent storage for classroom transcripts, offline lesson caching,
and custom village vocabulary.
"""

import sqlite3
import json
import os
import time
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "vidya_classroom.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Live Classroom History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classroom_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        source_text TEXT NOT NULL,
        target_lang TEXT NOT NULL,
        translated_text TEXT NOT NULL,
        pronunciation TEXT,
        session_id TEXT,
        audio_played INTEGER DEFAULT 0
    )
    """)

    # 2. Saved / Offline Lesson Packages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_lessons (
        id TEXT PRIMARY KEY,
        grade TEXT,
        subject TEXT,
        title TEXT,
        content_json TEXT,
        downloaded_at REAL,
        is_offline_ready INTEGER DEFAULT 1
    )
    """)

    # 3. Custom Village / Dialect Vocabulary
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custom_vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_lang TEXT NOT NULL,
        hindi_word TEXT NOT NULL,
        tribal_word TEXT NOT NULL,
        phonetic TEXT,
        village_or_tribe TEXT,
        created_at REAL
    )
    """)

    conn.commit()
    conn.close()


def save_classroom_translation(source_text: str, target_lang: str, translated_text: str, pronunciation: str, session_id: str = "default") -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO classroom_history (timestamp, source_text, target_lang, translated_text, pronunciation, session_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (time.time(), source_text, target_lang, translated_text, pronunciation, session_id))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_recent_classroom_history(limit: int = 25) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM classroom_history ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_custom_vocab(target_lang: str, hindi_word: str, tribal_word: str, phonetic: str = "", village: str = "") -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO custom_vocabulary (target_lang, hindi_word, tribal_word, phonetic, village_or_tribe, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (target_lang, hindi_word, tribal_word, phonetic, village, time.time()))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_custom_vocab(target_lang: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if target_lang:
        cursor.execute("SELECT * FROM custom_vocabulary WHERE target_lang = ?", (target_lang,))
    else:
        cursor.execute("SELECT * FROM custom_vocabulary")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def query_pralekha_sentence(src_text: str, src_lang: str, tgt_lang: str) -> Optional[str]:
    """Look up an exact or prefix parallel sentence pair from Pralekha dataset in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    src_text_clean = src_text.strip().rstrip("। .!?")
    if not src_text_clean:
        conn.close()
        return None
    
    # 1. Try exact match first
    cursor.execute("""
    SELECT tgt_text FROM pralekha_sentence_pairs
    WHERE LOWER(src_lang) = LOWER(?) AND LOWER(tgt_lang) = LOWER(?) AND (src_text = ? OR src_text = ?)
    LIMIT 1
    """, (src_lang, tgt_lang, src_text.strip(), src_text_clean))
    row = cursor.fetchone()
    
    # 2. Try punctuation-insensitive match
    if not row:
        cursor.execute("""
        SELECT tgt_text FROM pralekha_sentence_pairs
        WHERE LOWER(src_lang) = LOWER(?) AND LOWER(tgt_lang) = LOWER(?) AND RTRIM(src_text, '। .!?') = ?
        LIMIT 1
        """, (src_lang, tgt_lang, src_text_clean))
        row = cursor.fetchone()

    # 3. Try prefix / substring match for dataset sentences
    if not row and len(src_text_clean) >= 10:
        like_pattern = src_text_clean[:40] + "%"
        cursor.execute("""
        SELECT tgt_text FROM pralekha_sentence_pairs
        WHERE LOWER(src_lang) = LOWER(?) AND LOWER(tgt_lang) = LOWER(?) AND src_text LIKE ?
        LIMIT 1
        """, (src_lang, tgt_lang, like_pattern))
        row = cursor.fetchone()

    conn.close()
    if row:
        return row["tgt_text"]
    return None


def query_pralekha_word(src_word: str, src_lang: str, tgt_lang: str) -> Optional[str]:
    """Look up a word translation from Pralekha dataset vocabulary in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT tgt_word FROM pralekha_vocabulary
    WHERE LOWER(src_lang) = LOWER(?) AND LOWER(tgt_lang) = LOWER(?) AND src_word = ?
    LIMIT 1
    """, (src_lang, tgt_lang, src_word.strip()))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["tgt_word"]
    return None


def get_pralekha_stats() -> Dict[str, Any]:
    """Get count metrics for Pralekha dataset in SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM pralekha_sentence_pairs")
        total_sentences = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pralekha_vocabulary")
        total_vocab = cursor.fetchone()[0]
    except Exception:
        total_sentences = 0
        total_vocab = 0
    conn.close()
    return {
        "dataset_name": "Pralekha-bucket (srilakshmi-08)",
        "total_parallel_sentences": total_sentences,
        "total_vocabulary_words": total_vocab,
        "is_offline_ready": True
    }


# Initialize on import
init_db()

