#!/usr/bin/env python3
"""
Morning Prediction Script - Runs at 8:30 AM IST on weekdays
Generates stock predictions and sends via email
"""

import os
import sys
import json
from datetime import datetime, timedelta
import pandas as pd
from email_sender import get_gmail_service, create_message, send_message
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import fetch_all_intraday, NIFTY_20
from technical_analyzer import compute_indicators
from news_analyzer import analyze_all_news
from recommender import recommend_stocks
import yfinance as yf
import asyncio

def safe_scalar(val):
    """Convert pandas/numpy values to scalar safely."""
    if hasattr(val, 'item'):
        val = val.item() if hasattr(val, 'size') and val.size == 1 else None
    if val is None or pd.isna(val):
        return '-'
    return f"{val:.2f}" if isinstance(val, (float, int)) else str(val)

def get_today_close(symbol):
    """Get today's closing price for a symbol."""
    try:
        # Use the improved data fetching method
        from data_fetcher import fetch_daily_data
        df = fetch_daily_data(symbol, days=5)  # Get 5 days to ensure we have recent data
        
        if df.empty:
            print(f"No data available for {symbol}")
            return None
        
        # Get the most recent close price
        latest_close = df['Close'].iloc[-1]
        print(f"Latest close for {symbol}: {latest_close}")
        return latest_close
        
    except Exception as e:
        print(f"Error getting close price for {symbol}: {e}")
        return None

def predict_close(rule_confidence, close):
    """Predict next day's closing price based on confidence score."""
    if close is None or close == '-':
        return '-'
    try:
        close = float(close)
    except Exception:
        return '-'
    
    if rule_confidence >= 2:
        return f"{close * 1.01:.2f}"  # +1%
    elif rule_confidence <= 0:
        return f"{close * 0.99:.2f}"  # -1%
    else:
        return f"{close:.2f}"

def get_technical_score(symbol):
    """Get technical analysis score for a symbol."""
    try:
        from data_fetcher import fetch_intraday_data
        from technical_analyzer import compute_indicators
        
        # Fetch intraday data
        df = fetch_intraday_data(symbol, period_days=30, interval='5m')
        
        if df.empty:
            print(f"  No intraday data for {symbol}, using default score")
            return 0.5  # Neutral score
        
        # Compute technical indicators
        indicators = compute_indicators(df)
        
        # Calculate a simple technical score based on indicators
        score = 0.5  # Base neutral score
        
        # Adjust based on RSI
        if 'rsi' in indicators and not pd.isna(indicators['rsi']):
            rsi = indicators['rsi']
            if rsi < 30:  # Oversold
                score += 0.2
            elif rsi > 70:  # Overbought
                score -= 0.2
        
        # Adjust based on MACD
        if 'macd' in indicators and not pd.isna(indicators['macd']):
            macd = indicators['macd']
            if macd > 0:  # Positive MACD
                score += 0.1
            else:  # Negative MACD
                score -= 0.1
        
        # Ensure score is between 0 and 1
        score = max(0, min(1, score))
        
        print(f"  Technical score for {symbol}: {score:.2f}")
        return score
        
    except Exception as e:
        print(f"  Error calculating technical score for {symbol}: {e}")
        return 0.5  # Default neutral score

def get_news_sentiment(symbol):
    """Get news sentiment score for a symbol."""
    try:
        from news_analyzer import analyze_news_sentiment
        
        # Get company name from symbol
        company_name = symbol.replace('.NS', '').replace('.BO', '')
        
        # Analyze news sentiment
        sentiment_score = analyze_news_sentiment(company_name)
        
        print(f"  Sentiment score for {symbol}: {sentiment_score:.2f}")
        return sentiment_score
        
    except Exception as e:
        print(f"  Error calculating sentiment score for {symbol}: {e}")
        return 0.5  # Default neutral score

def generate_predictions():
    """Generate predictions for all stocks."""
    # Use reliable stocks instead of all NIFTY_20
    from data_fetcher import RELIABLE_STOCKS
    
    predictions = []
    
    print("🔮 Generating predictions for reliable stocks...")
    
    for symbol in RELIABLE_STOCKS:
        try:
            print(f"\n📊 Processing: {symbol}")
            
            # Get current close price
            current_close = get_today_close(symbol)
            if current_close is None:
                print(f"❌ Skipping {symbol} - no current price data")
                continue
            
            # Get technical analysis
            technical_score = get_technical_score(symbol)
            
            # Get news sentiment
            sentiment_score = get_news_sentiment(symbol)
            
            # Calculate confidence score
            confidence_score = (technical_score + sentiment_score) / 2
            
            # Predict close price (simple prediction based on current price and confidence)
            predicted_close = current_close * (1 + (confidence_score - 0.5) * 0.02)  # ±2% range
            
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
            print(f"✅ Generated prediction for {symbol}: {recommendation} (Confidence: {confidence_score:.2f})")
            
        except Exception as e:
            print(f"❌ Error generating prediction for {symbol}: {e}")
            continue
    
    print(f"\n📈 Generated {len(predictions)} predictions successfully")
    return predictions

