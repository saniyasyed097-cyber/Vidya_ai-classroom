"""
VIDYA AI - Pralekha Offline Dataset Database Builder
Downloads & processes parallel corpora from HuggingFace Bucket 'srilakshmi-08/Pralekha-bucket'
Builds offline SQLite database tables in backend/vidya_classroom.db
"""

import os
import sys
import sqlite3
import urllib.request
import time
import pandas as pd

# Fix Windows console UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = os.path.join(os.path.dirname(__file__), "vidya_classroom.db")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset_cache")
HF_BASE_URL = "https://huggingface.co/buckets/srilakshmi-08/Pralekha-bucket/resolve/"

FILES_TO_PROCESS = [
    ("dev/eng_hin-00000-of-00001.parquet", "dev_eng_hin.parquet"),
    ("dev/eng_tel-00000-of-00001.parquet", "dev_eng_tel.parquet"),
    ("test/eng_hin-00000-of-00001.parquet", "test_eng_hin.parquet"),
    ("test/eng_tel-00000-of-00001.parquet", "test_eng_tel.parquet"),
]

def init_pralekha_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pralekha_sentence_pairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        src_lang TEXT NOT NULL,
        tgt_lang TEXT NOT NULL,
        src_text TEXT NOT NULL,
        tgt_text TEXT NOT NULL,
        split_name TEXT DEFAULT 'pralekha',
        created_at REAL
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pralekha_lookup ON pralekha_sentence_pairs(src_lang, tgt_lang, src_text)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pralekha_vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        src_lang TEXT NOT NULL,
        tgt_lang TEXT NOT NULL,
        src_word TEXT NOT NULL,
        tgt_word TEXT NOT NULL,
        frequency INTEGER DEFAULT 1
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vocab_lookup ON pralekha_vocabulary(src_lang, tgt_lang, src_word)")

    conn.commit()
    conn.close()

def download_file(rel_path, target_filename):
    os.makedirs(CACHE_DIR, exist_ok=True)
    local_path = os.path.join(CACHE_DIR, target_filename)
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        print(f"✓ Found cached file: {target_filename} ({os.path.getsize(local_path)} bytes)", flush=True)
        return local_path

    url = HF_BASE_URL + rel_path
    print(f"↓ Downloading from HuggingFace Bucket: {rel_path} ...", flush=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
        with open(local_path, "wb") as f:
            f.write(data)
    print(f"✓ Saved {local_path} ({len(data)} bytes)", flush=True)
    return local_path

def build_pralekha_database():
    print("=" * 60, flush=True)
    print("  VIDYA AI - Building Pralekha Offline Dataset Database", flush=True)
    print("=" * 60, flush=True)

    init_pralekha_tables()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing pralekha data before rebuild
    cursor.execute("DELETE FROM pralekha_sentence_pairs")
    cursor.execute("DELETE FROM pralekha_vocabulary")
    conn.commit()

    total_pairs = 0
    now = time.time()

    # Process pairs
    for rel_path, fname in FILES_TO_PROCESS:
        try:
            local_path = download_file(rel_path, fname)
            df = pd.read_parquet(local_path)
            split_tag = "dev" if "dev" in fname else "test"
            
            # Identify languages
            if "eng_hin" in fname:
                rows_to_insert = []
                for _, r in df.iterrows():
                    rows_to_insert.append(('english', 'hindi', str(r['src_txt']).strip(), str(r['tgt_txt']).strip(), split_tag, now))
                    rows_to_insert.append(('hindi', 'english', str(r['tgt_txt']).strip(), str(r['src_txt']).strip(), split_tag, now))
                cursor.executemany("""
                INSERT INTO pralekha_sentence_pairs (src_lang, tgt_lang, src_text, tgt_text, split_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, rows_to_insert)
                total_pairs += len(rows_to_insert)
                print(f"  + Added {len(rows_to_insert)} English-Hindi sentence pairs ({split_tag})")

            elif "eng_tel" in fname:
                rows_to_insert = []
                for _, r in df.iterrows():
                    rows_to_insert.append(('english', 'telugu', str(r['src_txt']).strip(), str(r['tgt_txt']).strip(), split_tag, now))
                    rows_to_insert.append(('telugu', 'english', str(r['tgt_txt']).strip(), str(r['src_txt']).strip(), split_tag, now))
                cursor.executemany("""
                INSERT INTO pralekha_sentence_pairs (src_lang, tgt_lang, src_text, tgt_text, split_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, rows_to_insert)
                total_pairs += len(rows_to_insert)
                print(f"  + Added {len(rows_to_insert)} English-Telugu sentence pairs ({split_tag})")

        except Exception as e:
            print(f"⚠️ Error processing {fname}: {e}")

    # Build direct Hindi <-> Telugu parallel pairs by joining dev & test English pivot
    print("\n🔗 Aligning Hindi <-> Telugu parallel sentence pairs using Pralekha corpus...")
    try:
        dev_hin_path = os.path.join(CACHE_DIR, "dev_eng_hin.parquet")
        dev_tel_path = os.path.join(CACHE_DIR, "dev_eng_tel.parquet")
        if os.path.exists(dev_hin_path) and os.path.exists(dev_tel_path):
            df_hin = pd.read_parquet(dev_hin_path)
            df_tel = pd.read_parquet(dev_tel_path)
            merged = pd.merge(df_hin, df_tel, on='src_txt', suffixes=('_hin', '_tel'))
            
            hi_te_pairs = []
            for _, r in merged.iterrows():
                hi_text = str(r['tgt_txt_hin']).strip()
                te_text = str(r['tgt_txt_tel']).strip()
                if hi_text and te_text:
                    hi_te_pairs.append(('hindi', 'telugu', hi_text, te_text, 'pralekha_aligned', now))
                    hi_te_pairs.append(('telugu', 'hindi', te_text, hi_text, 'pralekha_aligned', now))

            cursor.executemany("""
            INSERT INTO pralekha_sentence_pairs (src_lang, tgt_lang, src_text, tgt_text, split_name, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, hi_te_pairs)
            total_pairs += len(hi_te_pairs)
            print(f"  + Added {len(hi_te_pairs)} direct Hindi <-> Telugu aligned sentence pairs!")

    except Exception as e:
        print(f"⚠️ Error aligning Hindi-Telugu: {e}")

    conn.commit()

    # Populate vocabulary table
    cursor.execute("SELECT COUNT(*) FROM pralekha_sentence_pairs")
    final_count = cursor.fetchone()[0]
    conn.close()

    print("\n" + "=" * 60)
    print(f"🎉 Pralekha Offline Dataset Database successfully built!")
    print(f"📊 Total parallel sentence entries in SQLite: {final_count}")
    print(f"📁 SQLite DB Path: {DB_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    build_pralekha_database()
