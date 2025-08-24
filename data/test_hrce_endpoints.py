#!/usr/bin/env python3
"""
Test script to verify HR&CE endpoints and understand data structure
"""

import requests
import json
from pprint import pprint

def test_endpoints():
    """Test various endpoint patterns to find working ones"""
    
    base_url = "https://hrce.tn.gov.in"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    
    print("Testing HR&CE Endpoints...")
    print("="*50)
    
    # First, try to access the search page to establish session
    print("\n1. Testing main search page...")
    search_url = f"{base_url}/hrcehome/temples_search.php?activity=temple_search"
    
    try:
        response = session.get(search_url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✓ Search page accessible")
            
            # Check if we can find any data in the HTML
            if "District" in response.text:
                print("   ✓ Found district references")
            if "Taluk" in response.text:
                print("   ✓ Found taluk references")
            if "Temple" in response.text:
                print("   ✓ Found temple references")
        else:
            print(f"   ✗ Failed with status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test different endpoint patterns
    test_patterns = [
        # Pattern 1: Direct AJAX calls
        {
            "url": f"{base_url}/temples/ajax/app_master.php",
            "method": "POST",
            "data": {"action": "getDistricts", "state_code": "33"}
        },
        # Pattern 2: Alternative path
        {
            "url": f"{base_url}/ajax/getDistricts.php",
            "method": "POST",
            "data": {"state_code": "33"}
        },
        # Pattern 3: GET request
        {
            "url": f"{base_url}/temples/ajax/app_master.php?action=getDistricts&state_code=33",
            "method": "GET",
            "data": None
        },
        # Pattern 4: Search API
        {
            "url": f"{base_url}/api/temples/search",
            "method": "POST",
            "data": {"district": "", "taluk": "", "village": ""}
        }
    ]
    
    print("\n2. Testing AJAX endpoints...")
    
    for i, pattern in enumerate(test_patterns, 1):
        print(f"\n   Pattern {i}: {pattern['url']}")
        
        try:
            if pattern['method'] == 'POST':
                response = session.post(pattern['url'], data=pattern['data'])
            else:
                response = session.get(pattern['url'])
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                # Try to parse as JSON
                try:
                    data = response.json()
                    print(f"   ✓ JSON response received")
                    print(f"   Data type: {type(data)}")
                    if isinstance(data, list):
                        print(f"   Items count: {len(data)}")
                        if data:
                            print(f"   Sample item: {data[0]}")
                    elif isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())}")
                except:
                    # Not JSON, check if HTML with data
                    if len(response.text) < 1000:
                        print(f"   Response: {response.text[:200]}")
                    else:
                        print(f"   HTML response ({len(response.text)} bytes)")
            else:
                print(f"   ✗ Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    # Try to find temple data in page source
    print("\n3. Checking for embedded data in search page...")
    
    try:
        response = session.get(search_url)
        
        # Look for JavaScript variables with data
        if "var districts" in response.text:
            print("   ✓ Found districts variable")
        if "var temples" in response.text:
            print("   ✓ Found temples variable")
        if "JSON.parse" in response.text:
            print("   ✓ Found JSON parsing - data might be embedded")
        
        # Check for select/option tags
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find district dropdown
        district_select = soup.find('select', {'name': 'district_code'}) or \
                         soup.find('select', {'id': 'district_code'}) or \
                         soup.find('select', {'class': 'district'})
        
        if district_select:
            options = district_select.find_all('option')
            print(f"   ✓ Found district dropdown with {len(options)} options")
            
            # Show first few districts
            if len(options) > 1:
                print("   Sample districts:")
                for option in options[1:4]:  # Skip empty first option
                    print(f"     - {option.text}: {option.get('value')}")
        
    except Exception as e:
        print(f"   ✗ Error parsing page: {e}")
    
    print("\n" + "="*50)
    print("Testing complete!")

def extract_embedded_data():
    """Try to extract any embedded data from the search page"""
    
    print("\n4. Attempting to extract embedded data...")
    
    url = "https://hrce.tn.gov.in/hrcehome/temples_search.php?activity=temple_search"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            import re
            
            # Look for JavaScript arrays or objects
            patterns = [
                r'var\s+(\w+)\s*=\s*(\[[\s\S]*?\]);',  # var name = [...];
                r'var\s+(\w+)\s*=\s*(\{[\s\S]*?\});',  # var name = {...};
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response.text)
                
                for var_name, var_content in matches:
                    if 'district' in var_name.lower() or 'temple' in var_name.lower():
                        print(f"   Found variable: {var_name}")
                        
                        # Try to clean and parse
                        try:
                            # Simple cleanup
                            cleaned = var_content.replace("'", '"')
                            data = json.loads(cleaned)
                            print(f"   ✓ Parsed {var_name}: {len(data)} items")
                            
                            # Save this data
                            with open(f"embedded_{var_name}.json", 'w') as f:
                                json.dump(data, f, indent=2)
                                print(f"   Saved to embedded_{var_name}.json")
                        except:
                            print(f"   Could not parse {var_name}")
            
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" HR&CE ENDPOINT TESTER")
    print("="*60)
    
    test_endpoints()
    extract_embedded_data()
    
    print("\n\nNote: If endpoints don't work directly, we may need to:")
    print("1. Use Selenium for JavaScript-rendered content")
    print("2. Analyze network traffic in browser DevTools")
    print("3. Check if authentication/session tokens are required")
    print("4. Use the search form with POST data")