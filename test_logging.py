#!/usr/bin/env python3
"""
Test script to verify logging functionality
"""

import logging
import sys
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_logging.log')
    ]
)
logger = logging.getLogger(__name__)

def test_logging():
    """Test logging functionality."""
    logger.info("🧪 Starting logging test")
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test with emojis and formatting
    logger.info("✅ Success message with emoji")
    logger.warning("⚠️ Warning message with emoji")
    logger.error("❌ Error message with emoji")
    
    # Test with data
    test_data = {
        "symbol": "RELIANCE.NS",
        "price": 1391.70,
        "confidence": 0.65
    }
    logger.info(f"📊 Test data: {test_data}")
    
    logger.info("✅ Logging test completed successfully")

if __name__ == "__main__":
    test_logging() 