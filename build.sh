#!/bin/bash

# Stock Prediction API - Build Script for Render
# This script ensures Python 3.11 is used and packages are installed safely

echo "🚀 Starting build process for Stock Prediction API..."

# Check Python version
echo "🐍 Checking Python version..."
python3 --version

# Upgrade pip and setuptools first
echo "📦 Upgrading pip and setuptools..."
python3 -m pip install --upgrade pip setuptools wheel

# Install packages one by one to identify any issues
echo "📦 Installing packages..."

# Core Flask dependencies
echo "  Installing Flask..."
python3 -m pip install Flask==2.2.5
python3 -m pip install Flask-CORS==4.0.0
python3 -m pip install gunicorn==20.1.0

# Data processing
echo "  Installing data processing packages..."
python3 -m pip install pandas==1.5.3
python3 -m pip install numpy==1.24.3
python3 -m pip install yfinance==0.2.18

# HTTP and API
echo "  Installing HTTP packages..."
python3 -m pip install requests==2.28.2
python3 -m pip install aiohttp==3.8.5

# AI and OpenAI
echo "  Installing AI packages..."
python3 -m pip install openai==0.27.8

# Google APIs
echo "  Installing Google API packages..."
python3 -m pip install google-auth==2.17.3
python3 -m pip install google-api-python-client==2.86.0

echo "✅ Build completed successfully!"
echo "🐍 Python version: $(python3 --version)"
echo "📦 Installed packages:"
python3 -m pip list 