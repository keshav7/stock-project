#!/usr/bin/env python3
"""
Morning prediction script for stock analysis.
Runs at 8:30 AM IST to predict stock prices and send email.
"""

import os
import sys
import json
import logging
from datetime import datetime
import yfinance as yf
import pandas as pd

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('morning_prediction.log')
    ]
)
logger = logging.getLogger(__name__)

# Set API keys
os.environ['NEWS_API_KEY'] = 'a9ce32b4eece45cdad109310c59be10d'
os.environ['OPENAI_API_KEY'] = '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'

def get_today_close(symbol):
    """Get today's closing price for a symbol."""
    logger.info(f"🔍 Getting today's close for {symbol}")
    try:
        # Use the improved data fetching method
        from data_fetcher import fetch_daily_data
        logger.info(f"📊 Fetching daily data for {symbol}")
        df = fetch_daily_data(symbol, days=5)  # Get 5 days to ensure we have recent data
        
        if df.empty:
            logger.warning(f"❌ No data available for {symbol}")
            return None
        
        # Get the most recent close price
        latest_close = df['Close'].iloc[-1]
        logger.info(f"✅ Latest close for {symbol}: {latest_close}")
        return latest_close
        
    except Exception as e:
        logger.error(f"❌ Error getting close price for {symbol}: {e}")
        return None

def predict_close(confidence_score, current_close):
    """Predict close price based on confidence score."""
    logger.info(f"🔮 Predicting close with confidence {confidence_score} and current close {current_close}")
    try:
        # Simple prediction: adjust by ±2% based on confidence
        adjustment = (confidence_score - 0.5) * 0.04  # ±2% range
        predicted = current_close * (1 + adjustment)
        logger.info(f"✅ Predicted close: {predicted} (adjustment: {adjustment:.4f})")
        return predicted
    except Exception as e:
        logger.error(f"❌ Error predicting close: {e}")
        return current_close

def safe_scalar(val):
    """Convert pandas/numpy values to scalar safely."""
    logger.debug(f"🔄 Converting value: {val} (type: {type(val)})")
    
    if hasattr(val, 'item'):
        if hasattr(val, 'size') and val.size == 1:
            val = val.item()
            logger.debug(f"✅ Converted to scalar: {val}")
        else:
            val = None
            logger.warning("⚠️ Size not 1, setting to None")

    if val is None or pd.isna(val):
        logger.warning("⚠️ Value is None or NaN, returning '-'")
        return '-'

    if isinstance(val, (float, int)):
        result = f"{val:.2f}"
        logger.debug(f"✅ Numeric value, returning: {result}")
        return result
    else:
        result = str(val)
        logger.debug(f"✅ String value, returning: {result}")
        return result

