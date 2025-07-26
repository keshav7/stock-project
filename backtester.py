import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class StockBacktester:
    def __init__(self, symbols, lookback_days=30):
        self.symbols = symbols
        self.lookback_days = lookback_days
        self.results = {}
        self.max_5m_days = 60
        
    def fetch_historical_data(self, symbol, start_date, end_date, interval='5m'):
        try:
            # For 5-minute data, ensure we're within 60 days
            max_start = datetime.now() - timedelta(days=self.max_5m_days)
            if start_date < max_start:
                start_date = max_start
            if end_date < max_start:
                return None
            df = yf.download(symbol, start=start_date, end=end_date, interval=interval, progress=False)
            if not df.empty:
                df = df.reset_index()
                return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
        return None
    
    def calculate_technical_indicators(self, df):
        if df is None or df.empty:
            return None
        try:
            # Create a copy to avoid modifying original
            df = df.copy()
            
            # Calculate EMA
            df['EMA_12'] = df['Close'].ewm(span=12).mean()
            df['EMA_26'] = df['Close'].ewm(span=26).mean()
            
            # Calculate MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            # Calculate RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Calculate Bollinger Bands - using a safer approach
            close_series = df['Close']
            bb_middle = close_series.rolling(window=20).mean()
            bb_std = close_series.rolling(window=20).std()
            
            df['BB_Middle'] = bb_middle
            df['BB_Upper'] = bb_middle + (bb_std * 2)
            df['BB_Lower'] = bb_middle - (bb_std * 2)
            
            # Volume indicators
            # Fix: df['Volume'] is a DataFrame, so select first column
            volume_series = df['Volume'].iloc[:, 0] if isinstance(df['Volume'], pd.DataFrame) else df['Volume']
            df['Volume_MA'] = volume_series.rolling(window=20).mean()
            df['Volume_Ratio'] = volume_series.astype(float) / df['Volume_MA'].astype(float)
            
            return df
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return None
    
    def generate_prediction_score(self, df):
        if df is None or df.empty:
            return 0
        try:
            score = 0
            latest = df.iloc[-1]
            
            # MACD Analysis - get scalar values using .item()
            try:
                macd_val = latest['MACD'].item() if not pd.isna(latest['MACD']).item() else 0
                macd_signal_val = latest['MACD_Signal'].item() if not pd.isna(latest['MACD_Signal']).item() else 0
                macd_hist_val = latest['MACD_Histogram'].item() if not pd.isna(latest['MACD_Histogram']).item() else 0
                
                if macd_val > macd_signal_val:
                    score += 1
                if macd_hist_val > 0:
                    score += 1
            except:
                pass
                
            # EMA Analysis
            try:
                ema12_val = latest['EMA_12'].item() if not pd.isna(latest['EMA_12']).item() else 0
                ema26_val = latest['EMA_26'].item() if not pd.isna(latest['EMA_26']).item() else 0
                if ema12_val > ema26_val:
                    score += 1
            except:
                pass
                
            # RSI Analysis
            try:
                rsi_val = latest['RSI'].item() if not pd.isna(latest['RSI']).item() else 50
                if 30 < rsi_val < 70:
                    score += 0.5
                elif rsi_val < 30:
                    score += 1
            except:
                pass
                
            # Bollinger Bands Analysis
            try:
                close_val = latest['Close'].item() if not pd.isna(latest['Close']).item() else 0
                bb_middle_val = latest['BB_Middle'].item() if not pd.isna(latest['BB_Middle']).item() else 0
                if close_val > bb_middle_val:
                    score += 0.5
            except:
                pass
                
            # Volume Analysis
            try:
                volume_ratio_val = latest['Volume_Ratio'].item() if not pd.isna(latest['Volume_Ratio']).item() else 1
                if volume_ratio_val > 1.2:
                    score += 0.5
            except:
                pass
                
            return min(score, 3)
        except Exception as e:
            print(f"Error generating prediction score: {e}")
            return 0
    
    def predict_price_range(self, df, confidence_score):
        if df is None or df.empty:
            return None, None, None
        try:
            # Get scalar values using .item()
            current_close = df['Close'].iloc[-1].item() if not pd.isna(df['Close'].iloc[-1]).item() else 0
            volatility = df['Close'].pct_change().std().item() if not pd.isna(df['Close'].pct_change().std()).item() else 0.01
            
            # Base prediction on confidence score
            if confidence_score >= 2.5:
                min_change = 0.01
                max_change = 0.03
                predicted_change = 0.02  # Midpoint for predicted price
            elif confidence_score >= 1.5:
                min_change = 0.005
                max_change = 0.02
                predicted_change = 0.0125  # Midpoint for predicted price
            elif confidence_score >= 0.5:
                min_change = -0.005
                max_change = 0.015
                predicted_change = 0.005  # Midpoint for predicted price
            else:
                min_change = -0.02
                max_change = 0.01
                predicted_change = -0.005  # Midpoint for predicted price
            
            # Adjust for volatility
            volatility_factor = min(volatility * 2, 0.05)
            min_change -= volatility_factor
            max_change += volatility_factor
            predicted_change += (volatility_factor * 0.5)  # Slight adjustment for predicted price
            
            predicted_min = current_close * (1 + min_change)
            predicted_max = current_close * (1 + max_change)
            predicted_price = current_close * (1 + predicted_change)
            
            return predicted_min, predicted_max, predicted_price
        except Exception as e:
            print(f"Error predicting price range: {e}")
            return None, None, None
    
    def check_prediction_accuracy(self, predicted_min, predicted_max, actual_data):
        if actual_data is None or actual_data.empty:
            return False, None, None
        try:
            # Get scalar values using .item()
            actual_high = actual_data['High'].max().item() if not pd.isna(actual_data['High'].max()).item() else 0
            actual_low = actual_data['Low'].min().item() if not pd.isna(actual_data['Low'].min()).item() else 0
            actual_close = actual_data['Close'].iloc[-1].item() if not pd.isna(actual_data['Close'].iloc[-1]).item() else 0
            
            # Check if any price touched the predicted range
            touched_range = (actual_low <= predicted_max and actual_high >= predicted_min)
            
            return touched_range, actual_low, actual_high
        except Exception as e:
            print(f"Error checking prediction accuracy: {e}")
            return False, None, None

    def run_backtest(self, test_days=15):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_days + test_days)
        max_start = datetime.now() - timedelta(days=self.max_5m_days)
        
        print(f"Running backtest from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"Testing {len(self.symbols)} symbols for {test_days} days...")
        print(f"Note: Using 5-minute data (limited to last 60 days by Yahoo Finance)")
        
        all_results = []
        
        for symbol in self.symbols:
            print(f"\nAnalyzing {symbol}...")
            symbol_results = []
            
            for day in range(test_days - 3):
                # Calculate dates
                current_date = end_date - timedelta(days=day)
                train_end = current_date - timedelta(days=4)
                train_start = train_end - timedelta(days=self.lookback_days)
                
                # D-3, D-2, D-1 dates
                d3_date = current_date - timedelta(days=3)
                d2_date = current_date - timedelta(days=2)
                d1_date = current_date - timedelta(days=1)
                
                # Ensure all dates are within the last 60 days
                if any(x < max_start for x in [train_start, train_end, d3_date, d2_date, d1_date]):
                    continue
                
                # Fetch training data (D-4 and earlier)
                train_data = self.fetch_historical_data(symbol, train_start, train_end, '5m')
                
                if train_data is not None and not train_data.empty:
                    # Calculate indicators on training data
                    train_data = self.calculate_technical_indicators(train_data)
                    
                    if train_data is not None:
                        # Generate prediction
                        confidence_score = self.generate_prediction_score(train_data)
                        predicted_min, predicted_max, predicted_price = self.predict_price_range(train_data, confidence_score)
                        
                        if predicted_min and predicted_max and predicted_price:
                            # Test predictions for D-3, D-2, D-1, and D-0 (current day)
                            for test_day, test_date in [(3, d3_date), (2, d2_date), (1, d1_date), (0, current_date)]:
                                if test_date < max_start:
                                    continue
                                    
                                # Fetch actual data for the test day
                                actual_data = self.fetch_historical_data(symbol, test_date, test_date + timedelta(days=1), '5m')
                                
                                if actual_data is not None and not actual_data.empty:
                                    # Check prediction accuracy
                                    touched_range, actual_low, actual_high = self.check_prediction_accuracy(
                                        predicted_min, predicted_max, actual_data
                                    )
                                    
                                    result = {
                                        'symbol': symbol,
                                        'prediction_date': current_date.strftime('%Y-%m-%d'),
                                        'test_day': f'D-{test_day}',
                                        'test_date': test_date.strftime('%Y-%m-%d'),
                                        'confidence_score': confidence_score,
                                        'predicted_price': predicted_price,
                                        'predicted_min': predicted_min,
                                        'predicted_max': predicted_max,
                                        'actual_low': actual_low,
                                        'actual_high': actual_high,
                                        'actual_close': actual_data['Close'].iloc[-1].item() if not pd.isna(actual_data['Close'].iloc[-1]).item() else 0,
                                        'touched_range': touched_range,
                                        'prediction_accuracy': 'HIT' if touched_range else 'MISS'
                                    }
                                    
                                    symbol_results.append(result)
                                    all_results.append(result)
            
            # Store symbol results
            self.results[symbol] = symbol_results
        
        return all_results
    
    def generate_report(self, results):
        if not results:
            return "No results to report."
        
        df = pd.DataFrame(results)
        
        # Overall statistics
        total_predictions = len(df)
        successful_predictions = len(df[df['touched_range'] == True])
        success_rate = (successful_predictions / total_predictions) * 100 if total_predictions > 0 else 0
        
        # Statistics by confidence level
        confidence_stats = df.groupby('confidence_score').agg({
            'touched_range': ['count', 'sum', 'mean']
        }).round(3)
        
        # Statistics by test day
        day_stats = df.groupby('test_day').agg({
            'touched_range': ['count', 'sum', 'mean']
        }).round(3)
        
        # Statistics by symbol
        symbol_stats = df.groupby('symbol').agg({
            'touched_range': ['count', 'sum', 'mean']
        }).round(3)
        
        report = f"""
=== STOCK PREDICTION BACKTEST REPORT ===

Overall Performance:
- Total Predictions: {total_predictions}
- Successful Predictions: {successful_predictions}
- Success Rate: {success_rate:.2f}%

Performance by Confidence Score:
{confidence_stats.to_string()}

Performance by Test Day:
{day_stats.to_string()}

Top Performing Symbols:
{symbol_stats.sort_values(('touched_range', 'mean'), ascending=False).head(10).to_string()}

Detailed Results:
{df[['symbol', 'test_day', 'test_date', 'confidence_score', 'prediction_accuracy']].to_string(index=False)}
        """
        
        return report

def comprehensive_test():
    """Comprehensive test to verify all functions work correctly."""
    print("Running comprehensive test...")
    
    # Test with just one symbol and minimal data
    test_symbols = ['RELIANCE.NS']
    backtester = StockBacktester(test_symbols, lookback_days=5)
    
    # Test data fetching
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    
    print(f"1. Testing data fetch for {test_symbols[0]} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Fetch test data
    test_data = backtester.fetch_historical_data(test_symbols[0], start_date, end_date, '5m')
    
    if test_data is None or test_data.empty:
        print("✗ Data fetch failed")
        return False
    
    print(f"✓ Data fetch successful: {len(test_data)} records")
    print(f"   Columns: {list(test_data.columns)}")
    print(f"   Data types: {test_data.dtypes.to_dict()}")
    
    # Test indicator calculation
    print("\n2. Testing indicator calculation...")
    test_data_with_indicators = backtester.calculate_technical_indicators(test_data)
    
    if test_data_with_indicators is None:
        print("✗ Indicator calculation failed")
        return False
    
    print("✓ Indicator calculation successful")
    print(f"   New columns: {[col for col in test_data_with_indicators.columns if col not in test_data.columns]}")
    
    # Test prediction score
    print("\n3. Testing prediction score generation...")
    try:
        score = backtester.generate_prediction_score(test_data_with_indicators)
        print(f"✓ Prediction score generated: {score}")
    except Exception as e:
        print(f"✗ Prediction score failed: {e}")
        return False
    
    # Test price range prediction
    print("\n4. Testing price range prediction...")
    try:
        pred_min, pred_max, pred_price = backtester.predict_price_range(test_data_with_indicators, score)
        if pred_min and pred_max and pred_price:
            print(f"✓ Price range prediction successful: {pred_min:.2f} - {pred_max:.2f}")
            print(f"✓ Predicted price: {pred_price:.2f}")
        else:
            print("✗ Price range prediction returned None values")
            return False
    except Exception as e:
        print(f"✗ Price range prediction failed: {e}")
        return False
    
    # Test prediction accuracy check
    print("\n5. Testing prediction accuracy check...")
    try:
        # Use the same data as "actual" for testing
        touched, actual_low, actual_high = backtester.check_prediction_accuracy(pred_min, pred_max, test_data)
        print(f"✓ Prediction accuracy check successful: touched={touched}, low={actual_low:.2f}, high={actual_high:.2f}")
    except Exception as e:
        print(f"✗ Prediction accuracy check failed: {e}")
        return False
    
    # Test a small backtest loop
    print("\n6. Testing small backtest loop...")
    try:
        # Simulate one iteration of the backtest
        current_date = end_date - timedelta(days=1)
        train_end = current_date - timedelta(days=4)
        train_start = train_end - timedelta(days=5)
        
        train_data = backtester.fetch_historical_data(test_symbols[0], train_start, train_end, '5m')
        if train_data is not None and not train_data.empty:
            train_data = backtester.calculate_technical_indicators(train_data)
            if train_data is not None:
                confidence_score = backtester.generate_prediction_score(train_data)
                predicted_min, predicted_max, predicted_price = backtester.predict_price_range(train_data, confidence_score)
                if predicted_min and predicted_max and predicted_price:
                    # Test with actual data
                    test_date = current_date - timedelta(days=1)
                    actual_data = backtester.fetch_historical_data(test_symbols[0], test_date, test_date + timedelta(days=1), '5m')
                    if actual_data is not None and not actual_data.empty:
                        touched_range, actual_low, actual_high = backtester.check_prediction_accuracy(
                            predicted_min, predicted_max, actual_data
                        )
                        print(f"✓ Small backtest loop successful: confidence={confidence_score}, touched={touched_range}")
                    else:
                        print("✗ Small backtest loop failed: no actual data")
                        return False
                else:
                    print("✗ Small backtest loop failed: no price predictions")
                    return False
            else:
                print("✗ Small backtest loop failed: no indicators")
                return False
        else:
            print("✗ Small backtest loop failed: no training data")
            return False
    except Exception as e:
        print(f"✗ Small backtest loop failed: {e}")
        return False
    
    print("\n✓ All comprehensive tests passed! Ready to run full backtest.")
    return True

def main():
    # Use only HDFC Bank stock for this backtest (HDFC merged with HDFC Bank)
    symbols = ['HDFCBANK.NS']
    
    # First run comprehensive test
    if comprehensive_test():
        # Initialize backtester
        backtester = StockBacktester(symbols, lookback_days=30)
        
        # Run backtest
        print("\nStarting backtest for HDFC Bank stock...")
        results = backtester.run_backtest(test_days=15)
        
        # Generate and print report
        report = backtester.generate_report(results)
        print(report)
        
        # Save results to file
        if results:
            df = pd.DataFrame(results)
            df.to_csv('backtest_results.csv', index=False)
            print(f"\nDetailed results saved to 'backtest_results.csv'")
        
        return results, report
    else:
        print("Comprehensive test failed. Please fix the issues before running full backtest.")
        return None, None

if __name__ == "__main__":
    main() 