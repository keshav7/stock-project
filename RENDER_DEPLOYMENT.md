# Render Deployment Guide for Stock Prediction API

This guide will help you deploy the Stock Prediction API to Render.

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository

Make sure your repository contains these essential files:
- `api_server.py` - Main API server
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration (optional)
- All other Python modules (data_fetcher.py, technical_analyzer.py, etc.)

### 2. Deploy to Render

#### Option A: Using Render Dashboard (Recommended)

1. **Go to [Render Dashboard](https://dashboard.render.com/)**
2. **Click "New +" and select "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**

   **Basic Settings:**
   - **Name:** `stock-prediction-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn api_server:app`

   **Environment Variables:**
   - `NEWS_API_KEY` = `a9ce32b4eece45cdad109310c59be10d`
   - `OPENAI_API_KEY` = `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`
   - `PYTHON_VERSION` = `3.11.7`

5. **Click "Create Web Service"**

#### Option B: Using render.yaml (Blue-Green Deployment)

If you have the `render.yaml` file in your repository:

1. **Go to [Render Dashboard](https://dashboard.render.com/)**
2. **Click "New +" and select "Blueprint"**
3. **Connect your GitHub repository**
4. **Render will automatically detect and use the render.yaml configuration**

## 🔧 Configuration Details

### Environment Variables

The API requires these environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `NEWS_API_KEY` | `a9ce32b4eece45cdad109310c59be10d` | News API key for sentiment analysis |
| `OPENAI_API_KEY` | `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` | OpenAI API key for AI analysis |
| `PYTHON_VERSION` | `3.11.7` | Python version (recommended for compatibility) |
| `PORT` | Auto-assigned by Render | Port for the web service |

### Build Configuration

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn api_server:app
```

**Python Version:** 3.11.7 (recommended for stability)

## 🚨 Troubleshooting

### Common Issues:

#### 1. Setuptools Import Error
**Error:** `Cannot import 'setuptools.build_meta'`

**Solutions:**
1. **Use Python 3.11:** Set `PYTHON_VERSION=3.11.7` in environment variables
2. **Use stable requirements:** Rename `requirements_stable.txt` to `requirements.txt`
3. **Alternative build command:**
   ```bash
   pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
   ```

#### 2. Build Failures
- Check `requirements.txt` is complete
- Verify all Python files are in repository
- Use Python 3.11 instead of 3.13

#### 3. Runtime Errors
- Check Render logs in dashboard
- Verify environment variables are set
- Monitor application logs

#### 4. Memory Issues
- Free tier has 512MB RAM limit
- Consider upgrading to paid plan for more resources
- Optimize memory usage in your application

#### 5. Timeout Issues
- Free tier has 30-second timeout
- Long-running operations should be async
- Consider using background workers for heavy tasks

### Alternative Requirements Files

If you encounter compatibility issues, try these alternatives:

1. **Use stable versions:**
   ```bash
   # Rename requirements_stable.txt to requirements.txt
   mv requirements_stable.txt requirements.txt
   ```

2. **Use minimal requirements:**
   ```bash
   # Create minimal requirements.txt
   echo "Flask==2.2.5
   Flask-CORS==4.0.0
   gunicorn==20.1.0
   yfinance==0.2.18
   pandas==1.5.3
   numpy==1.24.3
   requests==2.28.2
   openai==0.27.8
   google-auth==2.17.3
   google-api-python-client==2.86.0" > requirements.txt
   ```

### Debug Commands:

```bash
# Check if service is running
curl https://your-app-name.onrender.com/health

# Test prediction endpoint
curl -X POST https://your-app-name.onrender.com/predict

# Check API status
curl https://your-app-name.onrender.com/status
```

## 📊 Monitoring and Logs

### View Logs
1. Go to your service in Render Dashboard
2. Click on "Logs" tab
3. Monitor real-time logs for debugging

### Health Check
Your API includes a health check endpoint:
```
GET https://your-app-name.onrender.com/health
```

### Status Monitoring
Check API status:
```
GET https://your-app-name.onrender.com/status
```

## 🌐 API Endpoints

Once deployed, your API will be available at:
`https://your-app-name.onrender.com`

### Available Endpoints:
- `GET /` - API information
- `POST /predict` - Generate predictions
- `POST /evaluate` - Evaluate predictions
- `GET /predictions/{date}` - Get predictions
- `GET /evaluations/{date}` - Get evaluations
- `GET /status` - API status
- `GET /health` - Health check

## 🔒 Security Considerations

### For Production Use:

1. **Use Environment Variables:**
   - Store API keys in Render's environment variables
   - Never commit API keys to your repository

2. **Add Authentication:**
   ```python
   from flask_httpauth import HTTPTokenAuth
   auth = HTTPTokenAuth(scheme='Bearer')
   ```

3. **Rate Limiting:**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=get_remote_address)
   ```

4. **HTTPS Only:**
   - Render automatically provides HTTPS
   - Force HTTPS redirects in your application

## 📈 Scaling

### Free Tier Limitations:
- 750 hours/month
- 512MB RAM
- 30-second timeout
- No custom domains

### Paid Plans:
- More resources available
- Custom domains
- Better performance
- Priority support

## 🔄 Continuous Deployment

### Automatic Deploys:
- Render automatically deploys on git push
- Each commit triggers a new deployment
- Rollback to previous versions available

### Manual Deploys:
- Trigger manual deployments from dashboard
- Deploy specific branches or commits
- Preview deployments for testing

## 📞 Support

### Render Support:
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)
- [Render Status](https://status.render.com/)

### API Documentation:
- Full API documentation available at your deployed URL
- Example: `https://your-app-name.onrender.com/`

## 🎉 Success!

Once deployed, your API will be:
- ✅ **Publicly accessible** via HTTPS
- ✅ **Automatically scaled** by Render
- ✅ **Monitored** with built-in logging
- ✅ **Secure** with environment variables
- ✅ **Reliable** with automatic restarts

Your Stock Prediction API is now ready for production use! 