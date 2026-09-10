@echo off
title VIDYA AI - Mother Tongue Learning
echo =======================================================
echo        VIDYA AI - Mother Tongue Classroom Web App
echo        Fixed Source Language: Hindi (हिन्दी)
echo        Target Languages: Gondi, Santhali, Bhili, Telugu
echo =======================================================
echo.
echo Starting FastAPI Backend Server on http://localhost:8000...
echo.

start "" "http://localhost:8000"
py -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
pause
