#!/usr/bin/env python3
"""
Scrape Temple Data from Dinamalar Temple Portal
Enriches our dataset with deity info, festivals, and Tamil content
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse

class DinamalarTempleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ta;q=0.8",
        })
        
        self.base_url = "https://temple.dinamalar.com/"
        Path("dinamalar_data").mkdir(exist_ok=True)
        
        # Categories to scrape
        self.categories = [
            {"name": "Vinayagar", "url": "koillist.php?cat=11", "count": 83},
            {"name": "Murugan", "url": "koillist.php?cat=10", "count": 153},
            {"name": "Shiva_Devaram", "url": "koillist_home.php?cat=1", "count": 274},
            {"name": "Shiva", "url": "koillist.php?cat=8", "count": 558},
            {"name": "Amman", "url": "koillist.php?cat=7", "count": 355},
            {"name": "Vishnu", "url": "koillist.php?cat=9", "count": 312},
            {"name": "108_Divya_Desam", "url": "108_divya_desam.php", "count": 108},
            {"name": "Navagraha", "url": "nava_kirakam.php", "count": 9},
        ]
        
        self.all_temples = []
        self.temple_details = []
        
    def get_page(self, url):
        """Fetch page with retries"""
        for attempt in range(3):
            try:
                resp = self.session.get(url, timeout=10)
                resp.encoding = 'utf-8'  # Ensure proper Tamil encoding
                if resp.status_code == 200:
                    return BeautifulSoup(resp.text, 'html.parser')
            except Exception as e:
                print(f"  Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        return None
    
    def extract_temple_list(self, category):
        """Extract temple list from category page"""
        print(f"\n📂 Scraping {category['name']} temples...")
        
        url = urljoin(self.base_url, category['url'])
        soup = self.get_page(url)
        
        if not soup:
            print(f"  ❌ Failed to load {category['name']}")
            return []
        
        temples = []
        
        # Find temple links - patterns vary by page
        # Pattern 1: Links in tables
        temple_links = soup.find_all('a', href=re.compile(r'koil_detail\.php\?id=\d+'))
        
        # Pattern 2: Special pages might have different structures
        if not temple_links:
            temple_links = soup.find_all('a', href=re.compile(r'.*[Tt]emple.*'))
        
        for link in temple_links:
            temple_name = link.get_text(strip=True)
            temple_url = urljoin(self.base_url, link.get('href'))
            
            # Skip non-temple links
            if not temple_name or 'dinamalar' in temple_name.lower():
                continue
            
            # Extract location if available
            location = ""
            parent = link.parent
            if parent:
                text = parent.get_text()
                # Look for location patterns
                location_match = re.search(r'[,\-]\s*([^,\-]+(?:District|[Tt]aluk|Nadu))', text)
                if location_match:
                    location = location_match.group(1).strip()
            
            temples.append({
                "name": temple_name,
                "url": temple_url,
                "category": category['name'],
                "location": location,
                "source": "dinamalar"
            })
        
        print(f"  ✓ Found {len(temples)} temples in {category['name']}")
        return temples
    
    def extract_temple_details(self, temple):
        """Extract detailed information from temple page"""
        soup = self.get_page(temple['url'])
        
        if not soup:
            return None
        
        details = {
            "name": temple['name'],
            "category": temple['category'],
            "url": temple['url'],
            "location": temple.get('location', ''),
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Extract main content area
        content = soup.find('div', class_='content') or soup.find('td', class_='content')
        
        if content:
            # Extract text content
            text = content.get_text()
            
            # Extract deity information
            deity_patterns = [
                r'மூலவர்\s*:?\s*([^\n]+)',
                r'இறைவன்\s*:?\s*([^\n]+)',
                r'இறைவி\s*:?\s*([^\n]+)',
                r'அம்மன்\s*:?\s*([^\n]+)',
            ]
            
            deities = []
            for pattern in deity_patterns:
                matches = re.findall(pattern, text)
                deities.extend(matches)
            
            if deities:
                details['deities'] = list(set(deities))
            
            # Extract location/address
            addr_patterns = [
                r'முகவரி\s*:?\s*([^\n]+)',
                r'இடம்\s*:?\s*([^\n]+)',
                r'ஊர்\s*:?\s*([^\n]+)',
            ]
            
            for pattern in addr_patterns:
                match = re.search(pattern, text)
                if match:
                    details['address'] = match.group(1).strip()
                    break
            
            # Extract festival information
            festival_patterns = [
                r'திருவிழா\s*:?\s*([^\n]+)',
                r'பண்டிகை\s*:?\s*([^\n]+)',
                r'உற்சவம்\s*:?\s*([^\n]+)',
            ]
            
            festivals = []
            for pattern in festival_patterns:
                matches = re.findall(pattern, text)
                festivals.extend(matches)
            
            if festivals:
                details['festivals'] = list(set(festivals))
            
            # Extract timing if available
            timing_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM|காலை|மாலை)[^\.]*)'
            timings = re.findall(timing_pattern, text)
            if timings:
                details['timings'] = timings
            
            # Store Tamil content
            details['tamil_content'] = {
                "has_tamil": True,
                "content_length": len(text),
                "sample": text[:500] if len(text) > 500 else text
            }
            
            # Extract images
            images = content.find_all('img')
            if images:
                image_urls = []
                for img in images[:10]:  # Limit to 10 images
                    src = img.get('src')
                    if src:
                        image_urls.append(urljoin(self.base_url, src))
                
                if image_urls:
                    details['images'] = image_urls
        
        return details
    
    def scrape_all_categories(self):
        """Scrape all temple categories"""
        print("\n" + "="*60)
        print(" SCRAPING DINAMALAR TEMPLE PORTAL")
        print("="*60)
        
        # Step 1: Get temple lists from all categories
        for category in self.categories:
            temples = self.extract_temple_list(category)
            self.all_temples.extend(temples)
            time.sleep(1)  # Be respectful
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_temples = []
        for temple in self.all_temples:
            if temple['url'] not in seen_urls:
                seen_urls.add(temple['url'])
                unique_temples.append(temple)
        
        self.all_temples = unique_temples
        print(f"\n📊 Total unique temples found: {len(self.all_temples)}")
        
        # Save temple list
        with open("dinamalar_data/temple_list.json", "w", encoding="utf-8") as f:
            json.dump(self.all_temples, f, ensure_ascii=False, indent=2)
        
        # Step 2: Get details for each temple (limited for now)
        print(f"\n📖 Fetching details for first 100 temples...")
        
        for i, temple in enumerate(self.all_temples[:100]):  # Limit to 100 for testing
            print(f"  Processing {i+1}/100: {temple['name'][:50]}...")
            
            details = self.extract_temple_details(temple)
            if details:
                self.temple_details.append(details)
            
            # Save progress every 20 temples
            if (i + 1) % 20 == 0:
                self.save_progress()
            
            time.sleep(0.5)  # Be respectful
        
        # Final save
        self.save_progress(final=True)
        
        return self.temple_details
    
    def save_progress(self, final=False):
        """Save scraped data"""
        suffix = "_final" if final else "_progress"
        
        with open(f"dinamalar_data/temple_details{suffix}.json", "w", encoding="utf-8") as f:
            json.dump(self.temple_details, f, ensure_ascii=False, indent=2)
        
        print(f"  💾 Saved {len(self.temple_details)} temple details")
    
    def generate_summary(self):
        """Generate summary of scraped data"""
        summary = {
            "total_temples_found": len(self.all_temples),
            "details_extracted": len(self.temple_details),
            "categories_scraped": len(self.categories),
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Analyze extracted data
        has_deities = sum(1 for t in self.temple_details if t.get('deities'))
        has_festivals = sum(1 for t in self.temple_details if t.get('festivals'))
        has_timings = sum(1 for t in self.temple_details if t.get('timings'))
        has_images = sum(1 for t in self.temple_details if t.get('images'))
        has_tamil = sum(1 for t in self.temple_details if t.get('tamil_content'))
        
        summary['data_coverage'] = {
            "with_deities": has_deities,
            "with_festivals": has_festivals,
            "with_timings": has_timings,
            "with_images": has_images,
            "with_tamil_content": has_tamil
        }
        
        # Category distribution
        category_dist = {}
        for temple in self.temple_details:
            cat = temple.get('category', 'Unknown')
            category_dist[cat] = category_dist.get(cat, 0) + 1
        
        summary['category_distribution'] = category_dist
        
        with open("dinamalar_data/scraping_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*60)
        print(" SCRAPING COMPLETE")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  Total temples found: {summary['total_temples_found']}")
        print(f"  Details extracted: {summary['details_extracted']}")
        print(f"  With deities: {has_deities}")
        print(f"  With festivals: {has_festivals}")
        print(f"  With timings: {has_timings}")
        print(f"  With images: {has_images}")
        print(f"  With Tamil content: {has_tamil}")
        
        return summary

def main():
    scraper = DinamalarTempleScraper()
    temples = scraper.scrape_all_categories()
    summary = scraper.generate_summary()
    
    print("\n✅ Next steps:")
    print("  1. Review temple_details_final.json")
    print("  2. Match with existing temple IDs")
    print("  3. Integrate into unified dataset")

if __name__ == "__main__":
    main()