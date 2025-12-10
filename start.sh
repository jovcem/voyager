#!/bin/bash
# Simple fallback script for starting all services
# For VS Code users: Use "Tasks: Run Task" -> "Start All Services" instead

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 Starting Voyager services..."
echo ""
echo "Note: If you're using VS Code, you can use the built-in tasks:"
echo "  Press Cmd+Shift+P → 'Tasks: Run Task' → 'Start All Services'"
echo ""

# Run setup
"$PROJECT_DIR/scripts/setup.sh"

# Start API in background
echo "🔧 Starting Python API..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate
python run_api.py &
API_PID=$!
echo "✓ Python API started (PID: $API_PID)"
echo ""

# Start web app in background
echo "🌐 Starting Web App..."
cd "$PROJECT_DIR/web"
npm run dev &
WEB_PID=$!
echo "✓ Web App started (PID: $WEB_PID)"
echo ""

echo "✅ All services started!"
echo ""
echo "📍 Service Status:"
echo "   • PostgreSQL: Running in Docker (background)"
echo "   • Python API: Running (PID: $API_PID) → http://localhost:8000"
echo "   • Web App: Running (PID: $WEB_PID)"
echo ""
echo "🛑 To stop all services:"
echo "   kill $API_PID $WEB_PID"
echo "   cd backend && docker-compose down"
echo ""
echo "Press Ctrl+C to stop this script (services will keep running)"
echo ""

# Wait for any process to exit
wait
