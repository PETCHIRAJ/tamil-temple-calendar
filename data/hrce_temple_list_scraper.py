#!/usr/bin/env python3
"""
HR&CE Temple List Scraper
Scrapes all 46,303 temples from the official Tamil Nadu HR&CE website
Using the temple_list.php page with district-wise pagination
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
import csv

class HRCETempleListScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://hrce.tn.gov.in"
        self.list_url = f"{self.base_url}/hrcehome/temple_list.php"
        
        # Set browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        })
        
        # Create output directory
        Path("raw_data").mkdir(exist_ok=True)
        
        # Rate limiting
        self.delay = 2  # seconds between requests
        
        # Districts in Tamil Nadu
        self.districts = [
            'Chennai', 'Kanchipuram', 'Tiruvallur', 'Cuddalore', 'Villupuram',
            'Vellore', 'Tiruvannamalai', 'Salem', 'Namakkal', 'Dharmapuri',
            'Erode', 'Coimbatore', 'Nilgiris', 'Thanjavur', 'Nagapattinam',
            'Tiruvarur', 'Tiruchirappalli', 'Karur', 'Perambalur', 'Pudukottai',
            'Madurai', 'Theni', 'Dindigul', 'Ramanathapuram', 'Virudhunagar',
            'Sivaganga', 'Tirunelveli', 'Thoothukudi', 'Kanniyakumari',
            'Krishnagiri', 'Ariyalur', 'Tiruppur', 'Chengalpattu', 'Kallakurichi',
            'Ranipet', 'Tenkasi', 'Tirupathur', 'Mayiladuthurai'
        ]
    
    def scrape_temple_list_page(self, district=None, page=1):
        """Scrape a single page of temple listings"""
        
        params = {'page': page}
        if district:
            params['district'] = district
        
        print(f"  Fetching page {page}...")
        time.sleep(self.delay)  # Rate limiting
        
        try:
            response = self.session.get(self.list_url, params=params)
            
            if response.status_code != 200:
                print(f"    Error: Status {response.status_code}")
                return None, False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the temple table
            tables = soup.find_all('table')
            temples = []
            has_next = False
            
            for table in tables:
                rows = table.find_all('tr')
                
                # Check if this is the temple data table
                if len(rows) > 1:
                    headers = []
                    
                    # Get headers from first row
                    header_row = rows[0]
                    header_cells = header_row.find_all(['th', 'td'])
                    headers = [cell.text.strip() for cell in header_cells]
                    
                    # Check if this looks like temple data
                    if any('temple' in h.lower() or 'kovil' in h.lower() for h in headers):
                        print(f"    Found temple table with {len(rows)-1} rows")
                        
                        # Extract temple data
                        for row in rows[1:]:
                            cells = row.find_all(['td', 'th'])
                            if cells:
                                temple = {}
                                
                                for i, cell in enumerate(cells):
                                    if i < len(headers):
                                        key = headers[i] or f'field_{i}'
                                    else:
                                        key = f'field_{i}'
                                    
                                    # Extract text and any links
                                    temple[key] = cell.text.strip()
                                    
                                    # Check for temple ID in links
                                    link = cell.find('a')
                                    if link and 'href' in link.attrs:
                                        href = link['href']
                                        # Extract temple ID if present
                                        if 'temple_id=' in href or 'TM' in href:
                                            import re
                                            id_match = re.search(r'(TM\d+)', href)
                                            if id_match:
                                                temple['temple_id'] = id_match.group(1)
                                
                                if any(temple.values()):  # Skip empty rows
                                    temples.append(temple)
            
            # Check for pagination - next page link
            next_link = soup.find('a', text='Next') or \
                       soup.find('a', {'class': 'next'}) or \
                       soup.find('a', text='»')
            
            if next_link:
                has_next = True
            
            # Also check if we got 20 temples (typical pagination size)
            if len(temples) == 20:
                has_next = True
            
            return temples, has_next
            
        except Exception as e:
            print(f"    Error: {e}")
            return None, False
    
    def scrape_district_temples(self, district_name):
        """Scrape all temples for a specific district"""
        print(f"\nScraping temples for district: {district_name}")
        
        all_temples = []
        page = 1
        
        while True:
            temples, has_next = self.scrape_temple_list_page(district=district_name, page=page)
            
            if temples:
                all_temples.extend(temples)
                print(f"    Total so far: {len(all_temples)} temples")
                
                # Save intermediate results
                with open(f'raw_data/temples_{district_name}_partial.json', 'w', encoding='utf-8') as f:
                    json.dump(all_temples, f, ensure_ascii=False, indent=2)
            
            if not has_next or not temples:
                break
            
            page += 1
            
            # Stop at 10 pages for testing (200 temples max per district)
            if page > 10:
                print("    Stopping at page 10 for testing")
                break
        
        print(f"  Completed: {len(all_temples)} temples for {district_name}")
        return all_temples
    
    def scrape_sample_temples(self, limit=10):
        """Scrape a sample of temples for validation"""
        print("\n" + "="*60)
        print(" SCRAPING SAMPLE TEMPLES FOR VALIDATION")
        print("="*60)
        
        # Try the main list page first
        print("\nTrying main temple list page...")
        temples, has_next = self.scrape_temple_list_page()
        
        if temples:
            print(f"\n✓ Found {len(temples)} temples on first page!")
            
            # Save sample
            sample = temples[:limit] if len(temples) > limit else temples
            
            with open('raw_data/sample_10_temples.json', 'w', encoding='utf-8') as f:
                json.dump(sample, f, ensure_ascii=False, indent=2)
            
            print(f"\nSaved {len(sample)} sample temples to raw_data/sample_10_temples.json")
            
            # Print sample
            print("\nSample temple data:")
            for i, temple in enumerate(sample[:3], 1):
                print(f"\nTemple {i}:")
                for key, value in temple.items():
                    if value:
                        print(f"  {key}: {value}")
            
            return sample
        else:
            print("Could not fetch from main list page")
            
            # Try with a specific small district
            print("\nTrying Nilgiris district (smallest - 51 temples)...")
            temples = self.scrape_district_temples('Nilgiris')
            
            if temples:
                sample = temples[:limit]
                
                with open('raw_data/sample_10_temples.json', 'w', encoding='utf-8') as f:
                    json.dump(sample, f, ensure_ascii=False, indent=2)
                
                return sample
        
        return None
    
    def scrape_all_temples(self):
        """Scrape all 46,303 temples from all districts"""
        print("\n" + "="*60)
        print(" SCRAPING ALL TEMPLES FROM HR&CE")
        print("="*60)
        print(f"\nTotal districts to process: {len(self.districts)}")
        print("Estimated temples: 46,303")
        print("This will take several hours with rate limiting...")
        
        all_temples = []
        
        for i, district in enumerate(self.districts, 1):
            print(f"\n[{i}/{len(self.districts)}] Processing {district}...")
            
            temples = self.scrape_district_temples(district)
            
            if temples:
                # Add district info to each temple
                for temple in temples:
                    temple['district'] = district
                
                all_temples.extend(temples)
            
            # Save progress
            with open('raw_data/all_temples_progress.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'total_temples': len(all_temples),
                    'districts_completed': i,
                    'temples': all_temples
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\nTotal temples collected: {len(all_temples)}")
            
            # For testing, stop after 3 districts
            if i >= 3:
                print("\nStopping after 3 districts for testing")
                break
        
        return all_temples

def main():
    """Main execution"""
    scraper = HRCETempleListScraper()
    
    print("\n" + "="*60)
    print(" HR&CE TEMPLE LIST SCRAPER")
    print("="*60)
    print("\nOptions:")
    print("1. Scrape 10 sample temples for validation")
    print("2. Scrape one district (Nilgiris - 51 temples)")
    print("3. Scrape all districts (46,303 temples - several hours)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        print("\nFetching 10 sample temples...")
        temples = scraper.scrape_sample_temples(10)
        
        if temples:
            print(f"\n✓ Successfully fetched {len(temples)} sample temples!")
            print("\nValidation checklist:")
            print("- [ ] Temple names are readable")
            print("- [ ] Tamil text is preserved")
            print("- [ ] Temple IDs are captured")
            print("- [ ] District information is present")
            print("\nCheck raw_data/sample_10_temples.json for full data")
    
    elif choice == '2':
        print("\nScraping Nilgiris district...")
        temples = scraper.scrape_district_temples('Nilgiris')
        
        if temples:
            with open('raw_data/nilgiris_temples.json', 'w', encoding='utf-8') as f:
                json.dump(temples, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ Scraped {len(temples)} temples from Nilgiris")
    
    elif choice == '3':
        confirm = input("\nThis will take several hours. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            temples = scraper.scrape_all_temples()
            print(f"\n✓ Scraped {len(temples)} temples total")
        else:
            print("Cancelled")
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()