#!/usr/bin/env python3
"""
Fetch temple list from HR&CE using different approaches
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from pathlib import Path
import time

def approach1_parse_search_page():
    """Parse the main search page for any embedded data"""
    
    print("\n=== Approach 1: Parse Search Page ===")
    
    url = "https://hrce.tn.gov.in/hrcehome/temples_search.php?activity=temple_search"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for any select elements with options
    selects = soup.find_all('select')
    
    data = {}
    
    for select in selects:
        name = select.get('name') or select.get('id')
        if name:
            options = []
            for option in select.find_all('option'):
                value = option.get('value')
                text = option.text.strip()
                if value and value != '':
                    options.append({'value': value, 'text': text})
            
            if options:
                data[name] = options
                print(f"Found {name}: {len(options)} options")
    
    # Look for any data tables
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables")
    
    # Save raw HTML for analysis
    with open('raw_data/search_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
        print("Saved raw HTML to raw_data/search_page.html")
    
    return data

def approach2_try_api_endpoints():
    """Try various API endpoint patterns"""
    
    print("\n=== Approach 2: Try API Endpoints ===")
    
    session = requests.Session()
    base_url = "https://hrce.tn.gov.in"
    
    # First establish session
    session.get(f"{base_url}/hrcehome/temples_search.php?activity=temple_search")
    
    endpoints = [
        # Try different API patterns
        ("/temples/get_temples.php", {}),
        ("/api/temples", {}),
        ("/temples/list", {}),
        ("/temples/search", {"action": "list"}),
        ("/temples/ajax/get_temples.php", {}),
        ("/ajax/temples.php", {}),
        # Try with parameters
        ("/temples/ajax/app_master.php", {"action": "getAllTemples"}),
        ("/temples/ajax/app_master.php", {"action": "getTempleList"}),
        ("/temples/ajax/app_master.php", {"action": "search", "district": ""}),
    ]
    
    results = []
    
    for endpoint, params in endpoints:
        url = base_url + endpoint
        print(f"Trying: {url}")
        
        try:
            # Try both GET and POST
            for method in ['GET', 'POST']:
                if method == 'GET':
                    response = session.get(url, params=params, timeout=5)
                else:
                    response = session.post(url, data=params, timeout=5)
                
                if response.status_code == 200:
                    # Check if it's JSON
                    try:
                        data = response.json()
                        print(f"  ✓ {method} worked! Got JSON with {len(data) if isinstance(data, list) else 'object'}")
                        results.append({'endpoint': url, 'method': method, 'data': data})
                        break
                    except:
                        # Check if it has temple data
                        if 'temple' in response.text.lower() and len(response.text) < 100000:
                            print(f"  ✓ {method} returned HTML with temple references")
                            if len(response.text) < 10000:
                                print(f"    Response: {response.text[:200]}...")
        except Exception as e:
            if 'Connection refused' not in str(e):
                print(f"  Error: {e}")
    
    return results

def approach3_search_with_params():
    """Submit the search form with different parameters"""
    
    print("\n=== Approach 3: Submit Search Form ===")
    
    session = requests.Session()
    base_url = "https://hrce.tn.gov.in/hrcehome/temples_search.php"
    
    # Get the initial page
    response = session.get(base_url, params={'activity': 'temple_search'})
    
    # Try submitting with empty search (get all)
    search_params = [
        {'search': 'Search', 'temple_name': ''},  # Empty search
        {'search': 'Search', 'district_code': '01'},  # First district
        {'search': 'Search', 'temple_name': 'Meenakshi'},  # Famous temple
        {'btnSearch': 'Search', 'txtTemple': ''},  # Alternative param names
        {'submit': 'Submit', 'temple': ''},
        {'action': 'search', 'query': ''},
    ]
    
    for params in search_params:
        print(f"Trying params: {params}")
        
        response = session.post(base_url, data=params)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for results
            # Check for tables with temple data
            for table in soup.find_all('table'):
                rows = table.find_all('tr')
                if len(rows) > 1:  # Has data rows
                    # Check if it contains temple-related data
                    header_text = str(table)
                    if any(word in header_text.lower() for word in ['temple', 'kovil', 'deity']):
                        print(f"  ✓ Found temple table with {len(rows)-1} rows")
                        
                        # Extract first few rows as sample
                        temples = []
                        for row in rows[1:6]:  # First 5 temples
                            cells = row.find_all(['td', 'th'])
                            temple_data = [cell.text.strip() for cell in cells]
                            if temple_data:
                                temples.append(temple_data)
                                print(f"    Row: {temple_data}")
                        
                        # Save sample
                        with open('raw_data/sample_temples.json', 'w', encoding='utf-8') as f:
                            json.dump(temples, f, ensure_ascii=False, indent=2)
                        
                        return temples

def approach4_parse_javascript():
    """Look for JavaScript that might contain temple data"""
    
    print("\n=== Approach 4: Parse JavaScript ===")
    
    url = "https://hrce.tn.gov.in/hrcehome/temples_search.php?activity=temple_search"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None
    
    # Look for JavaScript arrays or objects
    patterns = [
        r'var\s+temples\s*=\s*(\[[\s\S]*?\]);',
        r'var\s+templeData\s*=\s*(\[[\s\S]*?\]);',
        r'var\s+districts\s*=\s*(\[[\s\S]*?\]);',
        r'temples:\s*(\[[\s\S]*?\])',
        r'"temples":\s*(\[[\s\S]*?\])',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, response.text)
        if matches:
            print(f"Found JavaScript data matching: {pattern}")
            
            for match in matches:
                try:
                    # Try to clean and parse
                    cleaned = match.replace("'", '"')
                    data = json.loads(cleaned)
                    print(f"  ✓ Parsed successfully: {len(data)} items")
                    return data
                except:
                    print(f"  Could not parse as JSON")
    
    # Look for AJAX URLs in JavaScript
    ajax_patterns = [
        r'url:\s*["\']([^"\']*temple[^"\']*)["\']',
        r'\.ajax\([^)]*["\']([^"\']*)["\']',
        r'fetch\(["\']([^"\']*)["\']'
    ]
    
    print("\nLooking for AJAX URLs in JavaScript...")
    for pattern in ajax_patterns:
        matches = re.findall(pattern, response.text)
        for match in matches:
            print(f"  Found AJAX URL: {match}")

def main():
    """Try all approaches to find temple data"""
    
    print("\n" + "="*60)
    print(" FETCHING TEMPLE DATA FROM HR&CE")
    print("="*60)
    
    # Create output directory
    Path("raw_data").mkdir(exist_ok=True)
    
    # Try all approaches
    results = {}
    
    # Approach 1
    data = approach1_parse_search_page()
    if data:
        results['search_page_data'] = data
        with open('raw_data/search_page_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Approach 2
    api_results = approach2_try_api_endpoints()
    if api_results:
        results['api_endpoints'] = api_results
    
    # Approach 3
    temple_results = approach3_search_with_params()
    if temple_results:
        results['search_results'] = temple_results
    
    # Approach 4
    js_data = approach4_parse_javascript()
    if js_data:
        results['javascript_data'] = js_data
    
    print("\n" + "="*60)
    print(" SUMMARY")
    print("="*60)
    
    if results:
        print("\n✓ Successfully found data using these methods:")
        for key in results:
            print(f"  - {key}")
        
        # Save all results
        with open('raw_data/all_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\nAll results saved to raw_data/all_results.json")
    else:
        print("\n✗ No data found. The website might require:")
        print("  1. Selenium for JavaScript rendering")
        print("  2. Analysis of network traffic")
        print("  3. Authentication tokens")
        print("  4. Different search parameters")
    
    print("\nNext steps:")
    print("1. Analyze raw_data/search_page.html manually")
    print("2. Use browser DevTools to monitor network requests")
    print("3. Try Selenium if JavaScript rendering is required")

if __name__ == "__main__":
    main()