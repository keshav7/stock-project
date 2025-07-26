#!/usr/bin/env python3
"""
Test script for Stock Prediction API
Demonstrates how to use the API endpoints
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:5000"

def test_api_status():
    """Test the API status endpoint."""
    print("🔍 Testing API Status...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            print("✅ API is running")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ API status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")

def test_prediction():
    """Test the prediction endpoint."""
    print("\n🚀 Testing Prediction Endpoint...")
    try:
        # Test with default email
        response = requests.post(f"{BASE_URL}/predict")
        if response.status_code == 200:
            print("✅ Prediction started successfully")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error testing prediction: {e}")

def test_prediction_with_email():
    """Test the prediction endpoint with custom email."""
    print("\n📧 Testing Prediction with Custom Email...")
    try:
        data = {"email": "test@example.com"}
        response = requests.post(f"{BASE_URL}/predict", json=data)
        if response.status_code == 200:
            print("✅ Prediction with custom email started successfully")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Prediction with custom email failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error testing prediction with custom email: {e}")

def test_evaluation():
    """Test the evaluation endpoint."""
    print("\n📊 Testing Evaluation Endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/evaluate")
        if response.status_code == 200:
            print("✅ Evaluation started successfully")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Evaluation failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error testing evaluation: {e}")

def test_get_predictions():
    """Test getting predictions for today."""
    print("\n📈 Testing Get Predictions...")
    try:
        today = datetime.now().strftime('%Y%m%d')
        response = requests.get(f"{BASE_URL}/predictions/{today}")
        if response.status_code == 200:
            print("✅ Retrieved predictions successfully")
            data = response.json()
            print(f"📊 Found {data['count']} predictions for {data['date']}")
            # Print first prediction as example
            if data['predictions']:
                print("📋 Sample prediction:")
                print(json.dumps(data['predictions'][0], indent=2))
        else:
            print(f"❌ Failed to get predictions: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error getting predictions: {e}")

def test_health_check():
    """Test the health check endpoint."""
    print("\n🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in health check: {e}")

def main():
    """Run all API tests."""
    print("🧪 Stock Prediction API Test Suite")
    print("=" * 50)
    
    # Test API status first
    test_api_status()
    
    # Test health check
    test_health_check()
    
    # Test prediction endpoints
    test_prediction()
    test_prediction_with_email()
    
    # Test evaluation endpoint
    test_evaluation()
    
    # Test data retrieval
    test_get_predictions()
    
    print("\n" + "=" * 50)
    print("✅ API Test Suite Completed!")

if __name__ == "__main__":
    main() 