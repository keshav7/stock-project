#!/usr/bin/env python3
"""
Test script to run full prediction generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from morning_prediction import generate_predictions
import json

def test_full_prediction():
    """Test the full prediction generation process."""
    print("🔮 Testing Full Prediction Generation")
    print("=" * 50)
    
    try:
        # Generate predictions
        print("Generating predictions...")
        predictions = generate_predictions()
        
        print(f"\nGenerated {len(predictions)} predictions:")
        print("-" * 50)
        
        for i, pred in enumerate(predictions, 1):
            print(f"\n{i}. {pred['symbol']}")
            print(f"   Confidence: {pred['confidence_score']}")
            print(f"   Current Close: {pred['current_close']}")
            print(f"   Predicted Close: {pred['predicted_close']}")
            print(f"   Reason: {pred['reason']}")
        
        # Save to file for inspection
        filename = f"test_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(predictions, f, indent=2)
        print(f"\nPredictions saved to: {filename}")
        
        return predictions
        
    except Exception as e:
        print(f"Error generating predictions: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    from datetime import datetime
    test_full_prediction() 