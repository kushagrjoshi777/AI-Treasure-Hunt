@echo off
setlocal
echo Starting AI Treasure Hunt Web Server...
set PORT=5000
start "" "http://localhost:%PORT%"
python web/app.py
pause
