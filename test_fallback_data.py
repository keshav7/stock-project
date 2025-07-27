#!/usr/bin/env python3
"""
Test script to verify fallback data functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import fetch_daily_data, RELIABLE_STOCKS, FALLBACK_DATA
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_fallback_data():
    """Test the fallback data functionality."""
    logger.info("🧪 Testing Fallback Data Functionality")
    logger.info("=" * 50)
    
    for symbol in RELIABLE_STOCKS:
        logger.info(f"\n📊 Testing: {symbol}")
        
        # Test daily data fetching
        df = fetch_daily_data(symbol, days=5)
        
        if not df.empty:
            logger.info(f"✅ Success! Data shape: {df.shape}")
            logger.info(f"   Latest close: {df['Close'].iloc[-1]}")
            logger.info(f"   Date range: {df.index[0]} to {df.index[-1]}")
        else:
            logger.warning(f"❌ No data available for {symbol}")
            
            # Check if fallback data exists
            if symbol in FALLBACK_DATA:
                fallback = FALLBACK_DATA[symbol]
                logger.info(f"📋 Fallback data available: {fallback}")
            else:
                logger.warning(f"⚠️ No fallback data for {symbol}")

def test_fallback_data_creation():
    """Test creating fallback data manually."""
    logger.info("\n🔧 Testing Fallback Data Creation")
    logger.info("=" * 40)
    
    for symbol, fallback in FALLBACK_DATA.items():
        logger.info(f"\n📊 Testing fallback for: {symbol}")
        logger.info(f"   Close price: {fallback['close']}")
        logger.info(f"   Company name: {fallback['name']}")
        
        # Test daily data fetching (should use fallback)
        df = fetch_daily_data(symbol, days=5)
        
        if not df.empty:
            logger.info(f"✅ Fallback data created successfully!")
            logger.info(f"   DataFrame shape: {df.shape}")
            logger.info(f"   Latest close: {df['Close'].iloc[-1]}")
        else:
            logger.error(f"❌ Fallback data creation failed for {symbol}")

if __name__ == "__main__":
    test_fallback_data()
    test_fallback_data_creation()
    
    logger.info("\n" + "=" * 50)
    logger.info("🎯 Test Summary:")
    logger.info("If you see '✅ Using fallback data' messages, the fallback system is working!")
    logger.info("This means predictions will work even when Yahoo Finance fails.") 