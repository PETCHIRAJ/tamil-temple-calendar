#!/usr/bin/env python3
"""
HR&CE Tamil Nadu Temple Data Scraper
Fetches and preserves raw government data from https://hrce.tn.gov.in
Stores everything as-is in JSON format for future processing
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hrce_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HRCETemplesScraper:
    """Scraper for Tamil Nadu HR&CE temple data"""
    
    def __init__(self, data_dir: str = "raw_data"):
        self.base_url = "https://hrce.tn.gov.in"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9,ta;q=0.8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'{self.base_url}/hrcehome/temples_search.php?activity=temple_search'
        })
        
        # Create data directory
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement rate limiting to be respectful"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()
    
    def _save_json(self, data: Dict, filename: str):
        """Save data to JSON file with timestamp"""
        filepath = self.data_dir / filename
        
        # Add metadata
        wrapped_data = {
            "source": "HR&CE Tamil Nadu",
            "scraped_at": datetime.now().isoformat(),
            "url": self.base_url,
            "data": data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(wrapped_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved data to {filepath}")
        return filepath
    
    def fetch_districts(self) -> List[Dict]:
        """Fetch all districts from HR&CE"""
        logger.info("Fetching districts...")
        
        # Try the AJAX endpoint
        url = f"{self.base_url}/temples/ajax/app_master.php"
        
        self._rate_limit()
        
        try:
            # First, we need to get the page to establish session
            search_page = self.session.get(
                f"{self.base_url}/hrcehome/temples_search.php?activity=temple_search"
            )
            
            # Now try to get districts
            # This might need POST data based on the JavaScript
            post_data = {
                'action': 'getDistricts',
                'state_code': '33'  # Tamil Nadu state code
            }
            
            response = self.session.post(url, data=post_data)
            
            if response.status_code == 200:
                districts = response.json() if response.content else []
                
                # Save raw district data
                self._save_json(districts, "districts_raw.json")
                
                logger.info(f"Found {len(districts)} districts")
                return districts
            else:
                logger.error(f"Failed to fetch districts: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching districts: {e}")
            return []
    
    def fetch_taluks(self, district_code: str) -> List[Dict]:
        """Fetch all taluks for a district"""
        logger.info(f"Fetching taluks for district {district_code}...")
        
        url = f"{self.base_url}/temples/ajax/app_master.php"
        
        self._rate_limit()
        
        try:
            post_data = {
                'action': 'getTaluks',
                'district_code': district_code
            }
            
            response = self.session.post(url, data=post_data)
            
            if response.status_code == 200:
                taluks = response.json() if response.content else []
                
                # Save raw taluk data
                filename = f"taluks_district_{district_code}_raw.json"
                self._save_json(taluks, filename)
                
                logger.info(f"Found {len(taluks)} taluks in district {district_code}")
                return taluks
            else:
                logger.error(f"Failed to fetch taluks: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching taluks: {e}")
            return []
    
    def fetch_villages(self, district_code: str, taluk_code: str) -> List[Dict]:
        """Fetch all villages for a taluk"""
        logger.info(f"Fetching villages for taluk {taluk_code}...")
        
        url = f"{self.base_url}/temples/ajax/app_master.php"
        
        self._rate_limit()
        
        try:
            post_data = {
                'action': 'getVillages',
                'district_code': district_code,
                'taluk_code': taluk_code
            }
            
            response = self.session.post(url, data=post_data)
            
            if response.status_code == 200:
                villages = response.json() if response.content else []
                
                # Save raw village data
                filename = f"villages_taluk_{taluk_code}_raw.json"
                self._save_json(villages, filename)
                
                logger.info(f"Found {len(villages)} villages in taluk {taluk_code}")
                return villages
            else:
                logger.error(f"Failed to fetch villages: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching villages: {e}")
            return []
    
    def fetch_temples_by_village(self, village_code: str) -> List[Dict]:
        """Fetch all temples in a village"""
        logger.info(f"Fetching temples for village {village_code}...")
        
        url = f"{self.base_url}/temples/ajax/app_master.php"
        
        self._rate_limit()
        
        try:
            post_data = {
                'action': 'getTemples',
                'village_code': village_code
            }
            
            response = self.session.post(url, data=post_data)
            
            if response.status_code == 200:
                temples = response.json() if response.content else []
                
                # Save raw temple data
                filename = f"temples_village_{village_code}_raw.json"
                self._save_json(temples, filename)
                
                logger.info(f"Found {len(temples)} temples in village {village_code}")
                return temples
            else:
                logger.error(f"Failed to fetch temples: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching temples: {e}")
            return []
    
    def fetch_temple_details(self, temple_id: str) -> Dict:
        """Fetch detailed information for a specific temple"""
        logger.info(f"Fetching details for temple {temple_id}...")
        
        url = f"{self.base_url}/temples/ajax/templeinfo_view_new.php"
        
        self._rate_limit()
        
        try:
            post_data = {
                'temple_id': temple_id,
                'action': 'getTempleInfo'
            }
            
            response = self.session.post(url, data=post_data)
            
            if response.status_code == 200:
                temple_info = response.json() if response.content else {}
                
                # Save raw temple details
                filename = f"temple_details_{temple_id}_raw.json"
                self._save_json(temple_info, filename)
                
                logger.info(f"Fetched details for temple {temple_id}")
                return temple_info
            else:
                logger.error(f"Failed to fetch temple details: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching temple details: {e}")
            return {}
    
    def scrape_all_temples(self, limit: Optional[int] = None):
        """
        Main method to scrape all temple data hierarchically
        
        Args:
            limit: Optional limit on number of temples to scrape (for testing)
        """
        logger.info("Starting comprehensive temple data scraping...")
        
        all_temples = []
        temple_count = 0
        
        # Progress tracking
        progress_file = self.data_dir / "scraping_progress.json"
        
        # Load previous progress if exists
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                progress = json.load(f)
                logger.info(f"Resuming from previous progress: {progress['temples_scraped']} temples")
        else:
            progress = {
                "started_at": datetime.now().isoformat(),
                "temples_scraped": 0,
                "districts_completed": [],
                "current_district": None
            }
        
        try:
            # Step 1: Get all districts
            districts = self.fetch_districts()
            
            if not districts:
                logger.error("No districts found. Check connection or endpoints.")
                return
            
            # Step 2: Iterate through districts
            for district in districts:
                district_code = district.get('district_code', district.get('code'))
                district_name = district.get('district_name', district.get('name', 'Unknown'))
                
                # Skip if already completed
                if district_code in progress['districts_completed']:
                    logger.info(f"Skipping already completed district: {district_name}")
                    continue
                
                logger.info(f"\n{'='*50}")
                logger.info(f"Processing District: {district_name} ({district_code})")
                logger.info(f"{'='*50}")
                
                progress['current_district'] = district_code
                
                # Step 3: Get taluks for this district
                taluks = self.fetch_taluks(district_code)
                
                # Step 4: Iterate through taluks
                for taluk in taluks:
                    taluk_code = taluk.get('taluk_code', taluk.get('code'))
                    taluk_name = taluk.get('taluk_name', taluk.get('name', 'Unknown'))
                    
                    logger.info(f"\n  Processing Taluk: {taluk_name} ({taluk_code})")
                    
                    # Step 5: Get villages for this taluk
                    villages = self.fetch_villages(district_code, taluk_code)
                    
                    # Step 6: Iterate through villages
                    for village in villages:
                        village_code = village.get('village_code', village.get('code'))
                        village_name = village.get('village_name', village.get('name', 'Unknown'))
                        
                        logger.info(f"    Processing Village: {village_name}")
                        
                        # Step 7: Get temples in this village
                        temples = self.fetch_temples_by_village(village_code)
                        
                        # Add location context to each temple
                        for temple in temples:
                            temple['district'] = district_name
                            temple['district_code'] = district_code
                            temple['taluk'] = taluk_name
                            temple['taluk_code'] = taluk_code
                            temple['village'] = village_name
                            temple['village_code'] = village_code
                            
                            all_temples.append(temple)
                            temple_count += 1
                            
                            # Check limit
                            if limit and temple_count >= limit:
                                logger.info(f"Reached limit of {limit} temples")
                                break
                        
                        if limit and temple_count >= limit:
                            break
                    
                    if limit and temple_count >= limit:
                        break
                
                # Mark district as completed
                progress['districts_completed'].append(district_code)
                progress['temples_scraped'] = temple_count
                
                # Save progress
                with open(progress_file, 'w') as f:
                    json.dump(progress, f, indent=2)
                
                # Save all temples collected so far
                self._save_json(all_temples, f"all_temples_raw_{len(all_temples)}.json")
                
                if limit and temple_count >= limit:
                    break
                
                # Longer pause between districts
                time.sleep(5)
            
            logger.info(f"\n{'='*50}")
            logger.info(f"Scraping completed! Total temples: {temple_count}")
            logger.info(f"{'='*50}")
            
            # Save final consolidated data
            final_data = {
                "total_temples": temple_count,
                "districts_processed": len(progress['districts_completed']),
                "temples": all_temples
            }
            
            self._save_json(final_data, "all_temples_final_raw.json")
            
        except KeyboardInterrupt:
            logger.info("\nScraping interrupted by user. Progress saved.")
            
        except Exception as e:
            logger.error(f"Unexpected error during scraping: {e}")
            
        finally:
            # Save final progress
            progress['last_run'] = datetime.now().isoformat()
            progress['temples_scraped'] = temple_count
            
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2)

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print(" HR&CE TAMIL NADU TEMPLE DATA SCRAPER")
    print("="*60)
    print("\nThis will fetch raw temple data from the government website.")
    print("Data will be saved as-is in JSON format for future processing.")
    print("\nOptions:")
    print("1. Test run (fetch 10 temples)")
    print("2. Fetch 100 temples")
    print("3. Fetch 1000 temples")
    print("4. Fetch ALL temples (43,774 - will take several hours)")
    print("5. Fetch specific temple details by ID")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    scraper = HRCETemplesScraper()
    
    if choice == '1':
        print("\nStarting test run for 10 temples...")
        scraper.scrape_all_temples(limit=10)
    elif choice == '2':
        print("\nFetching 100 temples...")
        scraper.scrape_all_temples(limit=100)
    elif choice == '3':
        print("\nFetching 1000 temples...")
        scraper.scrape_all_temples(limit=1000)
    elif choice == '4':
        confirm = input("\nThis will fetch ALL temples and may take several hours. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            scraper.scrape_all_temples()
        else:
            print("Cancelled.")
    elif choice == '5':
        temple_id = input("\nEnter temple ID (e.g., TM037875): ").strip()
        temple_details = scraper.fetch_temple_details(temple_id)
        print(f"\nFetched details for temple {temple_id}")
        print(json.dumps(temple_details, indent=2, ensure_ascii=False))
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()