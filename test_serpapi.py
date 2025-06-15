#!/usr/bin/env python3
import os
from serpapi import GoogleSearch

def test_serpapi():
    """Test SerpAPI functionality"""
    serpapi_key = os.getenv('SERP_API_KEY')
    
    if not serpapi_key:
        print("❌ No SERP_API_KEY environment variable found!")
        print("Please set your SerpAPI key:")
        print("export SERP_API_KEY='your_api_key_here'")
        return False
    
    print(f"✅ Found SerpAPI key: {serpapi_key[:10]}...")
    
    # Test with a simple search
    params = {
        "q": "Complete Eye Care official website",
        "api_key": serpapi_key,
        "num": 3
    }
    
    try:
        print("🔍 Testing SerpAPI search...")
        search = GoogleSearch(params)
        results = search.get_dict()
        
        organic_results = results.get("organic_results", [])
        print(f"✅ Found {len(organic_results)} search results")
        
        for i, result in enumerate(organic_results):
            title = result.get("title", "No title")
            url = result.get("link", "No URL")
            print(f"  {i+1}. {title}")
            print(f"     {url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing SerpAPI: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing SerpAPI Integration")
    print("=" * 40)
    
    if test_serpapi():
        print("\n✅ SerpAPI test successful! You can now run the main scraper.")
    else:
        print("\n❌ SerpAPI test failed. Please check your API key and try again.") 