#!/bin/bash

# Stock Prediction API - Render Deployment Script

echo "🚀 Preparing Stock Prediction API for Render deployment..."

# Check if we're in the right directory
if [ ! -f "api_server.py" ]; then
    echo "❌ Error: api_server.py not found. Please run this script from the project root."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p predictions
mkdir -p evaluations
mkdir -p logs

# Ensure files have correct permissions
echo "🔐 Setting file permissions..."
chmod +x api_server.py
chmod +x morning_prediction.py
chmod +x evening_evaluation.py

# Create a .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log

# Data files
predictions/
evaluations/
*.csv
*.json
!requirements*.json

# API keys and tokens
token.pickle
*.pem
*.key

# Environment variables
.env
.env.local
.env.production

# Temporary files
*.tmp
*.temp
EOF
fi

# Check if all required files exist
echo "✅ Checking required files..."
required_files=(
    "api_server.py"
    "requirements.txt"
    "runtime.txt"
    "render.yaml"
    "data_fetcher.py"
    "technical_analyzer.py"
    "news_analyzer.py"
    "email_sender.py"
    "morning_prediction.py"
    "evening_evaluation.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
    fi
done

echo ""
echo "🎯 Deployment Preparation Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Push to GitHub:"
echo "   git add ."
echo "   git commit -m 'Ready for Render deployment'"
echo "   git push origin main"
echo ""
echo "2. Deploy on Render:"
echo "   - Go to https://dashboard.render.com/"
echo "   - Click 'New +' → 'Web Service'"
echo "   - Connect your GitHub repository"
echo "   - Use these settings:"
echo "     * Build Command: pip install -r requirements.txt"
echo "     * Start Command: gunicorn api_server:app"
echo "     * Environment Variables:"
echo "       - NEWS_API_KEY = a9ce32b4eece45cdad109310c59be10d"
echo "       - OPENAI_API_KEY = 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"
echo ""
echo "3. Test after deployment:"
echo "   python3 test_deployment.py"
echo ""
echo "🚀 Your API will be ready!" 