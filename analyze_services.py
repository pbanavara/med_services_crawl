#!/usr/bin/env python3
import os
import json
import re
from collections import Counter

def analyze_services():
    """Analyze the services extracted from the current output files."""
    
    output_dir = "output"
    all_services = []
    problematic_services = []
    good_services = []
    
    # Define patterns that indicate non-service content
    exclude_patterns = [
        r'why am i being asked',
        r'what is the goal',
        r'how to',
        r'when should',
        r'can i',
        r'insurance',
        r'coverage',
        r'billing',
        r'payment',
        r'cost',
        r'price',
        r'frequently asked',
        r'faq',
        r'privacy policy',
        r'terms of service',
        r'contact us',
        r'about us',
        r'hours',
        r'location',
        r'directions',
        r'testimonial',
        r'review',
        r'rating',
        r'star',
        r'facebook',
        r'instagram',
        r'twitter',
        r'linkedin',
        r'youtube',
        r'yelp',
        r'healthgrades',
        r'blue cross',
        r'blue shield',
        r'anthem',
        r'humana',
        r'cigna',
        r'aetna'
    ]
    
    # Define patterns that indicate good service content
    service_patterns = [
        r'eye exam',
        r'vision test',
        r'glaucoma',
        r'cataract',
        r'lasik',
        r'contact lens',
        r'glasses',
        r'frames',
        r'ophthalmology',
        r'optometry',
        r'retina',
        r'macular',
        r'dry eye',
        r'pediatric',
        r'surgery',
        r'treatment',
        r'therapy',
        r'procedure',
        r'consultation',
        r'screening',
        r'imaging',
        r'oct',
        r'visual field',
        r'refraction'
    ]
    
    print("🔍 Analyzing service extraction quality...")
    print("=" * 60)
    
    # Read all JSON files in output directory
    for filename in os.listdir(output_dir):
        if filename.endswith('.json') and not filename.startswith('enhanced_'):
            filepath = os.path.join(output_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                group_name = data.get('group_name', 'Unknown')
                services = data.get('services', [])
                
                print(f"\n📋 {group_name}")
                print(f"   Total services extracted: {len(services)}")
                
                for service in services:
                    all_services.append(service)
                    
                    # Check if it's problematic
                    is_problematic = any(re.search(pattern, service.lower()) for pattern in exclude_patterns)
                    is_good_service = any(re.search(pattern, service.lower()) for pattern in service_patterns)
                    
                    if is_problematic:
                        problematic_services.append(service)
                        print(f"   ❌ Problematic: {service[:80]}...")
                    elif is_good_service:
                        good_services.append(service)
                        print(f"   ✅ Good service: {service[:80]}...")
                    else:
                        print(f"   ⚠️  Neutral: {service[:80]}...")
                
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    
    print(f"Total services extracted: {len(all_services)}")
    print(f"Good services: {len(good_services)} ({len(good_services)/len(all_services)*100:.1f}%)")
    print(f"Problematic services: {len(problematic_services)} ({len(problematic_services)/len(all_services)*100:.1f}%)")
    print(f"Neutral services: {len(all_services) - len(good_services) - len(problematic_services)} ({(len(all_services) - len(good_services) - len(problematic_services))/len(all_services)*100:.1f}%)")
    
    print("\n🔍 TOP PROBLEMATIC PATTERNS:")
    problematic_counter = Counter()
    for service in problematic_services:
        for pattern in exclude_patterns:
            if re.search(pattern, service.lower()):
                problematic_counter[pattern] += 1
    
    for pattern, count in problematic_counter.most_common(10):
        print(f"   {pattern}: {count} occurrences")
    
    print("\n✅ TOP GOOD SERVICE PATTERNS:")
    good_counter = Counter()
    for service in good_services:
        for pattern in service_patterns:
            if re.search(pattern, service.lower()):
                good_counter[pattern] += 1
    
    for pattern, count in good_counter.most_common(10):
        print(f"   {pattern}: {count} occurrences")
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Add more exclusion patterns for insurance and FAQ content")
    print("2. Improve service keyword detection")
    print("3. Add length and content quality filters")
    print("4. Use the enhanced scraper for better results")

if __name__ == "__main__":
    analyze_services() 