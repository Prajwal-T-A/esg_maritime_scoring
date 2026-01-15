#!/bin/bash

# Maritime ESG Analytics - Quick Start Script
# Starts both backend and frontend servers

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PATH="$PROJECT_DIR/.venv/bin"

echo "════════════════════════════════════════════════════════════════"
echo "  Maritime ESG Analytics - Quick Start"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv "$PROJECT_DIR/.venv"
    echo "✅ Virtual environment created"
fi

echo "🚀 Starting Maritime ESG Analytics Platform..."
echo ""

# Start Backend
echo "📱 Starting Backend Server (Port 8000)..."
cd "$PROJECT_DIR"
$VENV_PATH/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 3
echo "   Backend PID: $BACKEND_PID"
echo "   📖 Swagger Docs: http://localhost:8000/docs"
echo ""

# Start Frontend
echo "⚛️  Starting Frontend Server (Port 3000)..."
cd "$PROJECT_DIR/frontend"
npm start &
FRONTEND_PID=$!
sleep 5
echo "   Frontend PID: $FRONTEND_PID"
echo "   🌐 App URL: http://localhost:3000"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ Services Started Successfully!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Docs:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait
