Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "       VIDYA AI - Mother Tongue Classroom Web App" -ForegroundColor Green
Write-Host "       Fixed Source Language: Hindi (हिन्दी)" -ForegroundColor Yellow
Write-Host "       Target Languages: Gondi, Santhali, Bhili, Telugu" -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Launching web browser and starting FastAPI server on http://localhost:8000..." -ForegroundColor Green
Start-Process "http://localhost:8000"
py -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
