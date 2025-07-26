import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Top 20 Nifty 50 stocks (sample, can be updated)
NIFTY_20 = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'ITC.NS', 'LT.NS', 'SBIN.NS', 'BHARTIARTL.NS',
    'BAJFINANCE.NS', 'KOTAKBANK.NS', 'ASIANPAINT.NS', 'HCLTECH.NS',
    'MARUTI.NS', 'AXISBANK.NS', 'SUNPHARMA.NS', 'TITAN.NS',
    'ULTRACEMCO.NS', 'WIPRO.NS'
]

def get_indian_date_range():
    """Get the proper date range for Indian market data."""
    # Get current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    
    # If it's weekend, get Friday's data
    if now_ist.weekday() >= 5:  # Saturday = 5, Sunday = 6
        # Go back to Friday
        days_back = now_ist.weekday() - 4  # Friday = 4
        now_ist = now_ist - timedelta(days=days_back)
    
    # Get data for the last 2 trading days
    end_date = now_ist.strftime('%Y-%m-%d')
    start_date = (now_ist - timedelta(days=5)).strftime('%Y-%m-%d')  # Go back 5 days to ensure we get data
    
    return start_date, end_date

def fetch_intraday_data(symbol, period_days=60, interval='5m'):
    """
    Fetch 5-min interval data for the past `period_days` for a given stock symbol.
    Returns a pandas DataFrame.
    """
    try:
        # Use period instead of specific dates for better reliability
        period = f"{period_days}d"
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        
        if df.empty:
            print(f"Warning: No data returned for {symbol}")
            return pd.DataFrame()
        
        df = df.reset_index()
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()

def fetch_daily_data(symbol, days=2):
    """
    Fetch daily data for a given stock symbol.
    Returns a pandas DataFrame.
    """
    try:
        # Use period instead of specific dates
        period = f"{days}d"
        df = yf.download(symbol, period=period, interval='1d', progress=False)
        
        if df.empty:
            print(f"Warning: No daily data returned for {symbol}")
            return pd.DataFrame()
        
        return df
    except Exception as e:
        print(f"Error fetching daily data for {symbol}: {e}")
        return pd.DataFrame()

def fetch_all_intraday(symbols=NIFTY_20, period_days=60, interval='5m'):
    """
    Fetch intraday data for all symbols. Returns a dict of DataFrames.
    """
    data = {}
    for symbol in symbols:
        try:
            df = fetch_intraday_data(symbol, period_days, interval)
            if not df.empty:
                data[symbol] = df
                print(f"✅ Successfully fetched {symbol}: {len(df)} records")
            else:
                print(f"❌ No data for {symbol}")
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    return data 

if __name__ == "__main__":
    print("Fetching intraday data for Nifty 20 stocks...")
    print(f"Fetching data for {len(NIFTY_20)} stocks...")
    
    # Fetch data for all stocks
    data = fetch_all_intraday()
    
    # Print summary for each stock
    for symbol, df in data.items():
        if not df.empty:
            print(f"{symbol}: {len(df)} records, Date range: {df['Datetime'].min()} to {df['Datetime'].max()}")
        else:
            print(f"{symbol}: No data available")
    
    print(f"\nSuccessfully fetched data for {len(data)} stocks") 