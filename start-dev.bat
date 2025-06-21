@echo off
echo Starting StudyBuddy Development Environment...
echo.

echo Starting Backend Server...
cd backend
start "StudyBuddy Backend" cmd /k "python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Starting Frontend Server...
cd ..\frontend
start "StudyBuddy Frontend" cmd /k "npm install && npm run dev"

echo.
echo Development servers are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:3000
echo.
echo Press any key to exit this script...
pause > nul 