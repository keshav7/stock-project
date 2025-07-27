#!/usr/bin/env python3
"""
Stock Prediction API Server
Provides REST API endpoints for stock predictions and evaluations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import logging
import os
from datetime import datetime

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api_server.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Default email for predictions
DEFAULT_EMAIL = "gupkes@gmail.com"

def set_api_keys():
    """Set API keys from environment variables or use defaults."""
    logger.info("🔑 Setting up API keys")
    
    # Try to get from environment variables first
    news_api_key = os.environ.get('NEWS_API_KEY')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    if not news_api_key:
        logger.warning("⚠️ NEWS_API_KEY not found in environment, using default")
        news_api_key = 'a9ce32b4eece45cdad109310c59be10d'
    
    if not openai_api_key:
        logger.warning("⚠️ OPENAI_API_KEY not found in environment, using default")
        openai_api_key = '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'
    
    # Set environment variables
    os.environ['NEWS_API_KEY'] = news_api_key
    os.environ['OPENAI_API_KEY'] = openai_api_key
    
    logger.info("✅ API keys configured successfully")

def run_prediction_task(recipient_email):
    """Run prediction task in a separate thread."""
    logger.info(f"🚀 Starting prediction task for {recipient_email}")
    try:
        from morning_prediction import generate_predictions, create_prediction_email_html
        from email_sender import send_email
        
        # Generate predictions
        logger.info("🔮 Generating predictions...")
        predictions = generate_predictions()
        
        if not predictions:
            logger.error("❌ No predictions generated!")
            return False
        
        logger.info(f"✅ Generated {len(predictions)} predictions")
        
        # Save predictions to file
        logger.info("💾 Saving predictions to file...")
        os.makedirs('predictions', exist_ok=True)
        filename = f"predictions/predictions_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w') as f:
            import json
            json.dump(predictions, f, indent=2)
        
        logger.info(f"✅ Predictions saved to {filename}")
        
        # Create email content
        logger.info("📧 Creating email content...")
        email_html = create_prediction_email_html(predictions)
        
        # Send email
        logger.info("📤 Sending prediction email...")
        subject = f"Stock Predictions - {datetime.now().strftime('%Y-%m-%d')}"
        
        message_id = send_email(recipient_email, subject, email_html)
        logger.info(f"✅ Prediction email sent successfully to {recipient_email}")
        logger.info(f"📧 Message ID: {message_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in prediction task: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def run_evaluation_task(recipient_email):
    """Run evaluation task in a separate thread."""
    logger.info(f"🚀 Starting evaluation task for {recipient_email}")
    try:
        from evening_evaluation import evaluate_predictions, create_evaluation_email_html
        from email_sender import send_email
        
        # Evaluate predictions
        logger.info("📊 Evaluating predictions...")
        evaluation_results = evaluate_predictions()
        
        if not evaluation_results:
            logger.error("❌ No evaluation results generated!")
            return False
        
        logger.info(f"✅ Generated {len(evaluation_results)} evaluation results")
        
        # Save evaluation results to file
        logger.info("💾 Saving evaluation results to file...")
        os.makedirs('evaluations', exist_ok=True)
        filename = f"evaluations/evaluations_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w') as f:
            import json
            json.dump(evaluation_results, f, indent=2)
        
        logger.info(f"✅ Evaluation results saved to {filename}")
        
        # Create email content
        logger.info("📧 Creating evaluation email content...")
        email_html = create_evaluation_email_html(evaluation_results)
        
        # Send email
        logger.info("📤 Sending evaluation email...")
        subject = f"Stock Predictions Evaluation - {datetime.now().strftime('%Y-%m-%d')}"
        
        message_id = send_email(recipient_email, subject, email_html)
        logger.info(f"✅ Evaluation email sent successfully to {recipient_email}")
        logger.info(f"📧 Message ID: {message_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in evaluation task: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

@app.route('/')
def home():
    """Home endpoint with API documentation."""
    logger.info("🏠 Home endpoint accessed")
    return jsonify({
        "message": "Stock Prediction API",
        "version": "1.0",
        "deployment": "Railway",
        "endpoints": {
            "/": "API Documentation (this page)",
            "/health": "Health check",
            "/status": "API status and configuration",
            "/predict": "Generate stock predictions and send email (POST)",
            "/evaluate": "Evaluate predictions and send email (POST)"
        },
        "usage": {
            "predict": "POST /predict with optional JSON body: {\"recipient_email\": \"user@example.com\"}",
            "evaluate": "POST /evaluate with optional JSON body: {\"recipient_email\": \"user@example.com\"}"
        },
        "default_email": DEFAULT_EMAIL,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    logger.info("🏥 Health check endpoint accessed")
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "deployment": "Railway"
    })

@app.route('/status')
def status():
    """API status endpoint."""
    logger.info("📊 Status endpoint accessed")
    
    # Check if API keys are set
    news_api_key = os.environ.get('NEWS_API_KEY')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    return jsonify({
        "status": "running",
        "deployment": "Railway",
        "timestamp": datetime.now().isoformat(),
        "configuration": {
            "default_email": DEFAULT_EMAIL,
            "news_api_key_set": bool(news_api_key),
            "openai_api_key_set": bool(openai_api_key),
            "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'production')
        },
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "predict": "/predict",
            "evaluate": "/evaluate"
        }
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Generate predictions and send email."""
    logger.info("🔮 Predict endpoint accessed")
    
    try:
        # Get recipient email from request or use default
        data = request.get_json() if request.is_json else {}
        recipient_email = data.get('recipient_email', DEFAULT_EMAIL)
        
        logger.info(f"📧 Using recipient email: {recipient_email}")
        
        # Set API keys
        set_api_keys()
        
        # Run prediction task in background
        logger.info("🔄 Starting prediction task in background thread")
        thread = threading.Thread(target=run_prediction_task, args=(recipient_email,))
        thread.daemon = True
        thread.start()
        
        logger.info("✅ Prediction task started successfully")
        
        return jsonify({
            "message": "Prediction task started successfully",
            "recipient_email": recipient_email,
            "email_sent": True,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error in predict endpoint: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            "error": str(e),
            "message": "Failed to start prediction task",
            "email_sent": False,
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/evaluate', methods=['POST'])
def evaluate():
    """Evaluate predictions and send email."""
    logger.info("📊 Evaluate endpoint accessed")
    
    try:
        # Get recipient email from request or use default
        data = request.get_json() if request.is_json else {}
        recipient_email = data.get('recipient_email', DEFAULT_EMAIL)
        
        logger.info(f"📧 Using recipient email: {recipient_email}")
        
        # Set API keys
        set_api_keys()
        
        # Run evaluation task in background
        logger.info("🔄 Starting evaluation task in background thread")
        thread = threading.Thread(target=run_evaluation_task, args=(recipient_email,))
        thread.daemon = True
        thread.start()
        
        logger.info("✅ Evaluation task started successfully")
        
        return jsonify({
            "message": "Evaluation task started successfully",
            "recipient_email": recipient_email,
            "email_sent": True,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error in evaluate endpoint: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            "error": str(e),
            "message": "Failed to start evaluation task",
            "email_sent": False,
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Stock Prediction API Server...")
    logger.info(f"📧 Default email: {DEFAULT_EMAIL}")
    logger.info("🌐 API will be available at: http://localhost:5000")
    logger.info("📖 API Documentation: http://localhost:5000/")
    
    # Set API keys on startup
    set_api_keys()
    
    # Run the app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False) 