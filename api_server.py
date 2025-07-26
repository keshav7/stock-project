#!/usr/bin/env python3
"""
Stock Prediction API Server
Provides REST API endpoints for stock predictions and evaluations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
import threading
import time

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our prediction modules
from morning_prediction import generate_predictions, save_predictions_to_file, send_prediction_email
from evening_evaluation import load_predictions_from_file, evaluate_all_predictions, save_evaluation_results, send_evaluation_email

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables to track API status
api_status = {
    "last_prediction_time": None,
    "last_evaluation_time": None,
    "is_running_prediction": False,
    "is_running_evaluation": False,
    "prediction_count": 0,
    "evaluation_count": 0
}

def set_api_keys():
    """Set environment variables for API keys from environment or use defaults."""
    # Get API keys from environment variables (for production) or use defaults
    news_api_key = os.environ.get('NEWS_API_KEY', 'a9ce32b4eece45cdad109310c59be10d')
    openai_api_key = os.environ.get('OPENAI_API_KEY', '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')
    
    os.environ['NEWS_API_KEY'] = news_api_key
    os.environ['OPENAI_API_KEY'] = openai_api_key

@app.route('/')
def home():
    """Home endpoint with API information."""
    return jsonify({
        "message": "Stock Prediction API",
        "version": "1.0.0",
        "deployment": "Render",
        "endpoints": {
            "GET /": "API information",
            "POST /predict": "Generate stock predictions and send email",
            "POST /evaluate": "Evaluate today's predictions and send email",
            "GET /status": "Get API status",
            "GET /predictions/<date>": "Get predictions for a specific date",
            "GET /evaluations/<date>": "Get evaluations for a specific date"
        },
        "status": api_status
    })

@app.route('/status')
def get_status():
    """Get current API status."""
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "api_status": api_status
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Generate stock predictions and send email."""
    if api_status["is_running_prediction"]:
        return jsonify({
            "error": "Prediction already in progress",
            "status": "busy"
        }), 409
    
    try:
        # Get email from request body, default to configured email
        recipient_email = 'gupkes@gmail.com'
        if request.is_json:
            data = request.get_json() or {}
            recipient_email = data.get('email', 'gupkes@gmail.com')
        
        # Set API keys
        set_api_keys()
        
        # Update status
        api_status["is_running_prediction"] = True
        api_status["last_prediction_time"] = datetime.now().isoformat()
        
        # Run prediction in a separate thread to avoid blocking
        def run_prediction():
            try:
                # Generate predictions
                predictions = generate_predictions()
                
                # Save predictions to file
                save_predictions_to_file(predictions)
                
                # Send email
                send_prediction_email(predictions, recipient_email)
                
                # Update status
                api_status["prediction_count"] += 1
                
            except Exception as e:
                print(f"Error in prediction thread: {e}")
            finally:
                api_status["is_running_prediction"] = False
        
        # Start prediction thread
        thread = threading.Thread(target=run_prediction)
        thread.start()
        
        return jsonify({
            "message": "Prediction started",
            "email": recipient_email,
            "status": "processing",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        api_status["is_running_prediction"] = False
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/evaluate', methods=['POST'])
def evaluate():
    """Evaluate today's predictions and send email."""
    if api_status["is_running_evaluation"]:
        return jsonify({
            "error": "Evaluation already in progress",
            "status": "busy"
        }), 409
    
    try:
        # Get email from request body, default to configured email
        recipient_email = 'gupkes@gmail.com'
        if request.is_json:
            data = request.get_json() or {}
            recipient_email = data.get('email', 'gupkes@gmail.com')
        
        # Set API keys
        set_api_keys()
        
        # Update status
        api_status["is_running_evaluation"] = True
        api_status["last_evaluation_time"] = datetime.now().isoformat()
        
        # Run evaluation in a separate thread to avoid blocking
        def run_evaluation():
            try:
                # Load today's predictions
                predictions = load_predictions_from_file()
                
                if predictions is None:
                    print("No predictions found for today")
                    return
                
                # Evaluate predictions
                evaluations = evaluate_all_predictions(predictions)
                
                # Save evaluation results
                save_evaluation_results(evaluations)
                
                # Send email
                send_evaluation_email(evaluations, recipient_email)
                
                # Update status
                api_status["evaluation_count"] += 1
                
            except Exception as e:
                print(f"Error in evaluation thread: {e}")
            finally:
                api_status["is_running_evaluation"] = False
        
        # Start evaluation thread
        thread = threading.Thread(target=run_evaluation)
        thread.start()
        
        return jsonify({
            "message": "Evaluation started",
            "email": recipient_email,
            "status": "processing",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        api_status["is_running_evaluation"] = False
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/predictions/<date>')
def get_predictions(date):
    """Get predictions for a specific date."""
    try:
        # Load predictions from file
        predictions = load_predictions_from_file(date)
        
        if predictions is None:
            return jsonify({
                "error": f"No predictions found for date: {date}",
                "status": "not_found"
            }), 404
        
        return jsonify({
            "date": date,
            "predictions": predictions,
            "count": len(predictions),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/evaluations/<date>')
def get_evaluations(date):
    """Get evaluations for a specific date."""
    try:
        # Load evaluations from file
        filename = f"evaluations_{date}.json"
        filepath = os.path.join('evaluations', filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                "error": f"No evaluations found for date: {date}",
                "status": "not_found"
            }), 404
        
        with open(filepath, 'r') as f:
            evaluations = json.load(f)
        
        return jsonify({
            "date": date,
            "evaluations": evaluations,
            "count": len(evaluations),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "status": "not_found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Stock Prediction API Server...")
    print("📧 Default email: gupkes@gmail.com")
    print("🌐 API will be available at: http://localhost:5000")
    print("📖 API Documentation: http://localhost:5000/")
    
    # Set API keys
    set_api_keys()
    
    # Get port from environment variable (for Render) or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False) 