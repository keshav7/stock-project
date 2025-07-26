#!/bin/bash

# Setup script for Stock Prediction Cron Jobs
# This script helps you set up automated morning predictions and evening evaluations

echo "🚀 Setting up Stock Prediction Cron Jobs"
echo "========================================"

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Script directory: $SCRIPT_DIR"

# Make the Python scripts executable
chmod +x "$SCRIPT_DIR/morning_prediction.py"
chmod +x "$SCRIPT_DIR/evening_evaluation.py"

echo ""
echo "📧 Email Configuration"
echo "======================"
echo "Please enter your email address to receive the prediction and evaluation emails:"
read -p "Email address: " EMAIL_ADDRESS

# Update email addresses in the scripts
echo "Updating email addresses in scripts..."

# Update morning prediction script
sed -i.bak "s/your-email@example.com/$EMAIL_ADDRESS/g" "$SCRIPT_DIR/morning_prediction.py"

# Update evening evaluation script
sed -i.bak "s/your-email@example.com/$EMAIL_ADDRESS/g" "$SCRIPT_DIR/evening_evaluation.py"

echo "✅ Email addresses updated in scripts"

echo ""
echo "⏰ Cron Job Setup"
echo "================"
echo "The following cron jobs will be created:"
echo "1. Morning Prediction: Runs at 8:30 AM IST (Mon-Fri)"
echo "2. Evening Evaluation: Runs at 5:00 PM IST (Mon-Fri)"
echo ""

# Create cron job entries
MORNING_CRON="30 8 * * 1-5 cd $SCRIPT_DIR && /usr/bin/python3 $SCRIPT_DIR/morning_prediction.py >> $SCRIPT_DIR/logs/morning_prediction.log 2>&1"
EVENING_CRON="0 17 * * 1-5 cd $SCRIPT_DIR && /usr/bin/python3 $SCRIPT_DIR/evening_evaluation.py >> $SCRIPT_DIR/logs/evening_evaluation.log 2>&1"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

echo "Creating cron job entries..."

# Check if cron jobs already exist
if crontab -l 2>/dev/null | grep -q "morning_prediction.py"; then
    echo "⚠️  Morning prediction cron job already exists"
else
    # Add morning cron job
    (crontab -l 2>/dev/null; echo "$MORNING_CRON") | crontab -
    echo "✅ Morning prediction cron job added"
fi

if crontab -l 2>/dev/null | grep -q "evening_evaluation.py"; then
    echo "⚠️  Evening evaluation cron job already exists"
else
    # Add evening cron job
    (crontab -l 2>/dev/null; echo "$EVENING_CRON") | crontab -
    echo "✅ Evening evaluation cron job added"
fi

echo ""
echo "📋 Current Cron Jobs:"
echo "===================="
crontab -l

echo ""
echo "📁 Directory Structure:"
echo "======================"
echo "Project directory: $SCRIPT_DIR"
echo "Logs directory: $SCRIPT_DIR/logs"
echo "Predictions directory: $SCRIPT_DIR/predictions (will be created automatically)"
echo "Evaluations directory: $SCRIPT_DIR/evaluations (will be created automatically)"

echo ""
echo "🔧 Manual Testing"
echo "================"
echo "You can test the scripts manually by running:"
echo "1. Morning prediction: python3 $SCRIPT_DIR/morning_prediction.py"
echo "2. Evening evaluation: python3 $SCRIPT_DIR/evening_evaluation.py"

echo ""
echo "📊 Log Files"
echo "============"
echo "Logs will be saved to:"
echo "- $SCRIPT_DIR/logs/morning_prediction.log"
echo "- $SCRIPT_DIR/logs/evening_evaluation.log"

echo ""
echo "🎯 What happens next?"
echo "===================="
echo "1. Morning (8:30 AM IST): Script generates predictions and sends email"
echo "2. Evening (5:00 PM IST): Script evaluates predictions and sends results"
echo "3. All data is saved locally for future reference"
echo "4. Logs are maintained for debugging"

echo ""
echo "✅ Setup completed successfully!"
echo "================================="
echo "Your automated stock prediction system is now configured."
echo "The first prediction email will be sent tomorrow at 8:30 AM IST (if it's a weekday)." 