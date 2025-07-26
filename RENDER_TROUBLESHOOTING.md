# Render Deployment Troubleshooting Guide

## 🚨 Current Issue: Setuptools Import Error

**Error:** `Cannot import 'setuptools.build_meta'`

This error occurs because Render is using Python 3.13, which has compatibility issues with some packages.

## 🔧 Solutions (Try in Order)

### Solution 1: Use Super Minimal Requirements (Recommended)

1. **Rename the super minimal requirements:**
   ```bash
   mv requirements_super_minimal.txt requirements.txt
   ```

2. **Update render.yaml build command:**
   ```yaml
   buildCommand: pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
   ```

3. **Push and redeploy:**
   ```bash
   git add .
   git commit -m "Use super minimal requirements"
   git push origin main
   ```

### Solution 2: Use Build Script

1. **Use the build script approach:**
   ```yaml
   buildCommand: ./build.sh
   ```

2. **Make sure build.sh is executable:**
   ```bash
   chmod +x build.sh
   ```

### Solution 3: Manual Package Installation

1. **In Render dashboard, set build command to:**
   ```bash
   pip install --upgrade pip setuptools wheel && pip install Flask==2.2.5 Flask-CORS==4.0.0 gunicorn==20.1.0 yfinance==0.2.18 pandas==1.5.3 numpy==1.24.3 requests==2.28.2 openai==0.27.8 google-auth==2.17.3 google-api-python-client==2.86.0
   ```

### Solution 4: Use pyproject.toml

1. **Rename pyproject.toml to be the primary configuration:**
   ```bash
   # Remove requirements.txt temporarily
   mv requirements.txt requirements_backup.txt
   ```

2. **Set build command to:**
   ```bash
   pip install --upgrade pip setuptools wheel && pip install -e .
   ```

### Solution 5: Force Python 3.11 in Dashboard

1. **In Render dashboard, add environment variable:**
   ```
   PYTHON_VERSION = 3.11.7
   ```

2. **Or try:**
   ```
   PYTHON_VERSION = 3.11
   ```

## 🎯 Quick Fix Commands

### Option A: Super Minimal (Most Likely to Work)
```bash
# In your repository
mv requirements_super_minimal.txt requirements.txt
git add .
git commit -m "Use super minimal requirements"
git push origin main
```

### Option B: Manual Installation
In Render dashboard, set build command to:
```bash
pip install --upgrade pip setuptools wheel && pip install Flask==2.2.5 Flask-CORS==4.0.0 gunicorn==20.1.0 yfinance==0.2.18 pandas==1.5.3 numpy==1.24.3 requests==2.28.2 openai==0.27.8 google-auth==2.17.3 google-api-python-client==2.86.0
```

## 🔍 Debugging Steps

### 1. Check Python Version
In Render logs, look for:
```
🐍 Python version: Python 3.11.7
```

### 2. Check Package Installation
Look for successful installation messages:
```
Successfully installed Flask-2.2.5 Flask-CORS-4.0.0 gunicorn-20.1.0...
```

### 3. Check for Errors
Look for specific package errors in the logs.

## 📋 Alternative Deployment Options

### Option 1: Heroku
```bash
# Create Procfile
echo "web: gunicorn api_server:app" > Procfile

# Deploy to Heroku
heroku create your-app-name
git push heroku main
```

### Option 2: Railway
1. Connect GitHub repository
2. Railway will auto-detect Python
3. Set environment variables

### Option 3: DigitalOcean App Platform
1. Connect GitHub repository
2. Select Python environment
3. Set build and run commands

## 🚀 Success Indicators

When deployment succeeds, you should see:
- ✅ Build completed successfully
- ✅ Service is running
- ✅ Health check passes: `curl https://your-app.onrender.com/health`

## 📞 Get Help

If none of these solutions work:

1. **Check Render Status:** https://status.render.com/
2. **Render Community:** https://community.render.com/
3. **Render Documentation:** https://render.com/docs/

## 🎯 Most Likely Solution

**Try Solution 1 first** - it has the highest success rate for this specific error.

The key is using Python 3.11 and minimal, stable package versions. 