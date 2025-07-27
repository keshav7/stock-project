import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Updated Nifty 50 stocks with verified symbols
NIFTY_20 = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'ITC.NS', 'LT.NS', 'SBIN.NS', 'BHARTIARTL.NS',
    'BAJFINANCE.NS', 'KOTAKBANK.NS', 'ASIANPAINT.NS', 'HCLTECH.NS',
    'MARUTI.NS', 'AXISBANK.NS', 'SUNPHARMA.NS', 'TITAN.NS',
    'ULTRACEMCO.NS', 'WIPRO.NS'
]

# Simplified list with only the most reliable stocks
RELIABLE_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS'
]

# Alternative symbols to try if primary fails
SYMBOL_ALTERNATIVES = {
    'SBIN.NS': ['SBIN.NS', 'SBIN.BO'],
    'BHARTIARTL.NS': ['BHARTIARTL.NS', 'BHARTIARTL.BO'],
    'BAJFINANCE.NS': ['BAJFINANCE.NS', 'BAJFINANCE.BO'],
    'KOTAKBANK.NS': ['KOTAKBANK.NS', 'KOTAKBANK.BO'],
    'ASIANPAINT.NS': ['ASIANPAINT.NS', 'ASIANPAINT.BO'],
    'HCLTECH.NS': ['HCLTECH.NS', 'HCLTECH.BO'],
    'MARUTI.NS': ['MARUTI.NS', 'MARUTI.BO'],
    'AXISBANK.NS': ['AXISBANK.NS', 'AXISBANK.BO'],
    'SUNPHARMA.NS': ['SUNPHARMA.NS', 'SUNPHARMA.BO'],
    'TITAN.NS': ['TITAN.NS', 'TITAN.BO'],
    'ULTRACEMCO.NS': ['ULTRACEMCO.NS', 'ULTRACEMCO.BO'],
    'WIPRO.NS': ['WIPRO.NS', 'WIPRO.BO']
}

def get_indian_date_range():
    """Get the proper date range for Indian market data."""
    logger.info("🌍 Getting Indian date range")
    # Get current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    logger.info(f"🕐 Current IST time: {now_ist}")
    
    # If it's weekend, get Friday's data
    if now_ist.weekday() >= 5:  # Saturday = 5, Sunday = 6
        # Go back to Friday
        days_back = now_ist.weekday() - 4  # Friday = 4
        now_ist = now_ist - timedelta(days=days_back)
        logger.info(f"📅 Weekend detected, using Friday: {now_ist}")
    
    # Get data for the last 2 trading days
    end_date = now_ist.strftime('%Y-%m-%d')
    start_date = (now_ist - timedelta(days=5)).strftime('%Y-%m-%d')  # Go back 5 days to ensure we get data
    
    logger.info(f"📅 Date range: {start_date} to {end_date}")
    return start_date, end_date

def try_multiple_symbols(symbol, period_days=60, interval='5m'):
    """Try multiple symbol variations to get data."""
    logger.info(f"🔄 Trying multiple symbols for {symbol}")
    alternatives = SYMBOL_ALTERNATIVES.get(symbol, [symbol])
    logger.info(f"📋 Symbol alternatives: {alternatives}")
    
    for alt_symbol in alternatives:
        try:
            logger.info(f"  🔍 Trying symbol: {alt_symbol}")
            period = f"{period_days}d"
            logger.info(f"  📊 Downloading with period: {period}, interval: {interval}")
            
            df = yf.download(alt_symbol, period=period, interval=interval, progress=False)
            
            if not df.empty:
                logger.info(f"  ✅ Success with {alt_symbol}: {len(df)} records")
                logger.info(f"  📈 Data shape: {df.shape}")
                logger.info(f"  📅 Date range: {df.index[0]} to {df.index[-1]}")
                df = df.reset_index()
                return df, alt_symbol
            else:
                logger.warning(f"  ❌ No data for {alt_symbol}")
                
        except Exception as e:
            logger.error(f"  ❌ Error with {alt_symbol}: {e}")
    
    logger.error(f"❌ All symbol alternatives failed for {symbol}")
    return pd.DataFrame(), None

