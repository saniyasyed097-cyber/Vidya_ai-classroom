"""
Automated Test Suite for VIDYA AI Backend
Verifies:
1. Health check & language configurations (Fixed Hindi source)
2. Live translation API (Hindi -> Gondi, Santhali, Bhili, Telugu)
3. Live document translation (/api/translate/file)
4. Automated worksheet generation
5. Curriculum lessons API
"""

import sys
import os
from fastapi.testclient import TestClient

# Ensure root is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from backend.app import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Hindi" in data["fixed_source_language"]
    print("✓ Health check test passed.")

def test_languages():
    response = client.get("/api/languages")
    assert response.status_code == 200
    data = response.json()
    assert data["fixed_source"]["code"] == "hi"
    assert data["fixed_source"]["is_fixed"] is True
    assert "gondi" in data["targets"]
    assert "santhali" in data["targets"]
    print("✓ Fixed Hindi & Tribal languages check passed.")

def test_translation():
    payload = {
        "text": "पौधों को पानी चाहिए।",
        "source_language": "hi",
        "target_language": "gondi"
    }
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["source_language"] == "hi"
    assert data["target_language"] == "gondi"
    assert len(data["translated_text"]) > 0
    assert "pronunciation" in data
    print(f"✓ Translation test passed: '{data['source_text']}' -> '{data['translated_text']}' ({data['pronunciation']})")

def test_file_translation():
    sample_text = "पौधों को बढ़ने के लिए पानी और सूर्य का प्रकाश चाहिए। पौधे हमारे मित्र हैं।"
    files = {
        "file": ("test_lesson.txt", sample_text.encode("utf-8"), "text/plain")
    }
    data = {"target_language": "gondi"}
    response = client.post("/api/translate/file", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["total_segments"] >= 1
    assert "worksheet" in res_data
    assert "match_words" in res_data["worksheet"]
    print(f"✓ File live translation passed: {res_data['total_segments']} segments, worksheet generated.")

def test_curriculum_lessons():
    response = client.get("/api/lessons")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 4
    first_lesson = data["lessons"][0]
    assert "Class 3" in first_lesson["grade"]
    assert "flashcards" in first_lesson
    print(f"✓ Curriculum lessons passed: {data['total']} lessons loaded.")

def test_pralekha_dataset():
    response = client.get("/api/pralekha/stats")
    assert response.status_code == 200
    data = response.json()
    assert "Pralekha" in data["dataset_name"]
    assert data["is_offline_ready"] is True
    print(f"✓ Pralekha HF Offline Dataset test passed: {data['total_parallel_sentences']} parallel sentences in SQLite.")

if __name__ == "__main__":
    print("\n--- Running VIDYA AI Test Suite ---")
    test_health()
    test_languages()
    test_translation()
    test_file_translation()
    test_curriculum_lessons()
    test_pralekha_dataset()
    print("\n🎉 ALL 6 TEST SUITES PASSED PERFECTLY!\n")

