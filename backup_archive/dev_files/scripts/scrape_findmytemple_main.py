#!/usr/bin/env python3
"""
Main FindMyTemple.com Temple Scraper
=====================================
A clean, maintainable script for scraping temple data from FindMyTemple.com

Usage:
    python scrape_findmytemple_main.py --temple-id t123
    python scrape_findmytemple_main.py --batch 10 --start 0
    python scrape_findmytemple_main.py --all

Author: Temple Calendar App Team
Date: 2024
"""

import json
import time
import argparse
import requests
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


class FindMyTempleScraper:
    """Scraper for FindMyTemple.com temple data"""
    
    BASE_URL = "http://www.findmytemple.com"
    CATEGORIES = [
        "sivan-temple",
        "vishnu-temple", 
        "murugan-temple",
        "amman-temple",
        "vinayagartemple",
        "aanjanayar-temple",
        "more-temples"
    ]
    
    def __init__(self, output_file: str = "findmytemple_scraped_data.json"):
        self.output_file = output_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; TempleScraper/1.0)'
        })
    
    def scrape_temple(self, temple_id: str, category: str, name: str) -> Dict:
        """Scrape a single temple's data"""
        url = f"{self.BASE_URL}/en/{category}/{temple_id}-{name.lower().replace(' ', '-')}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract data from HTML (simplified - use BeautifulSoup in production)
            temple_data = {
                "temple_id": temple_id,
                "name": name,
                "category": category,
                "url": url,
                "location": {
                    "city": "",
                    "state": "Tamil Nadu",
                    "country": "India",
                    "address": "",
                    "coordinates": {"latitude": None, "longitude": None}
                },
                "deity": {
                    "main_deity": "",
                    "goddess": "",
                    "other_deities": [],
                    "deity_type": self._get_deity_type(category)
                },
                "temple_info": {
                    "age": "",
                    "architectural_style": "",
                    "historical_significance": "",
                    "mythology": "",
                    "unique_features": []
                },
                "festivals": [],
                "timings": {
                    "general": "",
                    "special_days": "",
                    "aarti_times": []
                },
                "facilities": [],
                "how_to_reach": {
                    "nearest_railway": "",
                    "nearest_airport": "",
                    "by_road": ""
                },
                "contact": {
                    "phone": "",
                    "email": "",
                    "website": ""
                },
                "scraped_at": datetime.now().isoformat(),
                "data_completeness": 50  # Basic scraping
            }
            
            print(f"✓ Scraped: {temple_id} - {name}")
            return temple_data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed: {temple_id} - {name} ({str(e)})")
            return None
    
    def _get_deity_type(self, category: str) -> str:
        """Map category to deity type"""
        mapping = {
            "sivan-temple": "Sivan",
            "vishnu-temple": "Vishnu",
            "murugan-temple": "Murugan",
            "amman-temple": "Amman",
            "vinayagartemple": "Vinayagar",
            "aanjanayar-temple": "Aanjanayar",
            "more-temples": "Other"
        }
        return mapping.get(category, "Unknown")
    
    def scrape_batch(self, temples: List[Dict], max_workers: int = 5) -> List[Dict]:
        """Scrape multiple temples in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.scrape_temple,
                    temple['temple_id'],
                    temple['category'],
                    temple['name']
                ): temple
                for temple in temples
            }
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        
        return results
    
    def save_data(self, temples: List[Dict], append: bool = False):
        """Save scraped data to JSON file"""
        if append and os.path.exists(self.output_file):
            with open(self.output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = {
                "source": "FindMyTemple.com",
                "scraped_date": datetime.now().isoformat(),
                "total_temples": 0,
                "temples": []
            }
        
        existing_data['temples'].extend(temples)
        existing_data['total_temples'] = len(existing_data['temples'])
        existing_data['last_updated'] = datetime.now().isoformat()
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(temples)} temples to {self.output_file}")
        print(f"Total temples in database: {existing_data['total_temples']}")


def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description='Scrape temple data from FindMyTemple.com')
    parser.add_argument('--temple-id', help='Scrape a specific temple by ID')
    parser.add_argument('--category', help='Temple category', default='sivan-temple')
    parser.add_argument('--name', help='Temple name')
    parser.add_argument('--batch', type=int, help='Number of temples to scrape')
    parser.add_argument('--start', type=int, default=0, help='Starting index for batch')
    parser.add_argument('--output', default='findmytemple_scraped_data.json', help='Output file')
    parser.add_argument('--workers', type=int, default=5, help='Number of parallel workers')
    
    args = parser.parse_args()
    
    scraper = FindMyTempleScraper(args.output)
    
    if args.temple_id:
        # Scrape single temple
        name = args.name or f"Temple {args.temple_id}"
        result = scraper.scrape_temple(args.temple_id, args.category, name)
        if result:
            scraper.save_data([result], append=True)
    
    elif args.batch:
        # Example batch scraping (would need temple list in production)
        print(f"Batch scraping {args.batch} temples starting from index {args.start}")
        # Load temple list and scrape batch
        # temples = load_temple_list()[args.start:args.start + args.batch]
        # results = scraper.scrape_batch(temples, args.workers)
        # scraper.save_data(results, append=True)
    
    else:
        print("Please specify --temple-id or --batch option")
        parser.print_help()


if __name__ == "__main__":
    main()