def get_technical_score(symbol):
    """Get technical analysis score for a symbol."""
    logger.info(f"📈 Getting technical score for {symbol}")
    try:
        from data_fetcher import fetch_intraday_data
        from technical_analyzer import compute_indicators
        
        # Fetch intraday data
        logger.info(f"📊 Fetching intraday data for {symbol}")
        df = fetch_intraday_data(symbol, period_days=30, interval='5m')
        
        if df.empty:
            logger.warning(f"⚠️ No intraday data for {symbol}, using default score")
            return 0.5  # Neutral score
        
        logger.info(f"✅ Got intraday data for {symbol}: {len(df)} records")
        
        # Compute technical indicators
        logger.info(f"🔧 Computing technical indicators for {symbol}")
        indicators = compute_indicators(df)
        logger.info(f"✅ Technical indicators computed: {indicators}")
        
        # Calculate a simple technical score based on indicators
        score = 0.5  # Base neutral score
        
        # Adjust based on RSI
        if 'rsi' in indicators and not pd.isna(indicators['rsi']):
            rsi = indicators['rsi']
            logger.info(f"📊 RSI for {symbol}: {rsi}")
            if rsi < 30:  # Oversold
                score += 0.2
                logger.info(f"📈 RSI oversold, adding 0.2 to score")
            elif rsi > 70:  # Overbought
                score -= 0.2
                logger.info(f"📉 RSI overbought, subtracting 0.2 from score")
        
        # Adjust based on MACD
        if 'macd' in indicators and not pd.isna(indicators['macd']):
            macd = indicators['macd']
            logger.info(f"📊 MACD for {symbol}: {macd}")
            if macd > 0:  # Positive MACD
                score += 0.1
                logger.info(f"📈 Positive MACD, adding 0.1 to score")
            else:  # Negative MACD
                score -= 0.1
                logger.info(f"📉 Negative MACD, subtracting 0.1 from score")
        
        # Ensure score is between 0 and 1
        score = max(0, min(1, score))
        
        logger.info(f"✅ Technical score for {symbol}: {score:.2f}")
        return score
        
    except Exception as e:
        logger.error(f"❌ Error calculating technical score for {symbol}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 0.5  # Default neutral score

def get_news_sentiment(symbol):
    """Get news sentiment score for a symbol."""
    logger.info(f"📰 Getting news sentiment for {symbol}")
    try:
        from news_analyzer import analyze_news_sentiment
        
        # Get company name from symbol
        company_name = symbol.replace('.NS', '').replace('.BO', '')
        logger.info(f"🔍 Analyzing sentiment for company: {company_name}")
        
        # Analyze news sentiment
        sentiment_score = analyze_news_sentiment(company_name)
        
        logger.info(f"✅ Sentiment score for {symbol}: {sentiment_score:.2f}")
        return sentiment_score
        
    except Exception as e:
        logger.error(f"❌ Error calculating sentiment score for {symbol}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 0.5  # Default neutral score

def generate_predictions():
    """Generate predictions for all stocks."""
    logger.info("🚀 Starting prediction generation process")
    
    # Use reliable stocks instead of all NIFTY_20
    from data_fetcher import RELIABLE_STOCKS
    
    predictions = []
    
    logger.info(f"🔮 Generating predictions for {len(RELIABLE_STOCKS)} reliable stocks: {RELIABLE_STOCKS}")
    
    for symbol in RELIABLE_STOCKS:
        try:
            logger.info(f"\n📊 Processing: {symbol}")
            
            # Get current close price
            logger.info(f"💰 Getting current close for {symbol}")
            current_close = get_today_close(symbol)
            if current_close is None:
                logger.warning(f"❌ Skipping {symbol} - no current price data")
                continue
            
            logger.info(f"✅ Current close for {symbol}: {current_close}")
            
            # Get technical analysis
            logger.info(f"📈 Getting technical analysis for {symbol}")
            technical_score = get_technical_score(symbol)
            logger.info(f"✅ Technical score for {symbol}: {technical_score}")
            
            # Get news sentiment
            logger.info(f"📰 Getting news sentiment for {symbol}")
            sentiment_score = get_news_sentiment(symbol)
            logger.info(f"✅ Sentiment score for {symbol}: {sentiment_score}")
            
            # Calculate confidence score
            confidence_score = (technical_score + sentiment_score) / 2
            logger.info(f"🎯 Calculated confidence score for {symbol}: {confidence_score:.2f}")
            
            # Predict close price (simple prediction based on current price and confidence)
            predicted_close = current_close * (1 + (confidence_score - 0.5) * 0.02)  # ±2% range
            logger.info(f"🔮 Predicted close for {symbol}: {predicted_close:.2f}")
            
            # Determine recommendation
            if confidence_score > 0.6:
                recommendation = "BUY"
                reason = "Strong technical indicators and positive sentiment"
            elif confidence_score < 0.4:
                recommendation = "SELL"
                reason = "Weak technical indicators and negative sentiment"
            else:
                recommendation = "HOLD"
                reason = "Mixed signals, maintain current position"
            
            logger.info(f"💡 Recommendation for {symbol}: {recommendation} - {reason}")
            
            prediction = {
                'symbol': symbol,
                'current_close': safe_scalar(current_close),
                'predicted_close': safe_scalar(predicted_close),
                'confidence_score': round(confidence_score, 2),
                'technical_score': round(technical_score, 2),
                'sentiment_score': round(sentiment_score, 2),
                'recommendation': recommendation,
                'reason': reason,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            predictions.append(prediction)
            logger.info(f"✅ Generated prediction for {symbol}: {recommendation} (Confidence: {confidence_score:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Error generating prediction for {symbol}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            continue
    
    logger.info(f"\n📈 Generated {len(predictions)} predictions successfully")
    logger.info(f"📋 Predictions: {json.dumps(predictions, indent=2)}")
    return predictions

def create_prediction_email_html(predictions):
    """Create HTML email content for predictions."""
    logger.info("📧 Creating prediction email HTML")
    
    if not predictions:
        logger.warning("⚠️ No predictions to include in email")
        return "<h2>No predictions available</h2>"
    
    html = f"""
    <h2>📊 Stock Predictions for {datetime.now().strftime('%Y-%m-%d')}</h2>
    <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f2f2f2;">
            <th>Symbol</th>
            <th>Current Close</th>
            <th>Predicted Close</th>
            <th>Confidence</th>
            <th>Technical</th>
            <th>Sentiment</th>
            <th>Recommendation</th>
            <th>Reason</th>
        </tr>
    """
    
    for pred in predictions:
        confidence_color = "green" if pred['confidence_score'] > 0.6 else "red" if pred['confidence_score'] < 0.4 else "orange"
        recommendation_color = "green" if pred['recommendation'] == "BUY" else "red" if pred['recommendation'] == "SELL" else "orange"
        
        html += f"""
        <tr>
            <td><strong>{pred['symbol']}</strong></td>
            <td>₹{pred['current_close']}</td>
            <td>₹{pred['predicted_close']}</td>
            <td style="color: {confidence_color};">{pred['confidence_score']}</td>
            <td>{pred['technical_score']}</td>
            <td>{pred['sentiment_score']}</td>
            <td style="color: {recommendation_color}; font-weight: bold;">{pred['recommendation']}</td>
            <td>{pred['reason']}</td>
        </tr>
        """
    
    html += "</table>"
    logger.info("✅ Prediction email HTML created successfully")
    return html

def main():
    """Main function to run morning predictions."""
    logger.info("🌅 Starting morning prediction process")
    
    try:
        # Check if it's a weekday (optional for testing)
        weekday = datetime.now().weekday()
        logger.info(f"📅 Current weekday: {weekday} (0=Monday, 6=Sunday)")
        
        # Generate predictions
        logger.info("🔮 Generating stock predictions...")
        predictions = generate_predictions()
        
        if not predictions:
            logger.error("❌ No predictions generated!")
            return
        
        # Save predictions to file
        logger.info("💾 Saving predictions to file...")
        os.makedirs('predictions', exist_ok=True)
        filename = f"predictions/predictions_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w') as f:
            json.dump(predictions, f, indent=2)
        
        logger.info(f"✅ Predictions saved to {filename}")
        
        # Create email content
        logger.info("📧 Creating email content...")
        email_html = create_prediction_email_html(predictions)
        
        # Send email
        logger.info("📤 Sending prediction email...")
        from email_sender import send_email
        
        subject = f"Stock Predictions - {datetime.now().strftime('%Y-%m-%d')}"
        recipient = "gupkes@gmail.com"
        
        message_id = send_email(recipient, subject, email_html)
        logger.info(f"✅ Prediction email sent successfully to {recipient}")
        logger.info(f"📧 Message ID: {message_id}")
        
    except Exception as e:
        logger.error(f"❌ Error in main prediction process: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 