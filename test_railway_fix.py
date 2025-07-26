#!/usr/bin/env python3
"""
Test script to verify Railway timezone fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import fetch_daily_data, NIFTY_20
import pytz
from datetime import datetime

def test_railway_fix():
    """Test the Railway timezone fix."""
    print("🔧 Testing Railway Timezone Fix")
    print("=" * 50)
    
    # Test timezone
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    print(f"Current IST time: {now_ist}")
    print(f"Weekday: {now_ist.weekday()} (0=Monday, 6=Sunday)")
    
    # Test with a few stocks
    test_symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing: {symbol}")
        try:
            df = fetch_daily_data(symbol, days=5)
            if not df.empty:
                print(f"✅ Success! Data shape: {df.shape}")
                print(f"   Latest close: {df['Close'].iloc[-1]}")
                print(f"   Date range: {df.index[0]} to {df.index[-1]}")
            else:
                print(f"❌ No data available")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_railway_fix() 