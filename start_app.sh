#!/bin/bash

# Start the backend server
echo "Starting backend server..."
cd backend
echo "Creating virtual environment if it doesn't exist..."
python -m venv venv
source venv/bin/activate
echo "Installing backend dependencies..."
pip install -r requirements.txt
echo "Initializing database..."
python init_db.py
echo "Starting Flask server..."
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to initialize
echo "Waiting for backend to initialize..."
sleep 5

# Start the frontend development server
echo "Starting frontend development server..."
cd frontend
echo "Installing frontend dependencies..."
npm install
echo "Starting Vite dev server..."
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Both servers are now running!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers."

# Handle graceful shutdown
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM EXIT

# Keep script running
wait
