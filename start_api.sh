#!/bin/bash

# Stock Prediction API Startup Script

echo "🚀 Starting Stock Prediction API Server..."

# Check if API server is already running
if pgrep -f "api_server.py" > /dev/null; then
    echo "⚠️  API server is already running!"
    echo "To stop it, run: pkill -f api_server.py"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the API server with logging
echo "📝 Logs will be saved to: logs/api_server.log"
echo "🌐 API will be available at: http://localhost:5000"
echo "📖 API Documentation: http://localhost:5000/"

# Start the server in the background with logging
nohup python3 api_server.py > logs/api_server.log 2>&1 &

# Get the process ID
API_PID=$!

# Wait a moment for the server to start
sleep 2

# Check if the server started successfully
if curl -s http://localhost:5000/ > /dev/null; then
    echo "✅ API server started successfully!"
    echo "🆔 Process ID: $API_PID"
    echo "📊 Check status: curl http://localhost:5000/status"
    echo "🛑 To stop: pkill -f api_server.py"
else
    echo "❌ Failed to start API server"
    echo "📋 Check logs: tail -f logs/api_server.log"
    exit 1
fi

echo ""
echo "🎯 Quick Test Commands:"
echo "  Generate predictions: curl -X POST http://localhost:5000/predict"
echo "  Evaluate predictions: curl -X POST http://localhost:5000/evaluate"
echo "  Get today's predictions: curl http://localhost:5000/predictions/$(date +%Y%m%d)"
echo "  Check status: curl http://localhost:5000/status" 