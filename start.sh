#!/bin/bash

# Activate the virtual environment
source backend/.venv/bin/activate

# Start the backend
echo "Starting backend..."
python backend/app.py &
backend_pid=$!

# Start the frontend
echo "Starting frontend..."
cd frontend/briefbox-front
npm start &
frontend_pid=$!

# Redirect output from backend and frontend to current terminal
tail -f /dev/null --pid=$backend_pid --pid=$frontend_pid