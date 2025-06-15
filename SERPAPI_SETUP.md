# SerpAPI Setup Guide

## Overview
The physician scraper has been updated to use SerpAPI instead of direct Google scraping. This provides more reliable and consistent search results without being blocked by Google's anti-bot measures.

## Setup Steps

### 1. Get a SerpAPI Key
1. Sign up at [serpapi.com](https://serpapi.com/)
2. Get your API key from the dashboard
3. Note: SerpAPI offers 100 free searches per month

### 2. Set Your API Key
You can set the API key in one of two ways:

**Option A: Environment Variable (Recommended)**
```bash
export SERP_API_KEY="your_api_key_here"
```

**Option B: Direct in Code**
Edit `physician_scraper.py` and uncomment/modify this line:
```python
serpapi_key = "your_api_key_here"  # Replace with your actual key
```

### 3. Test the Setup
Run the test script to verify everything is working:
```bash
python test_serpapi.py
```

### 4. Run the Scraper
```bash
python physician_scraper.py
```

**Note:** The scraper is configured to process only the first 20 rows by default for testing. To process the full dataset, change `max_rows = 20` to `max_rows = None` in the script.

## What Changed

### Before (Selenium/Google Scraping)
- Used Selenium to scrape Google search results
- Often blocked by Google's anti-bot measures
- Required complex HTML parsing
- Unreliable results

### After (SerpAPI)
- Uses SerpAPI's structured search results
- No blocking or CAPTCHAs
- Clean JSON responses
- Reliable and consistent results
- **Limited to 20 rows by default for testing**

## Logging
The updated scraper includes comprehensive logging:
- Console output for real-time monitoring
- Log file (`scraper.log`) for detailed debugging
- Progress tracking for each physician group

## Cost Considerations
- SerpAPI offers 100 free searches per month
- Additional searches cost $0.05 each
- With 20 test rows, you'll use 20 searches (free tier covers this)
- For 132,086 physician groups, you'd need approximately $6,600 worth of searches
- **Start with the 20-row test to verify everything works**

## Testing with a Sample
The scraper is already configured to test with the first 20 rows. If you want to test with a different sample size:

```python
# In physician_scraper.py, change this line:
max_rows = 20  # Change to desired number or None for full dataset
```

## Troubleshooting

### "No SerpAPI key available"
- Make sure you've set the SERP_API_KEY environment variable
- Or uncomment and set the key directly in the code

### "Error searching for website with SerpAPI"
- Check your API key is correct
- Verify you have remaining searches in your SerpAPI account
- Check your internet connection

### No search results found
- This is normal for some physician groups that may not have websites
- The scraper will log which groups don't have websites found
- Check the logs for details

## Environment Variable
The script now uses `SERP_API_KEY` as the environment variable name (instead of `SERPAPI_KEY`):
```bash
export SERP_API_KEY="your_api_key_here"
``` 