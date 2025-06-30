#!/bin/bash

# Firefly III Quick Setup Script for Phygital Facility Manager
# This script automates the installation of Firefly III for financial management

echo "🏦 Firefly III Setup for Phygital Facility Manager"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker is installed"

# Check if Firefly III is already running
if docker ps | grep -q firefly-iii; then
    echo "⚠️  Firefly III container is already running"
    echo "   Container status:"
    docker ps | grep firefly-iii
    echo ""
    echo "   To access Firefly III: http://localhost:8080"
    exit 0
fi

# Check if container exists but is stopped
if docker ps -a | grep -q firefly-iii; then
    echo "🔄 Found existing Firefly III container. Starting it..."
    docker start firefly-iii
    echo "✅ Firefly III started successfully!"
    echo "   Access it at: http://localhost:8080"
    exit 0
fi

echo "🚀 Installing Firefly III..."

# Generate a random 32-character APP_KEY
APP_KEY=$(head /dev/urandom | LC_ALL=C tr -dc 'A-Za-z0-9' | head -c 32)
echo "🔑 Generated APP_KEY: $APP_KEY"

# Create volume for uploads
echo "📁 Creating Docker volume for file uploads..."
docker volume create firefly_iii_upload

# Run Firefly III container
echo "🐳 Starting Firefly III container..."
docker run -d \
  --name firefly-iii \
  -p 8080:8080 \
  -e APP_KEY="$APP_KEY" \
  -e DB_CONNECTION=sqlite \
  -e APP_URL=http://localhost:8080 \
  -v firefly_iii_upload:/var/www/html/storage/upload \
  fireflyiii/core:latest

# Wait for container to start
echo "⏳ Waiting for Firefly III to start..."
sleep 10

# Check if container is running
if docker ps | grep -q firefly-iii; then
    echo "✅ Firefly III is now running!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Open Firefly III: http://localhost:8080"
    echo "2. Complete the initial setup wizard"
    echo "3. Create your admin account"
    echo "4. Go to Profile → OAuth → Personal Access Tokens"
    echo "5. Create a new token named 'Facility Manager Integration'"
    echo "6. Copy the token and add it to your .env file:"
    echo "   FIREFLY_BASE_URL=http://localhost:8080"
    echo "   FIREFLY_API_TOKEN=your_very_long_token_here"
    echo "7. Restart your facility manager application"
    echo ""
    echo "🎉 Setup complete! Your Financial Dashboard will be ready after token configuration."
else
    echo "❌ Failed to start Firefly III container"
    echo "   Check Docker logs: docker logs firefly-iii"
    exit 1
fi
