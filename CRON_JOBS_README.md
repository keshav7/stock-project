# Automated Stock Prediction Cron Jobs

This system provides automated stock prediction and evaluation through two scheduled cron jobs that run on weekdays.

## 🕐 Schedule

### Morning Prediction Job
- **Time:** 8:30 AM IST (Monday-Friday)
- **Script:** `morning_prediction.py`
- **Purpose:** Generates stock predictions for the day and sends email

### Evening Evaluation Job
- **Time:** 5:00 PM IST (Monday-Friday)
- **Script:** `evening_evaluation.py`
- **Purpose:** Evaluates morning predictions against actual market performance and sends results

## 🚀 Quick Setup

1. **Make the setup script executable:**
   ```bash
   chmod +x setup_cron_jobs.sh
   ```

2. **Run the setup script:**
   ```bash
   ./setup_cron_jobs.sh
   ```

3. **Follow the prompts to enter your email address**

The setup script will:
- Configure email addresses in both scripts
- Create the necessary cron job entries
- Set up logging directories
- Make scripts executable

## 📁 File Structure

```
stock-project/
├── morning_prediction.py      # Morning prediction script
├── evening_evaluation.py      # Evening evaluation script
├── setup_cron_jobs.sh        # Setup script
├── logs/                     # Log files (created automatically)
│   ├── morning_prediction.log
│   └── evening_evaluation.log
├── predictions/              # Prediction files (created automatically)
│   └── predictions_YYYYMMDD.json
└── evaluations/              # Evaluation files (created automatically)
    └── evaluations_YYYYMMDD.json
```

## 📧 Email Features

### Morning Prediction Email
- **Subject:** "Morning Stock Predictions - [Date Time]"
- **Content:**
  - Top 5 stock picks for the day
  - Confidence scores for each prediction
  - Predicted closing prices
  - Technical analysis reasoning
  - Beautiful HTML formatting

### Evening Evaluation Email
- **Subject:** "Evening Stock Evaluation - [Date Time]"
- **Content:**
  - Performance summary (HITS/MISSES/Success Rate)
  - Detailed comparison table
  - Actual vs predicted prices
  - Color-coded results (Green for HIT, Red for MISS)

## 🔧 Manual Testing

You can test the scripts manually:

```bash
# Test morning prediction
python3 morning_prediction.py

# Test evening evaluation
python3 evening_evaluation.py
```

## 📊 Data Storage

### Prediction Files
- **Location:** `predictions/predictions_YYYYMMDD.json`
- **Content:** Daily predictions with confidence scores and reasoning

### Evaluation Files
- **Location:** `evaluations/evaluations_YYYYMMDD.json`
- **Content:** Daily evaluation results with actual vs predicted performance

### Log Files
- **Location:** `logs/morning_prediction.log` and `logs/evening_evaluation.log`
- **Content:** Execution logs for debugging and monitoring

## ⚙️ Configuration

### Email Configuration
Update the email address in both scripts:
```python
recipient_email = "your-email@example.com"  # Change this
```

### Cron Job Timing
To modify the schedule, edit the cron entries:
```bash
# View current cron jobs
crontab -l

# Edit cron jobs
crontab -e
```

**Current cron format:**
- Morning: `30 8 * * 1-5` (8:30 AM, Mon-Fri)
- Evening: `0 17 * * 1-5` (5:00 PM, Mon-Fri)

## 🎯 Evaluation Criteria

### HIT Criteria
- Predicted close price is within **2%** of actual close price
- Example: Predicted ₹100, Actual ₹98-102 = HIT

### MISS Criteria
- Predicted close price differs by more than **2%** from actual close price
- Example: Predicted ₹100, Actual ₹97 or ₹103 = MISS

### Other Statuses
- **NO_DATA:** Unable to fetch actual market data
- **ERROR:** Error occurred during evaluation

## 🔍 Monitoring

### Check Logs
```bash
# View morning prediction logs
tail -f logs/morning_prediction.log

# View evening evaluation logs
tail -f logs/evening_evaluation.log
```

### Check Cron Jobs
```bash
# List all cron jobs
crontab -l

# Check cron service status
sudo systemctl status cron
```

### Test Email Configuration
```bash
# Test email sending
python3 email_sender.py
```

## 🛠️ Troubleshooting

### Common Issues

1. **Scripts not running:**
   - Check if cron service is running: `sudo systemctl status cron`
   - Verify cron jobs exist: `crontab -l`
   - Check logs for errors: `tail -f logs/morning_prediction.log`

2. **Email not received:**
   - Verify email address in scripts
   - Check Gmail API authentication
   - Test email sending manually

3. **No prediction data:**
   - Check internet connection
   - Verify Yahoo Finance API access
   - Check for market holidays

### Debug Mode
Add debug logging to scripts:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Tracking

The system automatically tracks:
- Daily success rates
- Prediction accuracy over time
- Confidence score effectiveness
- Stock-specific performance

All data is stored locally for analysis and improvement.

## 🔒 Security Notes

- Gmail API credentials are stored locally
- All data is kept on your local machine
- No external data sharing
- Regular token refresh handled automatically

## 📞 Support

For issues or questions:
1. Check the log files first
2. Test scripts manually
3. Verify cron job configuration
4. Check email authentication

## 🎉 Success!

Once configured, you'll receive:
- **Daily morning emails** with stock predictions
- **Daily evening emails** with performance results
- **Automatic data storage** for analysis
- **Comprehensive logging** for monitoring

The system runs automatically on weekdays, providing you with consistent stock analysis and performance tracking. 