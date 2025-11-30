#!/bin/bash

# setup.sh - Start Docker containers for iRacing Telemetry API

set -e  # Exit on error

echo "🚀 Starting iRacing Telemetry API with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📝 Creating .env file from .env.example..."
        cp .env.example .env
        echo "⚠️  Please update .env with your OAuth credentials before using authentication features."
    else
        echo "⚠️  No .env or .env.example file found. Proceeding with default environment variables."
    fi
fi

# Build and start containers
echo "🔨 Building and starting Docker containers..."
docker compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker compose ps | grep -q "Up"; then
    echo "✅ Docker containers are running!"
    echo ""
    echo "📊 Service Status:"
    docker compose ps
    echo ""
    echo "🌐 API is available at: http://localhost"
    echo "🗄️  MySQL is available at: localhost:3306"
    echo "🐛 Python debugger port: 5678"
    echo ""
    echo "📚 View logs with: docker compose logs -f"
    echo "🛑 Stop services with: docker compose down"
else
    echo "❌ Error: Failed to start Docker containers"
    echo "Check logs with: docker compose logs"
    exit 1
fi
