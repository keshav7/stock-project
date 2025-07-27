import os
import json
import base64
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from datetime import datetime
import re

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Get Gmail service with proper authentication."""
    creds = None
    
    # Load credentials from the provided JSON
    credentials_data = {
        "installed": {
            "client_id": "98125166614-l06f896e1rd7j9jh31v52sq67p217nq2.apps.googleusercontent.com",
            "project_id": "gmail-agent-keshav",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "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",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    # Save credentials to a temporary file
    with open('temp_credentials.json', 'w') as f:
        json.dump(credentials_data, f)
    
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'temp_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Clean up temporary file
    os.remove('temp_credentials.json')
    
    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text, is_html=True):
    """Create a message for an email."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    if is_html:
        msg = MIMEText(message_text, 'html')
    else:
        msg = MIMEText(message_text, 'plain')
    message.attach(msg)
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """Send an email message."""
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f'Message Id: {message["id"]}')
        return message
    except Exception as error:
        print(f'An error occurred: {error}')
        return None

def get_stock_analysis_output():
    """Run the main.py script and capture its output."""
    try:
        # Set the NEWS_API_KEY environment variable
        env = os.environ.copy()
        env['NEWS_API_KEY'] = 'a9ce32b4eece45cdad109310c59be10d'
        
        # Run the main.py script and capture output
        result = subprocess.run(['python3', 'main.py'], 
                              capture_output=True, text=True, env=env)
        
        return result.stdout
    except Exception as e:
        print(f"Error running main.py: {e}")
        return None

def parse_stock_recommendations(output):
    """Parse the stock recommendations from the output and return structured data."""
    recommendations = []
    
    # Find the recommendations table in the output
    lines = output.split('\n')
    in_table = False
    
    for line in lines:
        if 'Tomorrow\'s Top 5 Intraday Stock Picks:' in line:
            in_table = True
            continue
        elif in_table and line.strip() and not line.startswith('#'):
            # Parse each recommendation line
            parts = line.split()
            if len(parts) >= 8:
                try:
                    rank = parts[0]
                    symbol = parts[1]
                    conf = parts[2]
                    close = parts[3]
                    pred_close = parts[4]
                    next_min = parts[5]
                    next_max = parts[6]
                    reason = ' '.join(parts[7:])
                    
                    recommendations.append({
                        'rank': rank,
                        'symbol': symbol,
                        'confidence': conf,
                        'close': close,
                        'pred_close': pred_close,
                        'next_min': next_min,
                        'next_max': next_max,
                        'reason': reason
                    })
                except:
                    continue
    
    return recommendations

def create_html_table(recommendations):
    """Create an HTML table from the recommendations."""
    html = """
    <table style="border-collapse: collapse; width: 100%; margin: 20px 0; font-family: Arial, sans-serif;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">#</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Symbol</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Confidence</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Close</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Pred Close</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Next Min</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Next Max</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Reason</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for rec in recommendations:
        html += f"""
            <tr style="background-color: {'#f9f9f9' if int(rec['rank']) % 2 == 0 else 'white'};">
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">{rec['rank']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold; color: #2c3e50;">{rec['symbol']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center; background-color: {'#d4edda' if float(rec['confidence']) >= 2 else '#fff3cd' if float(rec['confidence']) >= 1 else '#f8d7da'};">{rec['confidence']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">₹{rec['close']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right; color: {'#28a745' if rec['pred_close'] != rec['close'] else '#6c757d'};">₹{rec['pred_close']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">{rec['next_min']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">{rec['next_max']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: left; font-size: 12px;">{rec['reason']}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    
    return html

def send_email(recipient_email, subject, html_content):
    """Send an email with the given content."""
    try:
        # Get Gmail service
        service = get_gmail_service()
        
        # Create and send message
        message = create_message('me', recipient_email, subject, html_content, is_html=True)
        result = send_message(service, 'me', message)
        
        if result:
            print(f"Email sent successfully to {recipient_email}")
            return result.get('id', 'unknown')
        else:
            print("Failed to send email")
            return None
            
    except Exception as e:
        print(f"Error sending email: {e}")
        return None

def send_stock_analysis_results(recipient_email):
    """Send stock analysis results via email."""
    try:
        # Get the actual output from main.py
        analysis_output = get_stock_analysis_output()
        
        if not analysis_output:
            print("Failed to get analysis output")
            return False
        
        # Parse recommendations
        recommendations = parse_stock_recommendations(analysis_output)
        
        # Get Gmail service
        service = get_gmail_service()
        
        # Create email content
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        subject = f"Stock Analysis Results - {current_time}"
        
        # Create HTML email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Stock Analysis Results</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 28px; text-align: center;">📈 Stock Analysis Results</h1>
                <p style="margin: 10px 0 0 0; text-align: center; font-size: 16px; opacity: 0.9;">Tomorrow's Top 5 Intraday Stock Picks</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #2c3e50; margin-top: 0;">🎯 Recommendations Summary</h2>
                <p style="margin: 0;">Analysis completed using advanced technical indicators and sentiment analysis.</p>
            </div>
            
            {create_html_table(recommendations)}
            
            <div style="background-color: #e8f4fd; padding: 20px; border-radius: 8px; margin-top: 30px;">
                <h3 style="color: #2c3e50; margin-top: 0;">📊 Analysis Methodology</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Technical Indicators:</strong> MACD (Moving Average Convergence Divergence), EMA (Exponential Moving Average)</li>
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
        
        # Create and send message
        message = create_message('me', recipient_email, subject, html_content, is_html=True)
        result = send_message(service, 'me', message)
        
        if result:
            print(f"Email sent successfully to {recipient_email}")
            return True
        else:
            print("Failed to send email")
            return False
            
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

if __name__ == "__main__":
    # You can change this to your email address
    recipient_email = input("Enter your email address: ")
    send_stock_analysis_results(recipient_email) 