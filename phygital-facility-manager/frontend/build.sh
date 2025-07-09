#!/bin/bash

# Frontend Build Script for Render Deployment

echo "🚀 Starting frontend build for Render deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the application
echo "🔨 Building application..."
npm run build

# Verify build output
if [ -d "dist" ]; then
    echo "✅ Build successful! Output directory 'dist' created."
    echo "📁 Build contents:"
    ls -la dist/
else
    echo "❌ Build failed! No 'dist' directory found."
    exit 1
fi

echo "🎉 Frontend build completed successfully!"
