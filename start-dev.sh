#!/bin/bash

echo "Starting StudyBuddy Development Environment..."
echo

echo "Starting Backend Server..."
cd backend
gnome-terminal --title="StudyBuddy Backend" -- bash -c "python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; exec bash" &

echo
echo "Starting Frontend Server..."
cd ../frontend
gnome-terminal --title="StudyBuddy Frontend" -- bash -c "npm install && npm run dev; exec bash" &

echo
echo "Development servers are starting..."
echo "Backend will be available at: http://localhost:8000"
echo "Frontend will be available at: http://localhost:3000"
echo
echo "Press Ctrl+C to stop all servers"
wait 