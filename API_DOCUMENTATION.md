# Stock Prediction API Documentation

A REST API for generating stock predictions and evaluations with email notifications.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_api.txt
```

### 2. Start the API Server
```bash
python3 api_server.py
```

The API will be available at: `http://localhost:5000`

## 📋 API Endpoints

### Base URL
```
http://localhost:5000
```

### 1. API Information
**GET /** - Get API information and available endpoints

**Response:**
```json
{
  "message": "Stock Prediction API",
  "version": "1.0.0",
  "endpoints": {
    "GET /": "API information",
    "POST /predict": "Generate stock predictions and send email",
    "POST /evaluate": "Evaluate today's predictions and send email",
    "GET /status": "Get API status",
    "GET /predictions/<date>": "Get predictions for a specific date",
    "GET /evaluations/<date>": "Get evaluations for a specific date"
  },
  "status": {
    "last_prediction_time": null,
    "last_evaluation_time": null,
    "is_running_prediction": false,
    "is_running_evaluation": false,
    "prediction_count": 0,
    "evaluation_count": 0
  }
}
```

### 2. API Status
**GET /status** - Get current API status

**Response:**
```json
{
  "status": "running",
  "timestamp": "2025-07-26T18:46:02.123456",
  "api_status": {
    "last_prediction_time": "2025-07-26T18:46:02.123456",
    "last_evaluation_time": null,
    "is_running_prediction": false,
    "is_running_evaluation": false,
    "prediction_count": 1,
    "evaluation_count": 0
  }
}
```

### 3. Generate Predictions
**POST /predict** - Generate stock predictions and send email

**Request Body (Optional):**
```json
{
  "email": "custom@example.com"
}
```

**Response:**
```json
{
  "message": "Prediction started",
  "email": "gupkes@gmail.com",
  "status": "processing",
  "timestamp": "2025-07-26T18:46:02.123456"
}
```

**Features:**
- Generates top 5 stock picks for the day
- Sends beautiful HTML email with predictions
- Saves predictions to local file
- Runs asynchronously (non-blocking)
- Default email: gupkes@gmail.com

### 4. Evaluate Predictions
**POST /evaluate** - Evaluate today's predictions and send results

**Request Body (Optional):**
```json
{
  "email": "custom@example.com"
}
```

**Response:**
```json
{
  "message": "Evaluation started",
  "email": "gupkes@gmail.com",
  "status": "processing",
  "timestamp": "2025-07-26T18:46:02.123456"
}
```

**Features:**
- Compares morning predictions with actual market performance
- Sends evaluation results via email
- Calculates HIT/MISS statistics
- Saves evaluation results to local file
- Runs asynchronously (non-blocking)

### 5. Get Predictions
**GET /predictions/{date}** - Get predictions for a specific date

**Parameters:**
- `date` (path): Date in YYYYMMDD format (e.g., 20250726)

**Response:**
```json
{
  "date": "20250726",
  "predictions": [
    {
      "rank": 1,
      "symbol": "ITC.NS",
      "confidence_score": 2.0,
      "current_close": "409.40",
      "predicted_close": "413.49",
      "reason": "MACD bullish + EMA bullish",
      "prediction_date": "2025-07-26",
      "prediction_time": "18:46:02"
    }
  ],
  "count": 5,
  "timestamp": "2025-07-26T18:46:02.123456"
}
```

### 6. Get Evaluations
**GET /evaluations/{date}** - Get evaluations for a specific date

**Parameters:**
- `date` (path): Date in YYYYMMDD format (e.g., 20250726)

**Response:**
```json
{
  "date": "20250726",
  "evaluations": [
    {
      "rank": 1,
      "symbol": "ITC.NS",
      "confidence_score": 2.0,
      "predicted_close": "413.49",
      "actual_open": "410.00",
      "actual_close": "415.20",
      "actual_high": "416.50",
      "actual_low": "409.80",
      "result": "HIT",
      "reason": "MACD bullish + EMA bullish"
    }
  ],
  "count": 5,
  "timestamp": "2025-07-26T18:46:02.123456"
}
```

### 7. Health Check
**GET /health** - Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-26T18:46:02.123456",
  "uptime": 1234567890.123
}
```

## 🔧 Usage Examples

### Using cURL

#### Generate Predictions
```bash
# With default email
curl -X POST http://localhost:5000/predict

# With custom email
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'
```

#### Evaluate Predictions
```bash
# With default email
curl -X POST http://localhost:5000/evaluate

# With custom email
curl -X POST http://localhost:5000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'
```

#### Get Today's Predictions
```bash
curl http://localhost:5000/predictions/20250726
```

#### Get Today's Evaluations
```bash
curl http://localhost:5000/evaluations/20250726
```

### Using Python

```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:5000"

# Generate predictions
response = requests.post(f"{BASE_URL}/predict")
if response.status_code == 200:
    print("Prediction started:", response.json())

# Generate predictions with custom email
data = {"email": "your-email@example.com"}
response = requests.post(f"{BASE_URL}/predict", json=data)
if response.status_code == 200:
    print("Prediction started:", response.json())

# Evaluate predictions
response = requests.post(f"{BASE_URL}/evaluate")
if response.status_code == 200:
    print("Evaluation started:", response.json())

# Get today's predictions
today = "20250726"
response = requests.get(f"{BASE_URL}/predictions/{today}")
if response.status_code == 200:
    predictions = response.json()
    print(f"Found {predictions['count']} predictions")
```

### Using JavaScript (Node.js)

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5000';

// Generate predictions
async function generatePredictions() {
    try {
        const response = await axios.post(`${BASE_URL}/predict`);
        console.log('Prediction started:', response.data);
    } catch (error) {
        console.error('Error:', error.response.data);
    }
}

// Generate predictions with custom email
async function generatePredictionsWithEmail(email) {
    try {
        const response = await axios.post(`${BASE_URL}/predict`, {
            email: email
        });
        console.log('Prediction started:', response.data);
    } catch (error) {
        console.error('Error:', error.response.data);
    }
}

// Evaluate predictions
async function evaluatePredictions() {
    try {
        const response = await axios.post(`${BASE_URL}/evaluate`);
        console.log('Evaluation started:', response.data);
    } catch (error) {
        console.error('Error:', error.response.data);
    }
}

// Get predictions
async function getPredictions(date) {
    try {
        const response = await axios.get(`${BASE_URL}/predictions/${date}`);
        console.log('Predictions:', response.data);
    } catch (error) {
        console.error('Error:', error.response.data);
    }
}
```

## 🧪 Testing

Run the test suite to verify API functionality:

```bash
python3 test_api.py
```

## 📊 Response Status Codes

- **200** - Success
- **404** - Not found (e.g., no predictions for date)
- **409** - Conflict (operation already in progress)
- **500** - Internal server error

## 🔒 Security Notes

- API keys are embedded in the server code
- No authentication required (for development)
- CORS enabled for all origins
- Consider adding authentication for production use

## 🚀 Production Deployment

For production deployment:

1. **Add Authentication:**
   ```python
   from flask_httpauth import HTTPTokenAuth
   auth = HTTPTokenAuth(scheme='Bearer')
   ```

2. **Use Environment Variables:**
   ```python
   import os
   NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
   OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
   ```

3. **Use Production WSGI Server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
   ```

4. **Add Rate Limiting:**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=get_remote_address)
   ```

## 📞 Support

For issues or questions:
1. Check the API status: `GET /status`
2. Check health: `GET /health`
3. Review server logs
4. Test with the provided test script

## 🎉 Success!

The API provides:
- ✅ **RESTful endpoints** for predictions and evaluations
- ✅ **Asynchronous processing** (non-blocking)
- ✅ **Email notifications** with beautiful HTML formatting
- ✅ **Data persistence** (local JSON files)
- ✅ **Status tracking** and monitoring
- ✅ **CORS support** for web applications
- ✅ **Comprehensive error handling** 