def save_predictions_to_file(predictions):
    """Save predictions to a JSON file for later comparison."""
    filename = f"predictions_{datetime.now().strftime('%Y%m%d')}.json"
    
    # Create predictions directory if it doesn't exist
    os.makedirs('predictions', exist_ok=True)
    filepath = os.path.join('predictions', filename)
    
    with open(filepath, 'w') as f:
        json.dump(predictions, f, indent=2)
    
    print(f"Predictions saved to {filepath}")
    return filepath

def create_prediction_email_html(predictions):
    """Create HTML email content for predictions."""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Morning Stock Predictions</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 28px; text-align: center;">🌅 Morning Stock Predictions</h1>
            <p style="margin: 10px 0 0 0; text-align: center; font-size: 16px; opacity: 0.9;">Today's Top 5 Intraday Stock Picks</p>
            <p style="margin: 5px 0 0 0; text-align: center; font-size: 14px; opacity: 0.8;">Generated at {current_time}</p>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="color: #2c3e50; margin-top: 0;">📊 Today's Predictions</h2>
            <p style="margin: 0;">Based on technical analysis and news sentiment analysis.</p>
        </div>
        
        <table style="border-collapse: collapse; width: 100%; margin: 20px 0; font-family: Arial, sans-serif;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">#</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Symbol</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Confidence</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Current Close</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Predicted Close</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Reason</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for pred in predictions:
        confidence_color = '#d4edda' if pred['confidence_score'] >= 2 else '#fff3cd' if pred['confidence_score'] >= 1 else '#f8d7da'
        html += f"""
            <tr style="background-color: {'#f9f9f9' if pred['rank'] % 2 == 0 else 'white'};">
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">{pred['rank']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold; color: #2c3e50;">{pred['symbol']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center; background-color: {confidence_color};">{pred['confidence_score']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">₹{pred['current_close']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right; color: {'#28a745' if pred['predicted_close'] != pred['current_close'] else '#6c757d'};">₹{pred['predicted_close']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: left; font-size: 12px;">{pred['reason']}</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
        
        <div style="background-color: #e8f4fd; padding: 20px; border-radius: 8px; margin-top: 30px;">
            <h3 style="color: #2c3e50; margin-top: 0;">📈 Analysis Methodology</h3>
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Technical Indicators:</strong> MACD, EMA, RSI, Bollinger Bands</li>
                <li><strong>News Sentiment:</strong> Real-time news analysis and sentiment scoring</li>
                <li><strong>Data Source:</strong> Yahoo Finance intraday data (5-minute intervals)</li>
                <li><strong>Confidence Score:</strong> Combined technical and sentiment analysis (0-3 scale)</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
            <p style="margin: 0; color: #6c757d; font-size: 14px;">
                Generated on: {current_time}<br>
                <em>This analysis is for informational purposes only. Please consult with a financial advisor before making investment decisions.</em>
            </p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_prediction_email(predictions, recipient_email):
    """Send prediction email."""
    try:
        service = get_gmail_service()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        subject = f"Morning Stock Predictions - {current_time}"
        
        html_content = create_prediction_email_html(predictions)
        
        message = create_message('me', recipient_email, subject, html_content, is_html=True)
        result = send_message(service, 'me', message)
        
        if result:
            print(f"Prediction email sent successfully to {recipient_email}")
            return True
        else:
            print("Failed to send prediction email")
            return False
            
    except Exception as e:
        print(f"Error sending prediction email: {e}")
        return False

def main():
    """Main function for morning prediction."""
    print("Starting morning prediction process...")
    
    # Set environment variables for API keys
    os.environ['NEWS_API_KEY'] = 'a9ce32b4eece45cdad109310c59be10d'
    os.environ['OPENAI_API_KEY'] = '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'
    
    # Temporarily disable weekend check for testing
    # if datetime.now().weekday() >= 5:  # Saturday or Sunday
    #     print("Weekend detected. Skipping prediction.")
    #     return
    
    try:
        # Generate predictions
        predictions = generate_predictions()
        
        # Save predictions to file
        save_predictions_to_file(predictions)
        
        # Send email (you can configure the recipient email here)
        recipient_email = "gupkes@gmail.com"  # Already updated
        send_prediction_email(predictions, recipient_email)
        
        print("Morning prediction process completed successfully!")
        
    except Exception as e:
        print(f"Error in morning prediction process: {e}")
        # You might want to send an error notification email here

if __name__ == "__main__":
    main() 