def fetch_intraday_data(symbol, period_days=60, interval='5m'):
    """
    Fetch 5-min interval data for the past `period_days` for a given stock symbol.
    Returns a pandas DataFrame.
    """
    logger.info(f"📊 Fetching intraday data for {symbol}")
    try:
        # Try multiple symbol variations
        df, working_symbol = try_multiple_symbols(symbol, period_days, interval)
        
        if df.empty:
            logger.warning(f"⚠️ No data returned for {symbol} (tried all alternatives)")
            return pd.DataFrame()
        
        logger.info(f"✅ Successfully fetched intraday data for {symbol}")
        return df
    except Exception as e:
        logger.error(f"❌ Error fetching {symbol}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return pd.DataFrame()

def fetch_daily_data(symbol, days=5):
    """
    Fetch daily data for a given stock symbol.
    Returns a pandas DataFrame.
    """
    logger.info(f"📈 Fetching daily data for {symbol}")
    try:
        # Try multiple symbol variations
        alternatives = SYMBOL_ALTERNATIVES.get(symbol, [symbol])
        logger.info(f"📋 Daily data alternatives: {alternatives}")
        
        for alt_symbol in alternatives:
            try:
                logger.info(f"  🔍 Trying daily data for: {alt_symbol}")
                period = f"{days}d"
                logger.info(f"  📊 Downloading with period: {period}")
                
                df = yf.download(alt_symbol, period=period, interval='1d', progress=False)
                
                if not df.empty:
                    logger.info(f"  ✅ Daily data success with {alt_symbol}: {len(df)} records")
                    logger.info(f"  📈 Data shape: {df.shape}")
                    logger.info(f"  📅 Date range: {df.index[0]} to {df.index[-1]}")
                    logger.info(f"  💰 Latest close: {df['Close'].iloc[-1]}")
                    return df
                else:
                    logger.warning(f"  ❌ No daily data for {alt_symbol}")
                    
            except Exception as e:
                logger.error(f"  ❌ Error with daily data for {alt_symbol}: {e}")
        
        logger.warning(f"⚠️ No daily data returned for {symbol} (tried all alternatives)")
        return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"❌ Error fetching daily data for {symbol}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return pd.DataFrame()

def fetch_all_intraday(symbols=NIFTY_20, period_days=60, interval='5m'):
    """
    Fetch intraday data for all symbols. Returns a dict of DataFrames.
    """
    data = {}
    successful_count = 0
    
    logger.info(f"🚀 Fetching intraday data for {len(symbols)} stocks...")
    logger.info(f"📋 Symbols: {symbols}")
    
    for symbol in symbols:
        try:
            logger.info(f"\n📊 Processing: {symbol}")
            df = fetch_intraday_data(symbol, period_days, interval)
            if not df.empty:
                data[symbol] = df
                successful_count += 1
                logger.info(f"✅ Successfully fetched {symbol}: {len(df)} records")
            else:
                logger.warning(f"❌ No data for {symbol}")
        except Exception as e:
            logger.error(f"❌ Error fetching {symbol}: {e}")
    
    logger.info(f"\n📈 Summary: {successful_count}/{len(symbols)} stocks fetched successfully")
    return data

def test_stock_availability():
    """Test which stocks are available."""
    logger.info("🔍 Testing Stock Availability")
    logger.info("=" * 50)
    
    test_symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS']
    
    for symbol in test_symbols:
        logger.info(f"\nTesting: {symbol}")
        df = fetch_daily_data(symbol, days=5)
        if not df.empty:
            logger.info(f"✅ Available: {symbol}")
            logger.info(f"   Latest close: {df['Close'].iloc[-1]}")
        else:
            logger.warning(f"❌ Not available: {symbol}")

if __name__ == "__main__":
    # Set up logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Testing stock data fetching...")
    test_stock_availability()
    
    logger.info("\n" + "=" * 50)
    logger.info("Fetching intraday data for Nifty 20 stocks...")
    
    # Fetch data for all stocks
    data = fetch_all_intraday()
    
    # Print summary for each stock
    for symbol, df in data.items():
        if not df.empty:
            logger.info(f"{symbol}: {len(df)} records, Date range: {df['Datetime'].min()} to {df['Datetime'].max()}")
        else:
            logger.warning(f"{symbol}: No data available")
    
    logger.info(f"\nSuccessfully fetched data for {len(data)} stocks") 