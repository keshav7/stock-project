#!/usr/bin/env python3
"""
Test script to debug data processing issue
"""

import yfinance as yf
import pandas as pd

def test_data_processing():
    """Test the data processing logic."""
    print("🔍 Testing Data Processing")
    print("=" * 50)
    
    # Test with a single stock
    symbol = 'RELIANCE.NS'
    print(f"Testing with: {symbol}")
    
    try:
        # Get the data
        df = yf.download(symbol, period='2d', interval='1d', progress=False)
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        
        # Get the close price
        close_price = df['Close'].iloc[-1]
        print(f"Raw close price: {close_price}")
        print(f"Type: {type(close_price)}")
        print(f"Has item(): {hasattr(close_price, 'item')}")
        
        # Test the safe_scalar function
        def safe_scalar(val):
            """Convert pandas/numpy values to scalar safely."""
            print(f"  safe_scalar input: {val} (type: {type(val)})")
            
            if hasattr(val, 'item'):
                print(f"  Has item() method")
                if hasattr(val, 'size') and val.size == 1:
                    val = val.item()
                    print(f"  After item(): {val} (type: {type(val)})")
                else:
                    val = None
                    print(f"  Size not 1, setting to None")
            
            if val is None or pd.isna(val):
                print(f"  Value is None or NaN, returning '-'")
                return '-'
            
            if isinstance(val, (float, int)):
                result = f"{val:.2f}"
                print(f"  Numeric value, returning: {result}")
                return result
            else:
                result = str(val)
                print(f"  String value, returning: {result}")
                return result
        
        # Test the processing
        processed_close = safe_scalar(close_price)
        print(f"\nFinal processed close: {processed_close}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_data_processing() 