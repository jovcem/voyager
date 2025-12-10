#!/bin/bash
set -e

echo "🚀 Setting up Voyager services..."
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
if [ ! -d "backend/venv" ]; then
    echo "❌ Error: Virtual environment not found at backend/venv"
    echo "   Please create it first: cd backend && python -m venv venv"
    exit 1
fi

if [ ! -d "web/node_modules" ]; then
    echo "❌ Error: node_modules not found in web/"
    echo "   Please run: cd web && npm install"
    exit 1
fi
echo "✓ Prerequisites check passed"
echo ""

# Start Docker
echo "🐳 Starting Docker services..."
cd backend
docker-compose up -d
echo "✓ Docker services starting"
echo ""

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U voyager_user -d voyager > /dev/null 2>&1; do
    printf "."
    sleep 1
done
echo ""
echo "✓ PostgreSQL is ready!"
echo ""

# Run migrations
echo "📊 Running migrations..."
source venv/bin/activate
python scripts/cli.py migrate up
deactivate
echo ""

echo "✅ Setup complete!"
echo "   You can now start the API and Web app"
echo ""
