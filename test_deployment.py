#!/usr/bin/env python3
"""
Test script for deployed Stock Prediction API
Replace YOUR_APP_NAME with your actual Render app name
"""

import requests
import json
from datetime import datetime

# Replace with your actual Render app URL
BASE_URL = "https://YOUR_APP_NAME.onrender.com"

def test_api_health():
    """Test if the API is running."""
    print("🏥 Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False

def test_api_info():
    """Test API information endpoint."""
    print("\n📋 Testing API Information...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ API information retrieved")
            data = response.json()
            print(f"📊 Version: {data.get('version')}")
            print(f"🌐 Deployment: {data.get('deployment')}")
            return True
        else:
            print(f"❌ API info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting API info: {e}")
        return False

def test_prediction():
    """Test prediction endpoint."""
    print("\n🚀 Testing Prediction Endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/predict", timeout=30)
        if response.status_code == 200:
            print("✅ Prediction started successfully")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error testing prediction: {e}")
        return False

def test_status():
    """Test status endpoint."""
    print("\n📊 Testing Status Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=10)
        if response.status_code == 200:
            print("✅ Status retrieved successfully")
            data = response.json()
            print(f"🔄 API Status: {data.get('status')}")
            print(f"⏰ Last Updated: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

def test_get_predictions():
    """Test getting predictions."""
    print("\n📈 Testing Get Predictions...")
    try:
        today = datetime.now().strftime('%Y%m%d')
        response = requests.get(f"{BASE_URL}/predictions/{today}", timeout=10)
        if response.status_code == 200:
            print("✅ Predictions retrieved successfully")
            data = response.json()
            print(f"📊 Found {data.get('count', 0)} predictions")
            return True
        elif response.status_code == 404:
            print("ℹ️  No predictions found for today (this is normal)")
            return True
        else:
            print(f"❌ Failed to get predictions: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting predictions: {e}")
        return False

def main():
    """Run all deployment tests."""
    print("🧪 Stock Prediction API Deployment Test Suite")
    print("=" * 60)
    print(f"🌐 Testing API at: {BASE_URL}")
    print("=" * 60)
    
    tests = [
        test_api_health,
        test_api_info,
        test_status,
        test_prediction,
        test_get_predictions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    print("\n🔗 Your API is ready to use!")
    print(f"📖 API Documentation: {BASE_URL}/")
    print(f"📊 API Status: {BASE_URL}/status")

if __name__ == "__main__":
    main() 