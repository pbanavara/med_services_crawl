# Physician Group Website Scraper

This tool extracts comprehensive information from physician group websites based on data from an Excel file, including services, social media presence, patient reviews, competitors, and location data.

## Features

### Core Functionality
- Reads physician group data from Excel file
- Finds the official website for each physician group using Google search
- Crawls the websites to extract services offered
- Saves the results as JSON files, one per physician group

### Enhanced Data Collection (Enhanced Scraper)
- **Improved Service Extraction:** Better filtering to exclude insurance, FAQ, and irrelevant content
- **Social Media Presence:** Searches for profiles on Facebook, Instagram, Twitter, LinkedIn, and YouTube
- **Patient Reviews:** Finds review platforms like Yelp, HealthGrades, Vitals, ZocDoc, and Google Reviews
- **Competitor Analysis:** Identifies local competitors in the same area
- **Location Data:** Extracts city, state, population, and median income information
- **Google Ads Detection:** Searches for sponsored listings

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. For Google search functionality, you'll need to:
   - **Option 1: Install the unofficial `google` package**
     ```
     pip install google
     ```
   - **Option 2: Use SerpAPI (recommended for production)**
     ```
     pip install google-search-results
     ```
     and set your API key:
     ```bash
     export SERP_API_KEY="your_api_key_here"
     ```

3. For the Selenium version, you'll need:
   - Chrome browser installed
   - ChromeDriver will be automatically downloaded by webdriver-manager

## Usage

### Basic Version
1. Place your Excel file in the same directory as the script
2. Make sure your Excel file has these columns:
   - `Physician Group Name`
   - `Address`

3. Run the script:
   ```
   python physician_scraper.py
   ```

### Enhanced Version (Recommended)
The enhanced scraper provides comprehensive data collection with improved accuracy:

```bash
# Set your SerpAPI key
export SERP_API_KEY="your_api_key_here"

# Run the enhanced scraper (processes 20 rows by default for testing)
python enhanced_physician_scraper.py
```

**Enhanced scraper features:**
- **Better service extraction** with intelligent filtering
- **Social media presence** detection
- **Patient review platform** identification
- **Competitor analysis** for local market research
- **Location demographics** including population and income data
- **Comprehensive logging** for debugging and monitoring

### Selenium Version
The Selenium version provides more advanced scraping capabilities, including:
- Better handling of JavaScript-rendered websites
- Better navigation through website menus
- Detection of service information in modern web components

Run the Selenium version with:
```
python physician_scraper_selenium.py
```

## Configuration

### Environment Variables
- `SERP_API_KEY`: Your SerpAPI key for Google search functionality

### Scraper Parameters
You can modify these parameters in the enhanced scraper:
- `max_rows`: Limit the number of rows to process (default: 20 for testing, set to `None` for full dataset)
- `max_depth`: Control crawling depth for service extraction (default: 2)
- `output_dir`: Specify output directory (default: "output")

## Results

### Basic Results
Results will be saved in the `output` directory as JSON files. Each JSON file contains:
- Group name
- Physician name
- Address
- Website URL
- List of services extracted from the website

### Enhanced Results
Enhanced scraper results include additional data:
```json
{
  "group_name": "Example Eye Care",
  "physician_name": "Example Eye Care",
  "address": "123 Main St, City, State",
  "website": "https://example.com",
  "services": ["Eye Exams", "Glaucoma Treatment", "LASIK Surgery"],
  "social_media_presence": {
    "facebook": {"url": "...", "title": "..."},
    "instagram": {"url": "...", "title": "..."}
  },
  "patient_reviews": {
    "yelp": {"url": "...", "title": "..."},
    "healthgrades": {"url": "...", "title": "..."}
  },
  "competitors": [
    {"name": "Competitor Name", "url": "...", "snippet": "..."}
  ],
  "location_data": {
    "city": "City",
    "state": "State",
    "population": "100,000",
    "median_income": "$50,000"
  },
  "scraped_at": "2024-01-01T12:00:00"
}
```

## Service Extraction Quality

The enhanced scraper includes intelligent filtering to improve service extraction quality:

### What Gets Excluded
- Insurance information (Blue Cross, Anthem, etc.)
- FAQ content ("Why am I being asked...", "How to...")
- Administrative content (billing, hours, contact info)
- Social media and review content
- Generic navigation items

### What Gets Included
- Actual medical services (eye exams, glaucoma treatment, LASIK)
- Medical procedures and therapies
- Specialized treatments and consultations
- Diagnostic services and screenings

## Analysis Tools

### Service Quality Analysis
Run the analysis script to evaluate current service extraction quality:
```bash
python analyze_services.py
```

This will provide:
- Statistics on service extraction quality
- Identification of problematic patterns
- Recommendations for improvement

## Customization

- Modify the `max_depth` parameter in `extract_services()` to control crawling depth
- Add or remove keywords in `_find_services_in_page()` to improve service detection
- Add specific site exclusions in the `find_website()` method
- Customize social media platforms or review sites in the enhanced scraper

## Limitations

- The scripts respect website rate limits by pausing between requests
- Very complex websites with heavy JavaScript may not be fully parsed in the basic version
- The accuracy of service extraction depends on how well-structured the target websites are
- SerpAPI has usage limits (100 free searches per month)
- Enhanced scraping takes longer due to additional data collection

## Cost Considerations

- **SerpAPI:** 100 free searches per month, then $50/month for 5,000 searches
- **Enhanced scraper:** Uses more API calls due to additional searches for social media, reviews, etc.
- **Testing:** Use `max_rows=20` for testing to minimize API usage

## Troubleshooting

### Common Issues
1. **No SerpAPI key:** Set `export SERP_API_KEY="your_key"`
2. **Empty results:** Check Excel column names match expected format
3. **Rate limiting:** Increase delays between requests
4. **Missing services:** Adjust filtering parameters in enhanced scraper

### Logs
- Basic scraper: `scraper.log`
- Enhanced scraper: `enhanced_scraper.log`
- Selenium scraper: `scraper_selenium.log`

## File Structure

```
├── physician_scraper.py              # Basic scraper
├── enhanced_physician_scraper.py     # Enhanced scraper (recommended)
├── physician_scraper_selenium.py     # Selenium-based scraper
├── analyze_services.py               # Service quality analysis
├── test_serpapi.py                   # SerpAPI testing utility
├── requirements.txt                  # Dependencies
├── SERPAPI_SETUP.md                  # SerpAPI setup guide
├── Physician Groups in US.xlsx       # Input data
└── output/                           # Results directory
    ├── enhanced_*.json              # Enhanced scraper results
    └── *.json                       # Basic scraper results
```