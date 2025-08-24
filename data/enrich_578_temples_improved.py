#!/usr/bin/env python3
"""
Enrichment script for 578 major temples - Improved version
Uses free methods only: OpenStreetMap Nominatim and pattern-based URL discovery
"""

import json
import time
import re
import logging
from pathlib import Path
from datetime import datetime
import requests
from urllib.parse import quote

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MajorTemplesEnricher:
    def __init__(self):
        """Initialize with 578 major temples"""
        # Load the unified temple dataset v2
        logger.info("Loading temple data...")
        with open("../integrated_data/unified_temple_data_v2.json", "r", encoding="utf-8") as f:
            all_temples = json.load(f)
        
        # Filter major temples (578 temples with income category 46_iii)
        # Keep as list of tuples (temple_id, temple_data)
        self.major_temples = [
            (temple_id, temple) for temple_id, temple in all_temples.items()
            if temple.get('income_category') == '46_iii'
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
    
    def normalize_temple_name(self, name):
        """Normalize temple name for URL patterns"""
        # Convert to lowercase
        name = name.lower()
        
        # Remove common prefixes
        prefixes = ['arulmigu', 'sri', 'shri', 'arulmighu']
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()
        
        # Remove common suffixes
        suffixes = ['temple', 'kovil', 'koil', 'devasthanam', 'swamy', 'swami']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()
        
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
        
        for i, (temple_id, temple) in enumerate(self.major_temples, 1):
            temple_name = temple.get('name', '')
            district = temple.get('district', '')
            full_address = temple.get('address', '')
            
            # Extract place name from address (usually after the last comma)
            place_name = ""
            if full_address and ',' in full_address:
                place_name = full_address.split(',')[-1].strip()
            
            # Progress indicator
            if i % 50 == 0:
                logger.info(f"  Progress: {i}/{len(self.major_temples)} temples processed")
            
            # Try different address formats
            addresses = []
            
            # First try with place name if available
            if place_name:
                addresses.append(f"{place_name}, {district}, Tamil Nadu, India")
            
            # Then try with temple name
            addresses.extend([
                f"{temple_name}, {district}, Tamil Nadu, India",
                f"{temple_name}, Tamil Nadu",
            ])
            
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
                            "display_name": location.raw.get('display_name', ''),
                            "confidence": self._calculate_confidence(
                                location.raw.get('display_name', ''),
                                temple_name,
                                district
                            ),
                            "source": "osm_nominatim",
                            "timestamp": datetime.now().isoformat()
                        }
                        success_count += 1
                        location_found = True
                        break
                        
                except (GeocoderTimedOut, GeocoderServiceError) as e:
                    logger.debug(f"    Geocoding error for {temple_name}: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"    Unexpected error for {temple_name}: {str(e)}")
                    continue
            
            if not location_found:
                self.results["failed"]["coordinates"].append({
                    "temple_id": temple_id,
                    "temple_name": temple_name,
                    "reason": "Not found in OSM"
                })
                failed_count += 1
        
        logger.info(f"\n  ✓ Coordinates found: {success_count}")
        logger.info(f"  ✗ Coordinates not found: {failed_count}")
    
    def _calculate_confidence(self, display_name, temple_name, district):
        """Calculate confidence level for geocoding result"""
        display_lower = display_name.lower()
        
        # High confidence if district name is in result
        if district.lower().replace(' district', '') in display_lower:
            return "high"
        
        # Medium confidence if Tamil Nadu is mentioned
        if 'tamil nadu' in display_lower:
            return "medium"
        
        # Low confidence otherwise
        return "low"
    
    def find_websites_pattern(self):
        """Find temple websites using URL patterns"""
        logger.info("\n🌐 PHASE 2: Finding websites using URL patterns...")
        
        success_count = 0
        
        # Common temple website patterns
        url_patterns = [
            # HR&CE patterns
            "https://{normalized_name}.hrce.tn.gov.in",
            "https://hrce.tn.gov.in/temples/{normalized_name}",
            
            # Common temple website patterns
            "https://{normalized_name}temple.com",
            "https://www.{normalized_name}temple.com",
            "https://{normalized_name}temple.org",
            "https://www.{normalized_name}temple.org",
            "https://{normalized_name}.com",
            "https://www.{normalized_name}.com",
        ]
        
        for temple_id, temple in self.major_temples[:50]:  # Test first 50 for patterns
            temple_name = temple.get('name', '')
            normalized = self.normalize_temple_name(temple_name)
            
            if not normalized:
                continue
            
            website_found = False
            
            for pattern in url_patterns:
                url = pattern.format(normalized_name=normalized)
                
                try:
                    # Quick HEAD request to check if URL exists
                    response = requests.head(url, timeout=3, allow_redirects=True)
                    
                    if response.status_code < 400:
                        self.results["websites"][temple_id] = {
                            "url": url,
                            "found_method": "pattern_matching",
                            "verified": True,
                            "timestamp": datetime.now().isoformat()
                        }
                        success_count += 1
                        website_found = True
                        break
                        
                except:
                    continue
            
            if not website_found:
                self.results["failed"]["websites"].append({
                    "temple_id": temple_id,
                    "temple_name": temple_name,
                    "reason": "No pattern matched"
                })
        
        logger.info(f"  ✓ Websites found via patterns: {success_count}")
    
    def find_websites_duckduckgo(self):
        """Find temple websites using DuckDuckGo search (no API key needed)"""
        logger.info("\n🔍 PHASE 3: Finding websites using DuckDuckGo search...")
        
        # Only search for temples without websites
        temples_without_websites = [
            (tid, t) for tid, t in self.major_temples 
            if tid not in self.results["websites"]
        ][:100]  # Limit to 100 searches to avoid rate limiting
        
        logger.info(f"  Searching for {len(temples_without_websites)} temples...")
        
        success_count = 0
        
        for i, (temple_id, temple) in enumerate(temples_without_websites, 1):
            if i % 20 == 0:
                logger.info(f"  Progress: {i}/{len(temples_without_websites)} searches")
            
            temple_name = temple.get('name', '')
            district = temple.get('district', '')
            
            # Search query
            query = f"{temple_name} {district} official website temple"
            
            try:
                # DuckDuckGo instant answer API (no key required)
                url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1"
                
                response = requests.get(url, timeout=5)
                data = response.json()
                
                # Check for official website in abstract URL
                if data.get('AbstractURL'):
                    website_url = data['AbstractURL']
                    
                    # Verify it's likely a temple website
                    if any(keyword in website_url.lower() for keyword in ['temple', 'hrce', 'kovil']):
                        self.results["websites"][temple_id] = {
                            "url": website_url,
                            "found_method": "duckduckgo",
                            "verified": False,
                            "timestamp": datetime.now().isoformat()
                        }
                        success_count += 1
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.debug(f"    Search error for {temple_name}: {str(e)}")
                continue
        
        logger.info(f"  ✓ Websites found via search: {success_count}")
    
    def save_results(self):
        """Save enriched data"""
        output_dir = Path("../enriched_data")
        output_dir.mkdir(exist_ok=True)
        
        # Save individual components
        if self.results["coordinates"]:
            coord_file = output_dir / "578_temples_coordinates_final.json"
            with open(coord_file, "w", encoding="utf-8") as f:
                json.dump(self.results["coordinates"], f, ensure_ascii=False, indent=2)
            logger.info(f"  Saved coordinates to: {coord_file}")
        
        if self.results["websites"]:
            website_file = output_dir / "578_temples_websites_final.json"
            with open(website_file, "w", encoding="utf-8") as f:
                json.dump(self.results["websites"], f, ensure_ascii=False, indent=2)
            logger.info(f"  Saved websites to: {website_file}")
        
        # Save combined enriched data
        enriched_temples = {}
        for temple_id, temple in self.major_temples:
            enriched_temples[temple_id] = {
                "temple_id": temple_id,
                "temple_name": temple.get('name', ''),
                "district": temple.get('district', ''),
                "coordinates": self.results["coordinates"].get(temple_id),
                "website": self.results["websites"].get(temple_id)
            }
        
        enriched_file = output_dir / "578_temples_enriched_final.json"
        with open(enriched_file, "w", encoding="utf-8") as f:
            json.dump(enriched_temples, f, ensure_ascii=False, indent=2)
        logger.info(f"  Saved enriched data to: {enriched_file}")
        
        # Save statistics
        self.results["statistics"] = {
            "total_temples": len(self.major_temples),
            "coordinates_found": len(self.results["coordinates"]),
            "websites_found": len(self.results["websites"]),
            "coordinates_success_rate": f"{len(self.results['coordinates'])/len(self.major_temples)*100:.1f}%",
            "websites_success_rate": f"{len(self.results['websites'])/len(self.major_temples)*100:.1f}%",
            "timestamp": datetime.now().isoformat()
        }
        
        stats_file = output_dir / "enrichment_statistics.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(self.results["statistics"], f, ensure_ascii=False, indent=2)
        logger.info(f"  Saved statistics to: {stats_file}")

def main():
    """Main enrichment pipeline"""
    print("\n" + "="*70)
    print(" 🔄 ENRICHING 578 MAJOR TEMPLES (FREE METHODS)")
    print("="*70)
    
    enricher = MajorTemplesEnricher()
    
    # Phase 1: Get coordinates from OpenStreetMap
    enricher.get_coordinates_osm()
    
    # Phase 2: Find websites using patterns
    enricher.find_websites_pattern()
    
    # Phase 3: Find websites using DuckDuckGo
    enricher.find_websites_duckduckgo()
    
    # Save results
    logger.info("\n💾 Saving enriched data...")
    enricher.save_results()
    
    # Final summary
    print("\n" + "="*70)
    print(" ✅ ENRICHMENT COMPLETE")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"  Total temples: {len(enricher.major_temples)}")
    print(f"  Coordinates found: {len(enricher.results['coordinates'])}")
    print(f"  Websites found: {len(enricher.results['websites'])}")
    print(f"\n📁 Output files saved in: enriched_data/")
    print(f"  - 578_temples_coordinates_final.json")
    print(f"  - 578_temples_websites_final.json")
    print(f"  - 578_temples_enriched_final.json")
    print(f"  - enrichment_statistics.json")
    
    print(f"\n⏭️  Next step: Run validate_and_integrate.py to create v3")

if __name__ == "__main__":
    main()