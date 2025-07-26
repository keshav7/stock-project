# 🚀 Quick Render Deployment Guide

## 📋 Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **API Keys** - Already configured in the code

## ⚡ 5-Minute Deployment

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Deploy on Render

1. **Go to [Render Dashboard](https://dashboard.render.com/)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure:**

   **Basic Settings:**
   - **Name:** `stock-prediction-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn api_server:app`

   **Environment Variables:**
   ```
   NEWS_API_KEY = a9ce32b4eece45cdad109310c59be10d
   OPENAI_API_KEY = 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
   ```

5. **Click "Create Web Service"**

### Step 3: Wait for Deployment
- Build takes 2-3 minutes
- Service will be available at: `https://your-app-name.onrender.com`

## 🧪 Test Your Deployment

1. **Update the URL in `test_deployment.py`:**
   ```python
   BASE_URL = "https://your-app-name.onrender.com"
   ```

2. **Run the test:**
   ```bash
   python3 test_deployment.py
   ```

## 🌐 API Endpoints

Your deployed API will have these endpoints:

- `GET /` - API information
- `POST /predict` - Generate stock predictions
- `POST /evaluate` - Evaluate predictions
- `GET /predictions/{date}` - Get predictions
- `GET /evaluations/{date}` - Get evaluations
- `GET /status` - API status
- `GET /health` - Health check

## 📧 Email Integration

The API automatically sends emails to `gupkes@gmail.com` when:
- Predictions are generated
- Evaluations are completed

## 🔧 Customization

### Change Email Recipient:
```bash
curl -X POST https://your-app-name.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'
```

### Test from Command Line:
```bash
# Generate predictions
curl -X POST https://your-app-name.onrender.com/predict

# Check status
curl https://your-app-name.onrender.com/status

# Get today's predictions
curl https://your-app-name.onrender.com/predictions/$(date +%Y%m%d)
```

## 🚨 Troubleshooting

### Common Issues:

1. **Build Fails:**
   - Check `requirements.txt` is complete
   - Verify all Python files are in repository

2. **Runtime Errors:**
   - Check Render logs in dashboard
   - Verify environment variables are set

3. **Timeout Issues:**
   - Free tier has 30-second timeout
   - Predictions run asynchronously

### Get Help:
- [Render Documentation](https://render.com/docs)
- [Full Deployment Guide](RENDER_DEPLOYMENT.md)
- [API Documentation](API_DOCUMENTATION.md)

## 🎉 Success!

Once deployed, your API will be:
- ✅ **Publicly accessible** via HTTPS
- ✅ **Automatically scaled** by Render
- ✅ **Monitored** with built-in logging
- ✅ **Secure** with environment variables
- ✅ **Reliable** with automatic restarts

**Your Stock Prediction API is now live! 🚀** 