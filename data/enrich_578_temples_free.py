#!/usr/bin/env python3
"""
Free Data Enrichment for 578 Major Temples
No paid APIs - Uses OpenStreetMap, URL patterns, and DuckDuckGo
Total time: ~30 minutes, Cost: $0
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path
import re
from urllib.parse import quote
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MajorTemplesEnricher:
    def __init__(self):
        """Initialize with 578 major temples"""
        # Load the full temple dataset
        logger.info("Loading temple data...")
        with open("../raw_data/tn_temples_full.json", "r", encoding="utf-8") as f:
            all_temples = json.load(f)
        
        # Filter major temples (income > 10 lakh)
        self.major_temples = [
            t for t in all_temples 
            if t.get('temple_12a_category') == '46_iii'
        ]
        
        logger.info(f"Found {len(self.major_temples)} major temples to enrich")
        
        # Results storage
        self.results = {
            "coordinates": {},
            "websites": {},
            "statistics": {},
            "failed": {
                "coordinates": [],
                "websites": []
            }
        }
        
        # Create output directory
        Path("../enriched_data").mkdir(exist_ok=True)
        
    def clean_temple_name(self, name):
        """Clean temple name for URL generation"""
        if not name:
            return ""
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove common prefixes
        prefixes = ["arulmigu", "sri", "shri", "shree", "arulmiku"]
        for prefix in prefixes:
            name = name.replace(prefix + " ", "")
        
        # Remove common suffixes
        name = name.replace(" temple", "").replace(" kovil", "")
        
        # Remove special characters and spaces
        name = re.sub(r'[^a-z0-9]', '', name)
        
        return name
    
    def get_coordinates_osm(self):
        """Get coordinates using OpenStreetMap Nominatim (Free)"""
        logger.info("\n📍 PHASE 1: Getting coordinates from OpenStreetMap...")
        logger.info("This will take ~10 minutes (rate limited to 1 req/sec)")
        
        try:
            from geopy.geocoders import Nominatim
            from geopy.exc import GeocoderTimedOut, GeocoderServiceError
        except ImportError:
            logger.error("Please install geopy: pip install geopy")
            return
        
        geolocator = Nominatim(
            user_agent="tamil_temple_calendar_app_v1",
            timeout=10
        )
        
        success_count = 0
        failed_count = 0
        
        for i, temple in enumerate(self.major_temples, 1):
            temple_id = temple.get('id')
            temple_name = temple.get('temple_name', '')
            district = temple.get('district', '')
            
            # Progress indicator
            if i % 50 == 0:
                logger.info(f"  Progress: {i}/{len(self.major_temples)} temples processed")
            
            # Try different address formats
            addresses = [
                # Full address
                f"{temple_name}, {temple.get('address', '')}, {district}, Tamil Nadu, India",
                # Name + district
                f"{temple_name}, {district}, Tamil Nadu",
                # Just name and state
                f"{temple_name}, Tamil Nadu",
            ]
            
            location_found = False
            
            for address in addresses:
                try:
                    # Rate limiting - 1 request per second
                    time.sleep(1)
                    
                    location = geolocator.geocode(address)
                    
                    if location:
                        self.results["coordinates"][temple_id] = {
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                            "address_used": address,
                            "osm_display_name": location.address,
                            "confidence": "high" if temple_name in location.address else "medium"
                        }
                        
                        logger.debug(f"  ✓ {temple_name[:40]}: {location.latitude:.4f}, {location.longitude:.4f}")
                        success_count += 1
                        location_found = True
                        break
                        
                except (GeocoderTimedOut, GeocoderServiceError) as e:
                    logger.debug(f"  ⚠ Geocoder error for {temple_name}: {e}")
                    continue
                except Exception as e:
                    logger.debug(f"  ✗ Error for {temple_name}: {e}")
                    continue
            
            if not location_found:
                self.results["failed"]["coordinates"].append({
                    "id": temple_id,
                    "name": temple_name,
                    "district": district
                })
                failed_count += 1
        
        logger.info(f"  ✅ Coordinates found: {success_count}/{len(self.major_temples)}")
        logger.info(f"  ❌ Failed: {failed_count}")
        
        # Save intermediate results
        self.save_results(intermediate=True)
    
    def check_temple_websites_patterns(self):
        """Check common URL patterns for temple websites (Free)"""
        logger.info("\n🌐 PHASE 2: Checking URL patterns for temple websites...")
        logger.info("This will take ~5 minutes")
        
        # Common temple website patterns
        url_patterns = [
            # HRCE patterns
            "https://{name}.hrce.tn.gov.in",
            "https://{name}.tnhrce.in",
            
            # Common temple domains
            "https://{name}temple.org",
            "https://{name}temple.com",
            "https://{name}temple.in",
            "https://www.{name}temple.org",
            "https://www.{name}temple.com",
            
            # Devasthanam patterns
            "https://{name}devasthanam.org",
            "https://{name}devasthanam.com",
            
            # Location based
            "https://{location}{name}.org",
            "https://{name}{location}.com",
        ]
        
        success_count = 0
        
        for i, temple in enumerate(self.major_temples, 1):
            temple_id = temple.get('id')
            temple_name = temple.get('temple_name', '')
            district = temple.get('district', '').replace(' District', '').lower()
            
            # Progress indicator
            if i % 100 == 0:
                logger.info(f"  Progress: {i}/{len(self.major_temples)} temples checked")
            
            # Skip if already found
            if temple_id in self.results["websites"]:
                continue
            
            # Clean names for URL
            clean_name = self.clean_temple_name(temple_name)
            clean_location = re.sub(r'[^a-z]', '', district)
            
            # Try each URL pattern
            for pattern in url_patterns:
                url = pattern.format(
                    name=clean_name,
                    location=clean_location
                )
                
                try:
                    # Use HEAD request for speed (don't download full page)
                    response = requests.head(
                        url, 
                        timeout=3,
                        allow_redirects=True,
                        headers={'User-Agent': 'Temple Calendar App Bot'}
                    )
                    
                    # Check if URL exists and returns success
                    if response.status_code < 400:
                        # Verify it's actually a temple website
                        # Do a quick GET to check content
                        verify_response = requests.get(url, timeout=5)
                        content_lower = verify_response.text.lower()[:5000]  # Check first 5KB
                        
                        # Look for temple-related keywords
                        temple_keywords = ['temple', 'kovil', 'devasthanam', 'darshan', 
                                         'pooja', 'deity', 'festival', 'hrce']
                        
                        if any(keyword in content_lower for keyword in temple_keywords):
                            self.results["websites"][temple_id] = {
                                "url": url,
                                "pattern_matched": pattern,
                                "verified": True,
                                "found_method": "pattern"
                            }
                            
                            logger.info(f"  ✓ Found: {temple_name[:30]} -> {url}")
                            success_count += 1
                            break
                            
                except requests.RequestException:
                    # URL doesn't exist or timeout
                    continue
                except Exception as e:
                    logger.debug(f"  Error checking {url}: {e}")
                    continue
        
        logger.info(f"  ✅ Websites found via patterns: {success_count}")
    
    def search_websites_duckduckgo(self):
        """Search for temple websites using DuckDuckGo (Free, no API key)"""
        logger.info("\n🦆 PHASE 3: Searching for websites via DuckDuckGo...")
        
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            logger.warning("DuckDuckGo search not available. Install: pip install duckduckgo-search")
            logger.warning("Skipping DuckDuckGo search phase...")
            return
        
        ddgs = DDGS()
        success_count = 0
        search_limit = 100  # Limit searches to avoid rate limiting
        
        temples_to_search = [
            t for t in self.major_temples[:search_limit]
            if t.get('id') not in self.results["websites"]
        ]
        
        logger.info(f"Searching for {len(temples_to_search)} temples without websites...")
        
        for i, temple in enumerate(temples_to_search, 1):
            temple_id = temple.get('id')
            temple_name = temple.get('temple_name', '')
            district = temple.get('district', '')
            
            if i % 20 == 0:
                logger.info(f"  Progress: {i}/{len(temples_to_search)} searches")
            
            # Search queries
            queries = [
                f'"{temple_name}" official website temple',
                f'"{temple_name}" {district} temple darshan timings',
            ]
            
            website_found = False
            
            for query in queries:
                if website_found:
                    break
                    
                try:
                    # Search with DuckDuckGo
                    results = ddgs.text(query, max_results=5, region='in-en')
                    
                    for result in results:
                        url = result.get('href', '')
                        title = result.get('title', '').lower()
                        body = result.get('body', '').lower()
                        
                        # Check if likely temple website
                        temple_indicators = ['temple', 'kovil', 'devasthanam', 'hrce', 
                                           'darshan', 'official', 'murugan', 'shiva']
                        
                        if any(ind in url.lower() for ind in temple_indicators):
                            # Verify the URL works
                            try:
                                response = requests.head(url, timeout=3, allow_redirects=True)
                                if response.status_code < 400:
                                    self.results["websites"][temple_id] = {
                                        "url": url,
                                        "search_query": query,
                                        "verified": False,  # Not fully verified
                                        "found_method": "duckduckgo"
                                    }
                                    
                                    logger.info(f"  ✓ Found via search: {temple_name[:30]} -> {url[:50]}")
                                    success_count += 1
                                    website_found = True
                                    break
                            except:
                                continue
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.debug(f"  Search error for {temple_name}: {e}")
                    continue
        
        logger.info(f"  ✅ Additional websites found via DuckDuckGo: {success_count}")
    
    def add_known_websites(self):
        """Add manually verified temple websites"""
        logger.info("\n📝 PHASE 4: Adding known temple websites...")
        
        known_websites = {
            # Major temples with known websites
            "Meenakshi Amman Temple": "https://maduraimeenakshi.org",
            "Brihadeeswarar Temple": "https://www.thanjavurtemple.tn.gov.in",
            "Ramanathaswamy Temple": "http://www.rameswaramtemple.nic.in",
            "Kapaleeshwarar Temple": "https://www.mylaikapaleeswarar.tnhrce.in",
            "Parthasarathy Temple": "https://www.thiruvallikkeni.tnhrce.in",
            "Nataraja Temple": "https://www.chidambaramnataraja.org",
            
            # Murugan temples
            "Palani Murugan Temple": "https://www.palani.org",
            "Tiruchendur Murugan Temple": "https://www.tiruchendurmurugan.org",
            
            # Add more as verified...
        }
        
        matched_count = 0
        
        for temple in self.major_temples:
            temple_name = temple.get('temple_name', '')
            temple_id = temple.get('id')
            
            # Check if temple name matches any known website
            for known_name, website in known_websites.items():
                if known_name.lower() in temple_name.lower() or \
                   temple_name.lower() in known_name.lower():
                    
                    if temple_id not in self.results["websites"]:
                        self.results["websites"][temple_id] = {
                            "url": website,
                            "verified": True,
                            "found_method": "known_list"
                        }
                        matched_count += 1
                        logger.info(f"  ✓ Matched: {temple_name[:40]} -> {website}")
                        break
        
        logger.info(f"  ✅ Known websites matched: {matched_count}")
    
    def save_results(self, intermediate=False):
        """Save enrichment results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare final results
        enriched_temples = []
        
        for temple in self.major_temples:
            temple_id = temple.get('id')
            enriched = {
                "id": temple_id,
                "name": temple.get('temple_name'),
                "district": temple.get('district'),
                "address": temple.get('address'),
                "income_category": temple.get('temple_12a_category')
            }
            
            # Add coordinates if found
            if temple_id in self.results["coordinates"]:
                enriched["coordinates"] = self.results["coordinates"][temple_id]
            
            # Add website if found
            if temple_id in self.results["websites"]:
                enriched["website"] = self.results["websites"][temple_id]
            
            enriched_temples.append(enriched)
        
        # Statistics
        self.results["statistics"] = {
            "total_temples": len(self.major_temples),
            "coordinates_found": len(self.results["coordinates"]),
            "websites_found": len(self.results["websites"]),
            "coordinates_success_rate": f"{len(self.results['coordinates'])/len(self.major_temples)*100:.1f}%",
            "websites_success_rate": f"{len(self.results['websites'])/len(self.major_temples)*100:.1f}%",
            "collection_timestamp": timestamp
        }
        
        # Save files
        suffix = "_intermediate" if intermediate else "_final"
        
        # Save full enriched data
        output_file = f"../enriched_data/578_temples_enriched{suffix}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(enriched_temples, f, ensure_ascii=False, indent=2)
        
        logger.info(f"  💾 Saved enriched data to {output_file}")
        
        # Save just coordinates for easy access
        if self.results["coordinates"]:
            coords_file = f"../enriched_data/578_temples_coordinates{suffix}.json"
            with open(coords_file, "w", encoding="utf-8") as f:
                json.dump(self.results["coordinates"], f, ensure_ascii=False, indent=2)
            logger.info(f"  💾 Saved coordinates to {coords_file}")
        
        # Save just websites for easy access
        if self.results["websites"]:
            websites_file = f"../enriched_data/578_temples_websites{suffix}.json"
            with open(websites_file, "w", encoding="utf-8") as f:
                json.dump(self.results["websites"], f, ensure_ascii=False, indent=2)
            logger.info(f"  💾 Saved websites to {websites_file}")
        
        # Save summary
        summary_file = f"../enriched_data/enrichment_summary{suffix}.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(self.results["statistics"], f, ensure_ascii=False, indent=2)
        
    def generate_report(self):
        """Generate final enrichment report"""
        print("\n" + "="*70)
        print(" 📊 ENRICHMENT COMPLETE - FINAL REPORT")
        print("="*70)
        
        stats = self.results["statistics"]
        
        print(f"\n🏛️ Total Major Temples Processed: {stats['total_temples']}")
        
        print(f"\n📍 Coordinates:")
        print(f"   Found: {stats['coordinates_found']} ({stats['coordinates_success_rate']})")
        print(f"   Failed: {len(self.results['failed']['coordinates'])}")
        
        print(f"\n🌐 Websites:")
        print(f"   Found: {stats['websites_found']} ({stats['websites_success_rate']})")
        
        # Website breakdown by method
        methods = {}
        for temple_id, website_info in self.results["websites"].items():
            method = website_info.get("found_method", "unknown")
            methods[method] = methods.get(method, 0) + 1
        
        print(f"\n   Websites by discovery method:")
        for method, count in methods.items():
            print(f"     - {method}: {count}")
        
        print(f"\n⏱️ Processing completed at: {stats['collection_timestamp']}")
        
        print(f"\n📁 Output Files:")
        print(f"   1. enriched_data/578_temples_enriched_final.json")
        print(f"   2. enriched_data/578_temples_coordinates_final.json")
        print(f"   3. enriched_data/578_temples_websites_final.json")
        print(f"   4. enriched_data/enrichment_summary_final.json")
        
        print(f"\n💰 Total Cost: $0 (All free methods)")
        print(f"⏱️ Estimated Time: ~30 minutes")
        
        print("\n✅ Next Steps:")
        print("   1. Integrate enriched data into unified_temple_data_v2.json")
        print("   2. Manually verify high-priority temple websites")
        print("   3. Use coordinates for map features")
        print("   4. Display 'Official Website' links in app")
    
    def run_enrichment(self):
        """Main enrichment pipeline"""
        print("\n" + "="*70)
        print(" 🚀 STARTING FREE DATA ENRICHMENT FOR 578 MAJOR TEMPLES")
        print("="*70)
        
        start_time = time.time()
        
        # Phase 1: Coordinates
        self.get_coordinates_osm()
        
        # Phase 2: URL Patterns
        self.check_temple_websites_patterns()
        
        # Phase 3: DuckDuckGo Search
        self.search_websites_duckduckgo()
        
        # Phase 4: Known Websites
        self.add_known_websites()
        
        # Save final results
        self.save_results(intermediate=False)
        
        # Generate report
        self.generate_report()
        
        elapsed = time.time() - start_time
        print(f"\n⏱️ Total processing time: {elapsed/60:.1f} minutes")

def main():
    """Main entry point"""
    print("\n🏛️ Tamil Nadu Major Temples - Free Data Enrichment")
    print("This script will enrich 578 major temples with:")
    print("  • Coordinates from OpenStreetMap")
    print("  • Official websites via pattern matching and search")
    print("  • No API keys or costs required")
    print("\nEstimated time: 30 minutes")
    
    enricher = MajorTemplesEnricher()
    enricher.run_enrichment()
    
    print("\n✨ Enrichment complete! Check enriched_data/ folder for results.")

if __name__ == "__main__":
    main()