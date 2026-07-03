#!/bin/bash
# Quick start script for the ATM FSM demo

echo "========================================="
echo "ATM FSM - Backend + Frontend Setup"
echo "========================================="
echo ""

# Check dependencies
echo "[1/3] Checking dependencies..."
if ! python3 -c "import flask, flask_cors" 2>/dev/null; then
  echo "Installing Flask and flask-cors..."
  pip install -q flask flask-cors
fi
echo "✓ Dependencies ready"
echo ""

# Start backend
echo "[2/3] Starting Flask backend on port 5000..."
python3 app.py &
BACKEND_PID=$!
sleep 2
echo "✓ Backend running (PID: $BACKEND_PID)"
echo ""

# Start frontend server
echo "[3/3] Starting static file server on port 8000..."
python3 -m http.server 8000 &
FRONTEND_PID=$!
sleep 1
echo "✓ Frontend running (PID: $FRONTEND_PID)"
echo ""

echo "========================================="
echo "✓ Setup complete!"
echo "========================================="
echo ""
echo "Open your browser to: http://127.0.0.1:8000"
echo ""
echo "Demo credentials:"
echo "  Account: 1234"
echo "  PIN:     9"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait
