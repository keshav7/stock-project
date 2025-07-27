#!/usr/bin/env python3
"""
Evening Evaluation Script - Runs at 5 PM IST on weekdays
Compares morning predictions with actual day's performance and sends results via email
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
from email_sender import get_gmail_service, create_message, send_message
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yfinance as yf

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('evening_evaluation.log')
    ]
)
logger = logging.getLogger(__name__)

def safe_scalar(val):
    """Convert pandas/numpy values to scalar safely."""
    if hasattr(val, 'item'):
        val = val.item() if hasattr(val, 'size') and val.size == 1 else None
    if val is None or pd.isna(val):
        return '-'
    return f"{val:.2f}" if isinstance(val, (float, int)) else str(val)

def get_today_performance(symbol):
    """Get today's actual performance for a symbol."""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        df = yf.download(symbol, start=today, end=today, interval='1d', progress=False)
        
        if df.empty:
            return None, None, None, None
        
        open_price = df['Open'].iloc[0]
        close_price = df['Close'].iloc[0]
        high_price = df['High'].iloc[0]
        low_price = df['Low'].iloc[0]
        
        return open_price, close_price, high_price, low_price
        
    except Exception as e:
        print(f"Error getting performance for {symbol}: {e}")
        return None, None, None, None

def evaluate_prediction(prediction, actual_open, actual_close, actual_high, actual_low):
    """Evaluate if the prediction was correct."""
    if actual_close is None or prediction['predicted_close'] == '-':
        return 'NO_DATA'
    
    try:
        predicted_close = float(prediction['predicted_close'])
        actual_close_val = float(actual_close)
        
        # Calculate the percentage difference
        diff_percentage = abs(predicted_close - actual_close_val) / actual_close_val * 100
        
        # Consider it a HIT if the prediction is within 2% of actual close
        if diff_percentage <= 2.0:
            return 'HIT'
        else:
            return 'MISS'
            
    except (ValueError, TypeError):
        return 'ERROR'

def load_predictions_from_file(date_str=None):
    """Load predictions from the JSON file for a specific date."""
    if date_str is None:
        date_str = datetime.now().strftime('%Y%m%d')
    
    filename = f"predictions_{date_str}.json"
    filepath = os.path.join('predictions', filename)
    
    if not os.path.exists(filepath):
        print(f"Prediction file not found: {filepath}")
        return None
    
    try:
        with open(filepath, 'r') as f:
            predictions = json.load(f)
        return predictions
    except Exception as e:
        print(f"Error loading predictions: {e}")
        return None

def evaluate_all_predictions(predictions):
    """Evaluate all predictions for the day."""
    evaluations = []
    
    for pred in predictions:
        symbol = pred['symbol']
        open_price, close_price, high_price, low_price = get_today_performance(symbol)
        
        result = evaluate_prediction(pred, open_price, close_price, high_price, low_price)
        
        evaluation = {
            'rank': pred['rank'],
            'symbol': symbol,
            'confidence_score': pred['confidence_score'],
            'predicted_close': pred['predicted_close'],
            'actual_open': safe_scalar(open_price),
            'actual_close': safe_scalar(close_price),
            'actual_high': safe_scalar(high_price),
            'actual_low': safe_scalar(low_price),
            'result': result,
            'reason': pred['reason']
        }
        
        evaluations.append(evaluation)
    
    return evaluations

