#!/bin/bash

# Docker Setup for Multi-Agent Collaboration POC
# This script sets up and runs the POC system using Docker Compose

echo "🐳 Setting up Multi-Agent Collaboration POC with Docker"
echo "======================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/{main,consensus,staging,quarantine}
mkdir -p logs reports

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if Fuseki is running
echo "🔍 Checking Fuseki status..."
if curl -f http://localhost:3030/$/ping > /dev/null 2>&1; then
    echo "✅ Fuseki is running at http://localhost:3030"
    echo "   - Admin UI: http://localhost:3030"
    echo "   - SPARQL endpoint: http://localhost:3030/ds"
else
    echo "❌ Fuseki is not responding. Check logs with: docker-compose logs fuseki"
fi

# Check if Gateway is running
echo "🔍 Checking Gateway status..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Gateway is running at http://localhost:8000"
    echo "   - API docs: http://localhost:8000/docs"
    echo "   - Health check: http://localhost:8000/health"
else
    echo "❌ Gateway is not responding. Check logs with: docker-compose logs gateway"
fi

echo ""
echo "🎉 POC System is running!"
echo "========================="
echo ""
echo "Services:"
echo "  - Fuseki (SPARQL server): http://localhost:3030"
echo "  - Gateway API: http://localhost:8000"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart: docker-compose restart"
echo "  - Rebuild: docker-compose up --build"
echo ""
echo "To run the demo:"
echo "  python simple_demo.py"
