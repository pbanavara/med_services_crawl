# Physician Group Website Scraper

This tool extracts service information from physician group websites based on data from an Excel file.

## Features

- Reads physician group data from Excel file
- Finds the official website for each physician group using Google search
- Crawls the websites to extract services offered
- Saves the results as JSON files, one per physician group

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. For Google search functionality, you'll need to:
   - Option 1: Install the unofficial `google` package
     ```
     pip install google
     ```
   - Option 2: Use the SerpAPI (recommended for production)
     ```
     pip install google-search-results
     ```
     and set your API key:
     ```python
     from serpapi import GoogleSearch
     search = GoogleSearch({"q": "query", "api_key": "your_api_key"})
     ```

3. For the Selenium version, you'll need:
   - Chrome browser installed
   - ChromeDriver will be automatically downloaded by webdriver-manager

## Usage

### Basic Version
1. Place your Excel file in the same directory as the script
2. Make sure your Excel file has these columns:
   - Group Name
   - Physician Name
   - Address

3. Run the script:
   ```
   python physician_scraper.py
   ```

### Selenium Version (Recommended)
The Selenium version provides more advanced scraping capabilities, including:
- Better handling of JavaScript-rendered websites
- Better navigation through website menus
- Detection of service information in modern web components

Run the Selenium version with:
```
python physician_scraper_selenium.py
```

## Results

Results will be saved in the `output` directory as JSON files. Each JSON file contains:
- Group name
- Physician name
- Address
- Website URL
- List of services extracted from the website

## Customization

- Modify the `max_depth` parameter in `extract_services()` to control crawling depth
- Add or remove keywords in `_find_services_in_page()` to improve service detection
- Add specific site exclusions in the `find_website()` method

## Limitations

- The scripts respect website rate limits by pausing between requests
- Very complex websites with heavy JavaScript may not be fully parsed in the basic version
- The accuracy of service extraction depends on how well-structured the target websites are