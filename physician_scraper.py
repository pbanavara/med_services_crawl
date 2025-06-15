#!/usr/bin/env python3
import os
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
import logging
from serpapi import GoogleSearch

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PhysicianScraper:
    def __init__(self, excel_path, output_dir="output", serpapi_key=None, max_rows=None):
        """Initialize the scraper with the Excel file path and output directory."""
        self.excel_path = excel_path
        self.output_dir = output_dir
        self.max_rows = max_rows
        self.serpapi_key = serpapi_key or os.getenv('SERP_API_KEY')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info(f"Initializing scraper with Excel file: {excel_path}")
        logger.info(f"Output directory: {output_dir}")
        if self.max_rows:
            logger.info(f"Will process maximum {self.max_rows} rows")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")
        
        if not self.serpapi_key:
            logger.warning("No SerpAPI key provided. Please set SERP_API_KEY environment variable or pass it to the constructor.")
    
    def load_data(self):
        """Load data from Excel file."""
        try:
            logger.info(f"Loading Excel file: {self.excel_path}")
            df = pd.read_excel(self.excel_path)
            
            # Limit rows if max_rows is specified
            if self.max_rows and len(df) > self.max_rows:
                df = df.head(self.max_rows)
                logger.info(f"Limited to first {self.max_rows} rows for testing")
            
            logger.info(f"Successfully loaded Excel file. Shape: {df.shape}")
            logger.info(f"Columns found: {df.columns.tolist()}")
            return df
        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            return None
    
    def find_website(self, group_name, physician_name, address):
        """Find website URL using SerpAPI."""
        if not self.serpapi_key:
            logger.error("No SerpAPI key available. Cannot search for websites.")
            return None
            
        query = f"{group_name} {physician_name} {address} official website"
        logger.info(f"Searching for website with query: {query}")
        
        params = {
            "q": query,
            "api_key": self.serpapi_key,
            "num": 5  # Get top 5 results
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            organic_results = results.get("organic_results", [])
            logger.info(f"Found {len(organic_results)} search results")
            
            for i, result in enumerate(organic_results):
                url = result.get("link")
                title = result.get("title", "")
                logger.debug(f"Checking result {i+1}: {title} -> {url}")
                
                if url and not any(site in url for site in ['facebook.com', 'linkedin.com', 'yelp.com', 'healthgrades.com', 'vitals.com', 'zocdoc.com']):
                    logger.info(f"Found suitable website: {url}")
                    return url
            
            logger.warning("No suitable website found in search results")
            return None
            
        except Exception as e:
            logger.error(f"Error searching for website with SerpAPI: {e}")
            return None
    
    def extract_services(self, url, visited=None, depth=0, max_depth=2):
        """Extract services from website by crawling links."""
        if visited is None:
            visited = set()
        
        if depth > max_depth or url in visited:
            return set()
        
        visited.add(url)
        services = set()
        
        logger.info(f"Crawling URL (depth {depth}): {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to load {url}: HTTP {response.status_code}")
                return services
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for services in the current page
            page_services = self._find_services_in_page(soup)
            services.update(page_services)
            logger.info(f"Found {len(page_services)} services on current page")
            
            # Crawl internal links
            if depth < max_depth:
                domain = urlparse(url).netloc
                links = soup.find_all('a', href=True)
                
                logger.debug(f"Checking {len(links)} internal links for service-related content")
                for link in links:
                    href = link['href']
                    if href.startswith('/') or domain in href:
                        full_url = urljoin(url, href)
                        if urlparse(full_url).netloc == domain and full_url not in visited:
                            # Only follow links that seem likely to contain service info
                            if any(keyword in full_url.lower() for keyword in ['service', 'treat', 'care', 'specialty', 'procedure', 'therapy']):
                                logger.debug(f"Following service-related link: {full_url}")
                                services.update(self.extract_services(full_url, visited, depth + 1, max_depth))
            
            logger.info(f"Total services found at depth {depth}: {len(services)}")
            return services
        
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return services
    
    def _find_services_in_page(self, soup):
        """Extract services from a page using various heuristics."""
        services = set()
        
        # Look for service keywords in headers and lists
        service_keywords = [
            'care', 'treatment', 'therapy', 'procedure', 'service', 'specialty',
            'surgery', 'consultation', 'exam', 'screening', 'test', 'imaging'
        ]
        
        logger.debug("Searching for services in page headers and lists")
        
        # Check headers
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        logger.debug(f"Found {len(headers)} headers to analyze")
        
        for header in headers:
            text = header.get_text().strip()
            if any(keyword in text.lower() for keyword in service_keywords):
                # Try to find lists following this header
                next_elem = header.find_next_sibling()
                if next_elem and next_elem.name in ['ul', 'ol']:
                    for li in next_elem.find_all('li'):
                        service_text = li.get_text().strip()
                        if len(service_text) > 3 and len(service_text.split()) < 10:
                            services.add(service_text)
                            logger.debug(f"Found service in list: {service_text}")
                
                # Add the header itself if it looks like a service
                if 3 < len(text) < 100 and not any(word in text.lower() for word in ['our', 'we', 'about', 'contact']):
                    services.add(text)
                    logger.debug(f"Found service in header: {text}")
        
        # Check paragraphs with service-related terms
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if any(f"provide {keyword}" in text.lower() or f"offer {keyword}" in text.lower() for keyword in service_keywords):
                # Try to extract services from this paragraph
                potential_services = re.findall(r'(?:provide|offer|specialize in|including)(?:\s\w+){0,3}\s((?:[A-Z][a-z]+\s?){1,5})', text)
                services.update(s.strip() for s in potential_services if s.strip())
        
        # Check for lists with service-like items
        list_items = soup.find_all('li')
        logger.debug(f"Found {len(list_items)} list items to analyze")
        
        for li in list_items:
            text = li.get_text().strip()
            if 3 < len(text) < 100 and text[0].isupper():
                # Check if parent has a service keyword
                parent = li.parent
                if parent and parent.find_previous_sibling():
                    parent_header = parent.find_previous_sibling().get_text().lower()
                    if any(keyword in parent_header for keyword in service_keywords):
                        services.add(text)
                        logger.debug(f"Found service in list with service header: {text}")
        
        # Check for service cards/blocks (common in modern websites)
        service_blocks = soup.select('.service, .card, .box, .item, .feature')
        logger.debug(f"Found {len(service_blocks)} service blocks/cards")
        
        for block in service_blocks:
            # Check if this block has a title that looks like a service
            title_elem = block.select_one('h2, h3, h4, .title, .heading')
            if title_elem:
                title = title_elem.get_text().strip()
                if 3 < len(title) < 100 and title[0].isupper():
                    services.add(title)
                    logger.debug(f"Found service in card/block: {title}")
        
        logger.debug(f"Total services found on page: {len(services)}")
        return services
    
    def process_data(self):
        """Process data from Excel file, find websites, and extract services."""
        logger.info("Starting data processing...")
        
        df = self.load_data()
        if df is None:
            logger.error("Failed to load data, exiting")
            return
        
        results = []
        total_rows = len(df)
        logger.info(f"Processing {total_rows} rows from Excel file")
        
        # Check for required columns
        required_columns = ['Physician Group Name', 'Address']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            logger.info(f"Available columns: {df.columns.tolist()}")
            return
        
        for index, row in df.iterrows():
            try:
                # Extract necessary information from row
                group_name = str(row.get('Physician Group Name', ''))
                address = str(row.get('Address', ''))
                
                # Use group name as physician name if no separate physician name column
                physician_name = group_name
                
                logger.info(f"Processing row {index + 1}/{total_rows}: {group_name}")
                
                # Skip if missing crucial information
                if not group_name or group_name == 'nan':
                    logger.warning(f"Skipping row {index + 1}: Missing group name")
                    continue
                
                # Find website
                website = self.find_website(group_name, physician_name, address)
                if not website:
                    logger.warning(f"No website found for {group_name}")
                    continue
                
                logger.info(f"Found website: {website}")
                
                # Extract services
                services = self.extract_services(website)
                services_list = list(services)
                
                logger.info(f"Extracted {len(services_list)} services for {group_name}")
                
                # Create result object
                result = {
                    'group_name': group_name,
                    'physician_name': physician_name,
                    'address': address,
                    'website': website,
                    'services': services_list
                }
                
                # Save to JSON
                sanitized_name = re.sub(r'[^\w\s-]', '', group_name).strip().replace(' ', '_')
                output_file = os.path.join(self.output_dir, f"{sanitized_name}.json")
                
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                logger.info(f"Saved results to: {output_file}")
                
                # Add to results list
                results.append(result)
                
                # Be polite to servers
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing row {index + 1}: {e}")
        
        logger.info(f"Processing complete. Successfully processed {len(results)} physician groups")
        return results

if __name__ == "__main__":
    logger.info("Starting Physician Group Website Scraper")
    
    # You can set your SerpAPI key here or use environment variable
    serpapi_key = os.getenv('SERP_API_KEY')  # Changed from SERPAPI_KEY to SERP_API_KEY
    # serpapi_key = "your_serpapi_key_here"  # Or uncomment and set directly
    
    # Set max_rows to 20 for testing (set to None for full dataset)
    max_rows = 20
    
    scraper = PhysicianScraper("Physician Groups in US.xlsx", serpapi_key=serpapi_key, max_rows=max_rows)
    results = scraper.process_data()
    logger.info("Scraper finished")