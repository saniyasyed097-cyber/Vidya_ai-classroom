"""
VIDYA AI - FastAPI Backend Server
Provides API endpoints for live speech translation, live file translation,
curriculum lessons, automated bilingual worksheets, and static PWA hosting.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.translation_engine import translation_engine, LANGUAGES
from backend.document_processor import document_processor
from backend.curriculum_data import CURRICULUM_LESSONS
from backend.database import (
    save_classroom_translation,
    get_recent_classroom_history,
    save_custom_vocab,
    get_custom_vocab,
    get_pralekha_stats
)

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("vidya_ai")

# Initialize FastAPI App
app = FastAPI(
    title="VIDYA AI - Mother Tongue Learning API",
    description="Classroom translation and bilingual curriculum generator for Hindi -> Tribal Languages",
    version="1.0.0"
)

# Enable CORS for cross-origin or local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class TranslateRequest(BaseModel):
    text: str
    source_language: str = "hi"  # Fixed to Hindi as specified
    target_language: str = "gondi"
    session_id: Optional[str] = "classroom_live"

class WorksheetRequest(BaseModel):
    text: str
    target_language: str = "gondi"
    lesson_title: Optional[str] = "कक्षा अभ्यास पत्र"

class CustomVocabRequest(BaseModel):
    target_language: str
    hindi_word: str
    tribal_word: str
    phonetic: Optional[str] = ""
    village: Optional[str] = ""


# --- API Routes ---

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "VIDYA AI - Mother Tongue Learning",
        "version": "1.0.0",
        "fixed_source_language": "hi (Hindi)",
        "supported_target_languages": list(LANGUAGES.keys()),
        "offline_ready": True
    }


@app.get("/api/languages")
async def list_languages():
    """
    Returns supported tribal and regional target languages with dialects and script info.
    """
    return {
        "fixed_source": {
            "code": "hi",
            "name": "Hindi",
            "native_name": "हिन्दी",
            "is_fixed": True,
            "badge": "Fixed Source Language"
        },
        "targets": LANGUAGES
    }


@app.post("/api/translate")
async def translate_text(req: TranslateRequest):
    """
    Translates teacher Hindi speech/text into the selected tribal mother tongue.
    Matches the exact API contract requested:
    POST /translate { "text": "...", "source_language": "hi", "target_language": "..." }
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    # Source language is fixed to Hindi
    result = translation_engine.translate_sentence(req.text, req.target_language)
    
    # Save to classroom history
    try:
        save_classroom_translation(
            source_text=result["source_text"],
            target_lang=result["target_lang"],
            translated_text=result["translated_text"],
            pronunciation=result.get("pronunciation", ""),
            session_id=req.session_id or "default"
        )
    except Exception as e:
        logger.warning(f"Failed to record history: {e}")

    return {
        "source_text": result["source_text"],
        "source_language": "hi",
        "target_language": result["target_lang"],
        "translated_text": result["translated_text"],
        "pronunciation": result.get("pronunciation", ""),
        "confidence": result.get("confidence", 0.95),
        "engine": result.get("engine", "lexicon_rules"),
        "vocabulary_highlight": result.get("vocabulary_highlight", [])
    }


@app.post("/api/translate/file")
async def translate_file(
    file: UploadFile = File(...),
    target_language: str = Form("gondi")
):
    """
    Live Document Translation Endpoint:
    Accepts PDF, DOCX, or TXT file, extracts Hindi content, segments it,
    translates segment-by-segment live, and auto-generates a bilingual classroom worksheet!
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    content_bytes = await file.read()
    if len(content_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 1. Extract text from uploaded document
    try:
        raw_text = document_processor.extract_text_from_bytes(content_bytes, file.filename)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"File parsing error: {str(e)}")

    # 2. Segment text into classroom sentences
    sentences = document_processor.segment_into_sentences(raw_text)
    if not sentences:
        # Fallback to lines
        sentences = [line.strip() for line in raw_text.split("\n") if len(line.strip()) > 3]

    if not sentences:
        raise HTTPException(status_code=422, detail="No readable Hindi text sentences found in file.")

    # Translate the COMPLETE document without truncation
    segmented_sentences = sentences

    # 3. Live batch translation
    translated_segments = translation_engine.translate_document_segments(segmented_sentences, target_language)

    # 4. Generate automated bilingual worksheet from file content
    target_info = LANGUAGES.get(target_language, {"name": target_language.capitalize()})
    worksheet = document_processor.generate_worksheet_from_segments(translated_segments, target_info.get("name", "Tribal"))

    full_source = "\n\n".join([s["source_text"] for s in translated_segments])
    full_target = "\n\n".join([s["translated_text"] for s in translated_segments])

    return {
        "filename": file.filename,
        "file_size": len(content_bytes),
        "target_language": target_language,
        "total_segments": len(translated_segments),
        "segments": translated_segments,
        "worksheet": worksheet,
        "full_source_text": full_source,
        "full_translated_text": full_target
    }


@app.get("/api/lessons")
async def get_lessons():
    """
    Returns curated bilingual classroom lessons (Classes 1-5 & FLN).
    """
    return {
        "lessons": CURRICULUM_LESSONS,
        "total": len(CURRICULUM_LESSONS)
    }


@app.get("/api/lessons/{lesson_id}")
async def get_single_lesson(lesson_id: str):
    for lesson in CURRICULUM_LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
    raise HTTPException(status_code=404, detail="Lesson not found.")


@app.post("/api/worksheets/generate")
async def generate_worksheet(req: WorksheetRequest):
    """
    Generates an automated bilingual worksheet from arbitrary Hindi educational text.
    """
    sentences = document_processor.segment_into_sentences(req.text)
    if not sentences:
        sentences = [req.text.strip()]

    translated_segments = translation_engine.translate_document_segments(sentences, req.target_language)
    target_info = LANGUAGES.get(req.target_language, {"name": req.target_language.capitalize()})
    worksheet = document_processor.generate_worksheet_from_segments(translated_segments, target_info.get("name", "Tribal"))
    worksheet["lesson_title"] = req.lesson_title

    return worksheet


@app.get("/api/history")
async def get_history():
    """
    Returns recent live classroom translations for transcripts and logs.
    """
    history = get_recent_classroom_history(30)
    return {"history": history}


@app.post("/api/vocabulary/custom")
async def add_custom_word(req: CustomVocabRequest):
    """
    Allows teachers to add tribal dialect words specific to their local village/tribe.
    """
    new_id = save_custom_vocab(
        target_lang=req.target_language,
        hindi_word=req.hindi_word,
        tribal_word=req.tribal_word,
        phonetic=req.phonetic or "",
        village=req.village or ""
    )
    return {"status": "saved", "id": new_id}


@app.get("/api/vocabulary/custom")
async def list_custom_words(target_language: Optional[str] = None):
    words = get_custom_vocab(target_language)
    return {"words": words}


@app.get("/api/pralekha/stats")
async def pralekha_dataset_stats():
    """
    Returns metrics and offline database metrics for the HuggingFace Pralekha dataset.
    """
    return get_pralekha_stats()


# Mount Static Files (Frontend PWA)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    # Fallback to serve assets like manifest.json, sw.js, css, js directly
    @app.get("/{full_path:path}")
    async def serve_frontend_assets(full_path: str):
        asset_path = os.path.join(FRONTEND_DIR, full_path)
        if os.path.exists(asset_path) and os.path.isfile(asset_path):
            return FileResponse(asset_path)
        # Default to index.html for client-side routing
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
