#!/usr/bin/env python3
"""
HR&CE Direct Temple Scraper
Directly accesses temple pages by ID pattern
"""

import requests
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

class HRCEDirectScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        })
        
        self.base_url = "https://hrce.tn.gov.in"
        Path("raw_data").mkdir(exist_ok=True)
        
    def fetch_temple_by_id(self, temple_id):
        """Fetch a specific temple by its ID"""
        # Try different URL patterns
        urls = [
            f"{self.base_url}/hrcehome/index_temple.php?tid={temple_id}",
            f"{self.base_url}/hrcehome/temple_details.php?id={temple_id}",
            f"{self.base_url}/temple/{temple_id}"
        ]
        
        for url in urls:
            try:
                resp = self.session.get(url, timeout=5)
                
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, "html.parser")
                    
                    # Check if we got actual temple data
                    page_text = soup.get_text(strip=True)
                    
                    # Skip if error message
                    if "date mismatched" in page_text or "No matching records" in page_text:
                        continue
                    
                    # Look for temple name or ID in page
                    if temple_id in page_text or len(page_text) > 500:
                        temple_data = {
                            "temple_id": temple_id,
                            "url": url,
                            "status": "found"
                        }
                        
                        # Extract title
                        title = soup.find("title")
                        if title:
                            temple_data["title"] = title.get_text(strip=True)
                        
                        # Extract any headers
                        for tag in ["h1", "h2", "h3"]:
                            headers = soup.find_all(tag)
                            for h in headers:
                                text = h.get_text(strip=True)
                                if text and len(text) > 5 and "temple" in text.lower():
                                    temple_data["name"] = text
                                    break
                        
                        # Extract tables for details
                        tables = soup.find_all("table")
                        if tables:
                            temple_data["has_details"] = True
                        
                        return temple_data
                        
            except Exception as e:
                continue
        
        return {"temple_id": temple_id, "status": "not_found"}
    
    def find_valid_temple_range(self):
        """Find the range of valid temple IDs"""
        print("Finding valid temple ID range...")
        
        # Test different ID formats
        test_ids = [
            "TM000001", "TM000010", "TM000100", "TM001000",
            "TM010000", "TM037875",  # Sankarankovil
            "TM040000", "TM045000", "TM046303"
        ]
        
        valid_ids = []
        
        for tid in test_ids:
            print(f"  Testing {tid}...", end="")
            result = self.fetch_temple_by_id(tid)
            
            if result["status"] == "found":
                print(" ✓ Found")
                valid_ids.append(tid)
            else:
                print(" ✗ Not found")
            
            time.sleep(1)  # Be respectful
        
        return valid_ids
    
    def fetch_sample_temples_parallel(self):
        """Fetch sample temples using parallel requests"""
        print("\n" + "="*60)
        print(" HR&CE DIRECT TEMPLE SCRAPER")
        print("="*60)
        
        # Generate sample IDs to test
        # Based on user research: 46,303 temples
        # Try different ranges
        sample_ids = []
        
        # Add known temple
        sample_ids.append("TM037875")  # Sankarankovil
        
        # Add some from beginning
        for i in range(1, 6):
            sample_ids.append(f"TM{i:06d}")
        
        # Add some from middle
        for i in range(20000, 20005):
            sample_ids.append(f"TM{i:06d}")
        
        # Add some from end
        for i in range(46300, 46304):
            sample_ids.append(f"TM{i:06d}")
        
        print(f"\nTesting {len(sample_ids)} temple IDs...")
        
        found_temples = []
        
        # Use thread pool for parallel fetching
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_id = {executor.submit(self.fetch_temple_by_id, tid): tid 
                           for tid in sample_ids}
            
            for future in as_completed(future_to_id):
                tid = future_to_id[future]
                try:
                    result = future.result()
                    print(f"  {tid}: {result['status']}")
                    
                    if result["status"] == "found":
                        found_temples.append(result)
                        
                        # Save first found temple HTML for analysis
                        if len(found_temples) == 1:
                            self.save_temple_page(tid)
                    
                except Exception as e:
                    print(f"  {tid}: Error - {e}")
                
                time.sleep(0.5)  # Small delay between results
        
        return found_temples
    
    def save_temple_page(self, temple_id):
        """Save full HTML of a temple page"""
        url = f"{self.base_url}/hrcehome/index_temple.php?tid={temple_id}"
        
        try:
            resp = self.session.get(url, timeout=10)
            soup = BeautifulSoup(resp.content, "html.parser")
            
            with open(f"raw_data/temple_{temple_id}_direct.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            
            print(f"    Saved HTML: raw_data/temple_{temple_id}_direct.html")
            
        except Exception as e:
            print(f"    Error saving HTML: {e}")
    
    def scrape_using_search_api(self):
        """Try using search API endpoint if available"""
        print("\nTrying search API approach...")
        
        search_url = f"{self.base_url}/hrcehome/ajax_temple_search.php"
        api_url = f"{self.base_url}/api/temples"
        
        # Try different API endpoints
        endpoints = [
            (f"{self.base_url}/hrcehome/ajax_temple_search.php", {"district": "Chennai"}),
            (f"{self.base_url}/hrcehome/get_temples.php", {"district": "Chennai"}),
            (f"{self.base_url}/api/temples", {"district": "Chennai", "page": 1}),
        ]
        
        for url, params in endpoints:
            try:
                print(f"  Trying: {url}")
                resp = self.session.post(url, data=params, timeout=5)
                
                if resp.status_code == 200:
                    # Check if JSON response
                    try:
                        data = resp.json()
                        if data:
                            print(f"    ✓ Got JSON data: {len(data)} items")
                            return data
                    except:
                        # Check if HTML with data
                        if len(resp.text) > 100:
                            print(f"    Got HTML response: {len(resp.text)} chars")
                            
            except Exception as e:
                print(f"    Error: {e}")
        
        return None

def main():
    scraper = HRCEDirectScraper()
    
    print("HR&CE Direct Temple Scraper")
    print("=" * 60)
    
    # Method 1: Find valid ID range
    print("\n1. Finding valid temple ID range...")
    valid_ids = scraper.find_valid_temple_range()
    
    if valid_ids:
        print(f"\n   ✓ Found {len(valid_ids)} valid temple IDs")
        print(f"   Valid IDs: {valid_ids}")
    
    # Method 2: Parallel fetch sample temples
    print("\n2. Fetching sample temples in parallel...")
    temples = scraper.fetch_sample_temples_parallel()
    
    if temples:
        # Save results
        with open("raw_data/direct_sample_temples.json", "w", encoding="utf-8") as f:
            json.dump(temples[:10], f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Found {len(temples)} accessible temples")
        print(f"✓ Saved to: raw_data/direct_sample_temples.json")
        
        print("\nSample temples found:")
        for temple in temples[:5]:
            print(f"  - {temple['temple_id']}: {temple.get('name', temple.get('title', 'Unknown'))}")
    
    # Method 3: Try search API
    print("\n3. Checking for API endpoints...")
    api_data = scraper.scrape_using_search_api()
    
    if api_data:
        print("\n✓ Found API endpoint!")
        with open("raw_data/api_temples.json", "w", encoding="utf-8") as f:
            json.dump(api_data, f, ensure_ascii=False, indent=2)
    
    # Summary
    print("\n" + "="*60)
    print(" SUMMARY")
    print("="*60)
    
    if temples or api_data:
        print("✅ Successfully found temple data!")
        print("\nNext steps:")
        print("1. Analyze the data structure")
        print("2. Identify all required fields")
        print("3. Scale up to fetch all temples")
    else:
        print("⚠️ Could not fetch temple data directly")
        print("\nRecommendations:")
        print("1. Use Selenium for JavaScript rendering")
        print("2. Contact HR&CE for API access")
        print("3. Check if login is required")

if __name__ == "__main__":
    main()