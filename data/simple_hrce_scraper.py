#!/usr/bin/env python3
"""
Simple HR&CE scraper that uses the search form to get temple data
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path

def scrape_temple_search():
    """Scrape temples using the search form"""
    
    base_url = "https://hrce.tn.gov.in"
    search_url = f"{base_url}/hrcehome/temples_search.php"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    print("Fetching temple search page...")
    
    # Create output directory
    output_dir = Path("raw_data")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # First GET request to get the form
        response = session.get(search_url, params={'activity': 'temple_search'})
        
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all select dropdowns to understand available filters
        print("\nAnalyzing search form...")
        
        # Find district dropdown
        district_select = soup.find('select', {'name': 'district_code'}) or \
                         soup.find('select', {'id': 'district_code'})
        
        districts = []
        if district_select:
            options = district_select.find_all('option')
            print(f"Found {len(options)-1} districts")  # -1 for empty option
            
            for option in options[1:]:  # Skip first empty option
                district_code = option.get('value')
                district_name = option.text.strip()
                if district_code:
                    districts.append({
                        'code': district_code,
                        'name': district_name
                    })
                    print(f"  - {district_name} ({district_code})")
            
            # Save districts
            with open(output_dir / 'districts.json', 'w', encoding='utf-8') as f:
                json.dump(districts, f, ensure_ascii=False, indent=2)
                print(f"\nSaved {len(districts)} districts to raw_data/districts.json")
        
        # Try to submit a search to get temple results
        print("\nTrying to fetch temples...")
        
        # Test with first district
        if districts:
            test_district = districts[0]
            print(f"Testing with district: {test_district['name']}")
            
            # Submit search form
            search_data = {
                'district_code': test_district['code'],
                'search': 'Search',
                'activity': 'temple_search'
            }
            
            response = session.post(search_url, data=search_data)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for results table
                tables = soup.find_all('table')
                
                for table in tables:
                    # Check if this is the results table
                    headers = table.find_all('th')
                    if any('Temple' in str(h) for h in headers):
                        print("Found temple results table!")
                        
                        # Extract temple data
                        temples = []
                        rows = table.find_all('tr')[1:]  # Skip header
                        
                        for row in rows[:10]:  # First 10 temples
                            cells = row.find_all('td')
                            if cells:
                                temple_data = {
                                    'raw_html': str(row),
                                    'cells': [cell.text.strip() for cell in cells]
                                }
                                temples.append(temple_data)
                                
                                # Print first temple as sample
                                if len(temples) == 1:
                                    print("\nSample temple data:")
                                    for i, cell in enumerate(temple_data['cells']):
                                        print(f"  Cell {i}: {cell}")
                        
                        # Save sample temples
                        if temples:
                            with open(output_dir / f'sample_temples_{test_district["code"]}.json', 'w', encoding='utf-8') as f:
                                json.dump(temples, f, ensure_ascii=False, indent=2)
                                print(f"\nSaved {len(temples)} sample temples")
                        
                        break
        
        # Try to find any JavaScript data
        print("\nLooking for embedded JavaScript data...")
        
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('temple' in script.string.lower() or 'district' in script.string.lower()):
                # Check for JSON-like structures
                import re
                
                # Look for var assignments with arrays or objects
                matches = re.findall(r'var\s+(\w+)\s*=\s*(\[.*?\]|\{.*?\})', script.string, re.DOTALL)
                
                for var_name, var_content in matches:
                    if len(var_content) > 100:  # Skip small objects
                        print(f"  Found variable: {var_name} ({len(var_content)} chars)")
                        
                        # Save raw JavaScript
                        with open(output_dir / f'js_var_{var_name}.txt', 'w') as f:
                            f.write(var_content)
        
        print("\nScraping complete! Check raw_data/ directory for results.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_direct_temple_url():
    """Test if individual temples have direct URLs"""
    
    print("\n" + "="*50)
    print("Testing direct temple URLs...")
    
    # Known temple ID from Sankarankovil
    test_ids = ['TM037875', 'TM000001', 'TM000100']
    
    session = requests.Session()
    base_url = "https://hrce.tn.gov.in"
    
    for temple_id in test_ids:
        print(f"\nTrying temple ID: {temple_id}")
        
        # Try different URL patterns
        urls = [
            f"{base_url}/temple/{temple_id}",
            f"{base_url}/temples/{temple_id}",
            f"{base_url}/temple_details.php?id={temple_id}",
            f"{base_url}/temples/temple_info.php?temple_id={temple_id}"
        ]
        
        for url in urls:
            try:
                response = session.get(url, timeout=5)
                if response.status_code == 200 and 'temple' in response.text.lower():
                    print(f"  ✓ Found at: {url}")
                    
                    # Save sample
                    with open(f'sample_temple_{temple_id}.html', 'w') as f:
                        f.write(response.text)
                    
                    break
            except:
                pass

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" SIMPLE HR&CE TEMPLE SCRAPER")
    print("="*60 + "\n")
    
    scrape_temple_search()
    test_direct_temple_url()