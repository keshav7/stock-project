#!/usr/bin/env python3
"""
Debug script to test stock data fetching
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

# Test symbols
TEST_SYMBOLS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS'
]

def test_stock_data():
    """Test stock data fetching for each symbol."""
    print("🔍 Testing Stock Data Fetching")
    print("=" * 50)
    
    for symbol in TEST_SYMBOLS:
        print(f"\n📊 Testing: {symbol}")
        
        try:
            # Test 1: Daily data (2 days)
            print("  Testing daily data (2 days)...")
            df_daily = yf.download(symbol, period='2d', interval='1d', progress=False)
            print(f"    Daily data shape: {df_daily.shape}")
            if not df_daily.empty:
                print(f"    Latest close: {df_daily['Close'].iloc[-1]}")
                print(f"    Date range: {df_daily.index[0]} to {df_daily.index[-1]}")
            else:
                print("    ❌ No daily data available")
            
            # Test 2: Intraday data (5-min intervals)
            print("  Testing intraday data (5-min intervals)...")
            df_intraday = yf.download(symbol, period='1d', interval='5m', progress=False)
            print(f"    Intraday data shape: {df_intraday.shape}")
            if not df_intraday.empty:
                print(f"    Latest close: {df_intraday['Close'].iloc[-1]}")
                print(f"    Date range: {df_intraday.index[0]} to {df_intraday.index[-1]}")
            else:
                print("    ❌ No intraday data available")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        print("-" * 30)

def test_current_market_status():
    """Test if markets are currently open."""
    print("\n🌍 Testing Market Status")
    print("=" * 30)
    
    # Test a simple US stock to see if yfinance is working
    try:
        print("Testing with AAPL (Apple) stock...")
        df_aapl = yf.download('AAPL', period='1d', interval='1d', progress=False)
        if not df_aapl.empty:
            print(f"✅ AAPL data available: {df_aapl['Close'].iloc[-1]}")
        else:
            print("❌ AAPL data not available")
    except Exception as e:
        print(f"❌ Error with AAPL: {e}")

def test_indian_market_timing():
    """Check if Indian markets are open."""
    print("\n🇮🇳 Indian Market Timing Check")
    print("=" * 30)
    
    now = datetime.now()
    print(f"Current time: {now}")
    
    # Indian market hours: 9:15 AM to 3:30 PM IST (Mon-Fri)
    is_weekday = now.weekday() < 5  # Monday = 0, Friday = 4
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    print(f"Weekday: {is_weekday}")
    print(f"Market open time: {market_open}")
    print(f"Market close time: {market_close}")
    
    if is_weekday and market_open <= now <= market_close:
        print("✅ Markets should be open")
    else:
        print("❌ Markets are closed (this might be why data is empty)")

if __name__ == "__main__":
    test_current_market_status()
    test_indian_market_timing()
    test_stock_data()
    
    print("\n" + "=" * 50)
    print("🔧 Debug Summary:")
    print("If you see empty data, possible causes:")
    print("1. Markets are closed (weekend/holiday)")
    print("2. Network connectivity issues")
    print("3. Yahoo Finance API issues")
    print("4. Symbol format issues") 