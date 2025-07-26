#!/usr/bin/env python3
"""
Test script for simplified prediction approach
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from morning_prediction import generate_predictions
import json
from datetime import datetime

def test_simplified_prediction():
    """Test the simplified prediction approach."""
    print("🔮 Testing Simplified Prediction Approach")
    print("=" * 50)
    
    try:
        # Generate predictions
        print("Generating predictions...")
        predictions = generate_predictions()
        
        if not predictions:
            print("❌ No predictions generated")
            return
        
        print(f"\n✅ Generated {len(predictions)} predictions:")
        print("-" * 50)
        
        for i, pred in enumerate(predictions, 1):
            print(f"\n{i}. {pred['symbol']}")
            print(f"   Current Close: {pred['current_close']}")
            print(f"   Predicted Close: {pred['predicted_close']}")
            print(f"   Confidence: {pred['confidence_score']}")
            print(f"   Technical Score: {pred['technical_score']}")
            print(f"   Sentiment Score: {pred['sentiment_score']}")
            print(f"   Recommendation: {pred['recommendation']}")
            print(f"   Reason: {pred['reason']}")
        
        # Save to file for inspection
        filename = f"test_simplified_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(predictions, f, indent=2)
        print(f"\nPredictions saved to: {filename}")
        
        return predictions
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_simplified_prediction() 