def create_evaluation_email_html(evaluations):
    """Create HTML email content for evaluation results."""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Calculate statistics
    total_predictions = len(evaluations)
    hits = len([e for e in evaluations if e['result'] == 'HIT'])
    misses = len([e for e in evaluations if e['result'] == 'MISS'])
    no_data = len([e for e in evaluations if e['result'] == 'NO_DATA'])
    errors = len([e for e in evaluations if e['result'] == 'ERROR'])
    
    success_rate = (hits / (hits + misses)) * 100 if (hits + misses) > 0 else 0
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Evening Stock Evaluation</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 28px; text-align: center;">🌆 Evening Stock Evaluation</h1>
            <p style="margin: 10px 0 0 0; text-align: center; font-size: 16px; opacity: 0.9;">Today's Prediction Results</p>
            <p style="margin: 5px 0 0 0; text-align: center; font-size: 14px; opacity: 0.8;">Evaluated at {current_time}</p>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="color: #2c3e50; margin-top: 0;">📊 Today's Performance Summary</h2>
            <div style="display: flex; justify-content: space-around; text-align: center; margin: 20px 0;">
                <div style="background-color: #d4edda; padding: 15px; border-radius: 8px; min-width: 120px;">
                    <h3 style="margin: 0; color: #155724;">HITS</h3>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold;">{hits}</p>
                </div>
                <div style="background-color: #f8d7da; padding: 15px; border-radius: 8px; min-width: 120px;">
                    <h3 style="margin: 0; color: #721c24;">MISSES</h3>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold;">{misses}</p>
                </div>
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; min-width: 120px;">
                    <h3 style="margin: 0; color: #856404;">SUCCESS RATE</h3>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold;">{success_rate:.1f}%</p>
                </div>
            </div>
        </div>
        
        <table style="border-collapse: collapse; width: 100%; margin: 20px 0; font-family: Arial, sans-serif;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">#</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Symbol</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Confidence</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Predicted</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Actual Close</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">High</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Low</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Result</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for eval_item in evaluations:
        result_color = '#d4edda' if eval_item['result'] == 'HIT' else '#f8d7da' if eval_item['result'] == 'MISS' else '#fff3cd'
        result_text = eval_item['result']
        
        html += f"""
            <tr style="background-color: {'#f9f9f9' if eval_item['rank'] % 2 == 0 else 'white'};">
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">{eval_item['rank']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold; color: #2c3e50;">{eval_item['symbol']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center;">{eval_item['confidence_score']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">₹{eval_item['predicted_close']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">₹{eval_item['actual_close']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">₹{eval_item['actual_high']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">₹{eval_item['actual_low']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center; background-color: {result_color}; font-weight: bold;">{result_text}</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
        
        <div style="background-color: #e8f4fd; padding: 20px; border-radius: 8px; margin-top: 30px;">
            <h3 style="color: #2c3e50; margin-top: 0;">📈 Evaluation Criteria</h3>
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>HIT:</strong> Predicted close price is within 2% of actual close price</li>
                <li><strong>MISS:</strong> Predicted close price differs by more than 2% from actual close price</li>
                <li><strong>NO_DATA:</strong> Unable to fetch actual market data for comparison</li>
                <li><strong>ERROR:</strong> Error occurred during evaluation</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
            <p style="margin: 0; color: #6c757d; font-size: 14px;">
                Evaluated on: {current_time}<br>
                <em>This evaluation is for informational purposes only. Past performance does not guarantee future results.</em>
            </p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_evaluation_email(evaluations, recipient_email):
    """Send evaluation email."""
    try:
        service = get_gmail_service()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        subject = f"Evening Stock Evaluation - {current_time}"
        
        html_content = create_evaluation_email_html(evaluations)
        
        message = create_message('me', recipient_email, subject, html_content, is_html=True)
        result = send_message(service, 'me', message)
        
        if result:
            print(f"Evaluation email sent successfully to {recipient_email}")
            return True
        else:
            print("Failed to send evaluation email")
            return False
            
    except Exception as e:
        print(f"Error sending evaluation email: {e}")
        return False

def save_evaluation_results(evaluations):
    """Save evaluation results to a JSON file."""
    filename = f"evaluations_{datetime.now().strftime('%Y%m%d')}.json"
    
    # Create evaluations directory if it doesn't exist
    os.makedirs('evaluations', exist_ok=True)
    filepath = os.path.join('evaluations', filename)
    
    with open(filepath, 'w') as f:
        json.dump(evaluations, f, indent=2)
    
    print(f"Evaluation results saved to {filepath}")
    return filepath

def evaluate_predictions():
    """Evaluate predictions for the current day."""
    logger.info("🌅 Starting evening evaluation process...")
    
    # Check if it's a weekday (Monday = 0, Sunday = 6)
    if datetime.now().weekday() >= 5:  # Saturday or Sunday
        logger.info("📅 Weekend detected. Skipping evaluation.")
        return []
    
    try:
        # Load today's predictions
        logger.info("📂 Loading today's predictions...")
        predictions = load_predictions_from_file()
        
        if predictions is None:
            logger.warning("⚠️ No predictions found for today. Skipping evaluation.")
            return []
        
        logger.info(f"✅ Loaded {len(predictions)} predictions for evaluation")
        
        # Evaluate predictions
        logger.info("📊 Evaluating predictions...")
        evaluations = evaluate_all_predictions(predictions)
        
        # Save evaluation results
        logger.info("💾 Saving evaluation results...")
        save_evaluation_results(evaluations)
        
        logger.info("✅ Evening evaluation process completed successfully!")
        return evaluations
        
    except Exception as e:
        logger.error(f"❌ Error in evening evaluation process: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []

def main():
    """Main function for evening evaluation."""
    print("Starting evening evaluation process...")
    
    # Check if it's a weekday (Monday = 0, Sunday = 6)
    if datetime.now().weekday() >= 5:  # Saturday or Sunday
        print("Weekend detected. Skipping evaluation.")
        return
    
    try:
        # Load today's predictions
        predictions = load_predictions_from_file()
        
        if predictions is None:
            print("No predictions found for today. Skipping evaluation.")
            return
        
        # Evaluate predictions
        evaluations = evaluate_all_predictions(predictions)
        
        # Save evaluation results
        save_evaluation_results(evaluations)
        
        # Send email (you can configure the recipient email here)
        recipient_email = "gupkes@gmail.com"  # Change this to your email
        send_evaluation_email(evaluations, recipient_email)
        
        print("Evening evaluation process completed successfully!")
        
    except Exception as e:
        print(f"Error in evening evaluation process: {e}")
        # You might want to send an error notification email here

if __name__ == "__main__":
    main() 