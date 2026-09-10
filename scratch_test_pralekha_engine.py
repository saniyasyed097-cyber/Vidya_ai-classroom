import sys
import sqlite3
sys.stdout.reconfigure(encoding='utf-8')

from backend.translation_engine import translation_engine

conn = sqlite3.connect("backend/vidya_classroom.db")
cursor = conn.cursor()
cursor.execute("SELECT src_text, tgt_text FROM pralekha_sentence_pairs WHERE src_lang='hindi' AND tgt_lang='telugu' AND LENGTH(src_text) < 100 LIMIT 1")
row = cursor.fetchone()
conn.close()

if row:
    hi_text, expected_te = row
    print("DB Hindi Text:", hi_text)
    print("Expected Telugu:", expected_te)
    
    res = translation_engine.translate_sentence(hi_text, "telugu")
    print("Engine Translated Text:", res["translated_text"])
    print("Engine Used:", res["engine"])
else:
    print("No short sentence row found in DB")
