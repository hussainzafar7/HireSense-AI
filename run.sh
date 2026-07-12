#!/bin/bash
echo "Starting HireSense AI..."
cd backend && source venv/bin/activate && python app.py &
BACKEND=$!
sleep 3
cd frontend && npm start &
FRONTEND=$!
echo ""
echo "==============================="
echo "Frontend: http://localhost:3000"
echo "API:      http://localhost:5000"
echo "==============================="
trap "kill $BACKEND $FRONTEND 2>/dev/null" EXIT
wait
