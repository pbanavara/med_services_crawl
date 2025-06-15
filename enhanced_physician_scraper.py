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
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedPhysicianScraper:
    def __init__(self, excel_path, output_dir="output", serpapi_key=None, max_rows=None):
        """Initialize the enhanced scraper with the Excel file path and output directory."""
        self.excel_path = excel_path
        self.output_dir = output_dir
        self.max_rows = max_rows
        self.serpapi_key = serpapi_key or os.getenv('SERP_API_KEY')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info(f"Initializing enhanced scraper with Excel file: {excel_path}")
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
    
    def extract_social_media_presence(self, group_name, address):
        """Search for social media profiles."""
        social_media = {}
        platforms = ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube']
        
        for platform in platforms:
            try:
                query = f"{group_name} {address} {platform}"
                params = {
                    "q": query,
                    "api_key": self.serpapi_key,
                    "num": 3
                }
                
                search = GoogleSearch(params)
                results = search.get_dict()
                organic_results = results.get("organic_results", [])
                
                for result in organic_results:
                    url = result.get("link", "")
                    if platform in url.lower():
                        social_media[platform] = {
                            "url": url,
                            "title": result.get("title", ""),
                            "snippet": result.get("snippet", "")
                        }
                        break
                
                time.sleep(1)  # Be polite to API
                
            except Exception as e:
                logger.warning(f"Error searching for {platform}: {e}")
        
        return social_media
    
    def extract_patient_reviews(self, group_name, address):
        """Search for patient reviews on review platforms."""
        review_platforms = {}
        platforms = ['yelp', 'healthgrades', 'vitals', 'zocdoc', 'google reviews']
        
        for platform in platforms:
            try:
                query = f"{group_name} {address} {platform} reviews"
                params = {
                    "q": query,
                    "api_key": self.serpapi_key,
                    "num": 3
                }
                
                search = GoogleSearch(params)
                results = search.get_dict()
                organic_results = results.get("organic_results", [])
                
                for result in organic_results:
                    url = result.get("link", "")
                    if platform.replace(' ', '') in url.lower():
                        review_platforms[platform] = {
                            "url": url,
                            "title": result.get("title", ""),
                            "snippet": result.get("snippet", "")
                        }
                        break
                
                time.sleep(1)  # Be polite to API
                
            except Exception as e:
                logger.warning(f"Error searching for {platform} reviews: {e}")
        
        return review_platforms
    
    def extract_competitors(self, group_name, address):
        """Search for competitors in the same area."""
        competitors = []
        
        try:
            # Extract city and state from address
            address_parts = address.split(',')
            if len(address_parts) >= 2:
                city_state = address_parts[-2].strip() + ', ' + address_parts[-1].strip()
            else:
                city_state = address
            
            # Search for similar practices in the area
            query = f"eye care optometry ophthalmology {city_state}"
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": 10
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            
            for result in organic_results:
                url = result.get("link", "")
                title = result.get("title", "")
                
                # Skip if it's the same practice or social media
                if (group_name.lower() not in title.lower() and 
                    not any(site in url for site in ['facebook.com', 'linkedin.com', 'yelp.com'])):
                    competitors.append({
                        "name": title,
                        "url": url,
                        "snippet": result.get("snippet", "")
                    })
                
                if len(competitors) >= 5:  # Limit to top 5 competitors
                    break
            
        except Exception as e:
            logger.warning(f"Error searching for competitors: {e}")
        
        return competitors
    
    def extract_location_data(self, address):
        """Extract city and state from address."""
        location_data = {
            "full_address": address,
            "city": "",
            "state": "",
            "population": "",
            "median_income": ""
        }
        
        try:
            # Parse address to extract city and state
            address_parts = address.split(',')
            if len(address_parts) >= 2:
                location_data["city"] = address_parts[-2].strip()
                location_data["state"] = address_parts[-1].strip()
            
            # Search for population and income data
            if location_data["city"] and location_data["state"]:
                query = f"{location_data['city']} {location_data['state']} population median income"
                params = {
                    "q": query,
                    "api_key": self.serpapi_key,
                    "num": 3
                }
                
                search = GoogleSearch(params)
                results = search.get_dict()
                organic_results = results.get("organic_results", [])
                
                for result in organic_results:
                    snippet = result.get("snippet", "")
                    # Extract population and income from snippet
                    population_match = re.search(r'population[:\s]*([\d,]+)', snippet, re.IGNORECASE)
                    if population_match:
                        location_data["population"] = population_match.group(1)
                    
                    income_match = re.search(r'median income[:\s]*\$?([\d,]+)', snippet, re.IGNORECASE)
                    if income_match:
                        location_data["median_income"] = f"${income_match.group(1)}"
                    break
                
        except Exception as e:
            logger.warning(f"Error extracting location data: {e}")
        
        return location_data
    
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
        """Extract services from a page using improved heuristics."""
        services = set()
        
        # Define actual medical service keywords
        service_keywords = [
            'care', 'treatment', 'therapy', 'procedure', 'service', 'specialty',
            'surgery', 'consultation', 'exam', 'screening', 'test', 'imaging',
            'ophthalmology', 'optometry', 'vision', 'eye', 'retina', 'glaucoma',
            'cataract', 'lasik', 'contact lens', 'glasses', 'frames'
        ]
        
        # Define phrases to exclude (insurance, FAQ, etc.)
        exclude_phrases = [
            'insurance', 'coverage', 'billing', 'payment', 'cost', 'price',
            'why am i', 'what is', 'how to', 'when should', 'can i',
            'frequently asked', 'faq', 'privacy policy', 'terms of service',
            'contact us', 'about us', 'hours', 'location', 'directions',
            'testimonial', 'review', 'rating', 'star', 'facebook', 'instagram',
            'twitter', 'linkedin', 'youtube', 'yelp', 'healthgrades'
        ]
        
        logger.debug("Searching for services in page headers and lists")
        
        # Check headers
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        logger.debug(f"Found {len(headers)} headers to analyze")
        
        for header in headers:
            text = header.get_text().strip()
            
            # Skip if it contains exclude phrases
            if any(phrase in text.lower() for phrase in exclude_phrases):
                continue
                
            if any(keyword in text.lower() for keyword in service_keywords):
                # Try to find lists following this header
                next_elem = header.find_next_sibling()
                if next_elem and next_elem.name in ['ul', 'ol']:
                    for li in next_elem.find_all('li'):
                        service_text = li.get_text().strip()
                        if (len(service_text) > 3 and len(service_text.split()) < 10 and
                            not any(phrase in service_text.lower() for phrase in exclude_phrases)):
                            services.add(service_text)
                            logger.debug(f"Found service in list: {service_text}")
                
                # Add the header itself if it looks like a service
                if (3 < len(text) < 100 and 
                    not any(word in text.lower() for word in ['our', 'we', 'about', 'contact']) and
                    not any(phrase in text.lower() for phrase in exclude_phrases)):
                    services.add(text)
                    logger.debug(f"Found service in header: {text}")
        
        # Check for service cards/blocks (common in modern websites)
        service_blocks = soup.select('.service, .card, .box, .item, .feature, .treatment, .procedure')
        logger.debug(f"Found {len(service_blocks)} service blocks/cards")
        
        for block in service_blocks:
            # Check if this block has a title that looks like a service
            title_elem = block.select_one('h2, h3, h4, .title, .heading, .service-title')
            if title_elem:
                title = title_elem.get_text().strip()
                if (3 < len(title) < 100 and title[0].isupper() and
                    not any(phrase in title.lower() for phrase in exclude_phrases)):
                    services.add(title)
                    logger.debug(f"Found service in card/block: {title}")
        
        # Check for navigation menus that might contain services
        nav_links = soup.select('nav a, .menu a, .navigation a, .services-menu a')
        for link in nav_links:
            text = link.get_text().strip()
            if (3 < len(text) < 50 and 
                any(keyword in text.lower() for keyword in service_keywords) and
                not any(phrase in text.lower() for phrase in exclude_phrases)):
                services.add(text)
                logger.debug(f"Found service in navigation: {text}")
        
        logger.debug(f"Total services found on page: {len(services)}")
        return services
    
    def process_data(self):
        """Process data from Excel file, find websites, and extract comprehensive information."""
        logger.info("Starting enhanced data processing...")
        
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
                
                # Extract additional data
                logger.info("Extracting social media presence...")
                social_media = self.extract_social_media_presence(group_name, address)
                
                logger.info("Extracting patient reviews...")
                patient_reviews = self.extract_patient_reviews(group_name, address)
                
                logger.info("Extracting competitors...")
                competitors = self.extract_competitors(group_name, address)
                
                logger.info("Extracting location data...")
                location_data = self.extract_location_data(address)
                
                # Create comprehensive result object
                result = {
                    'group_name': group_name,
                    'physician_name': physician_name,
                    'address': address,
                    'website': website,
                    'services': services_list,
                    'social_media_presence': social_media,
                    'patient_reviews': patient_reviews,
                    'competitors': competitors,
                    'location_data': location_data,
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Save to JSON
                sanitized_name = re.sub(r'[^\w\s-]', '', group_name).strip().replace(' ', '_')
                output_file = os.path.join(self.output_dir, f"enhanced_{sanitized_name}.json")
                
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                logger.info(f"Saved enhanced results to: {output_file}")
                
                # Add to results list
                results.append(result)
                
                # Be polite to servers
                time.sleep(3)  # Increased delay for enhanced scraping
                
            except Exception as e:
                logger.error(f"Error processing row {index + 1}: {e}")
        
        logger.info(f"Processing complete. Successfully processed {len(results)} physician groups")
        return results

if __name__ == "__main__":
    logger.info("Starting Enhanced Physician Group Website Scraper")
    
    # You can set your SerpAPI key here or use environment variable
    serpapi_key = os.getenv('SERP_API_KEY')  # Changed from SERPAPI_KEY to SERP_API_KEY
    # serpapi_key = "your_serpapi_key_here"  # Or uncomment and set directly
    
    # Set max_rows to 20 for testing (set to None for full dataset)
    max_rows = 20
    
    scraper = EnhancedPhysicianScraper("Physician Groups in US.xlsx", serpapi_key=serpapi_key, max_rows=max_rows)
    results = scraper.process_data()
    logger.info("Enhanced scraper finished") 