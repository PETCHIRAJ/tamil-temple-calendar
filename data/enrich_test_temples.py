#!/usr/bin/env python3
"""
Test version of enrichment script - processes only 5 temples for testing
"""

import json
import time
import re
import logging
from pathlib import Path
from datetime import datetime
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TempleEnricherTest:
    """Test enricher for 5 temples only"""
    
    def __init__(self):
        # Load major temples data
        logger.info("Loading temple data...")
        with open("../integrated_data/unified_temple_data_v2.json", "r", encoding="utf-8") as f:
            all_temples = json.load(f)
        
        # Filter only major temples (578 temples) - but take only first 5 for testing
        # Keep as list of tuples (temple_id, temple_data)
        self.major_temples = [
            (temple_id, temple) for temple_id, temple in all_temples.items()
            if temple.get('income_category') == '46_iii'
        ][:5]  # ONLY 5 TEMPLES FOR TESTING
        
        logger.info(f"Testing with {len(self.major_temples)} temples")
        
        # Initialize results
        self.coordinates = {}
        self.websites = {}
        
    def get_coordinates_osm(self):
        """Get coordinates using OpenStreetMap Nominatim"""
        logger.info("\n📍 Getting coordinates from OpenStreetMap...")
        
        try:
            from geopy.geocoders import Nominatim
            from geopy.exc import GeocoderTimedOut, GeocoderServiceError
        except ImportError:
            logger.error("Please install geopy: pip install geopy")
            return
        
        geolocator = Nominatim(
            user_agent="tamil_temple_calendar_app_test_v1",
            timeout=10
        )
        
        for i, (temple_id, temple) in enumerate(self.major_temples, 1):
            temple_name = temple.get('name', '')
            district = temple.get('district', '')
            full_address = temple.get('address', '')
            
            # Extract place name from address (usually after the last comma)
            place_name = ""
            if full_address and ',' in full_address:
                place_name = full_address.split(',')[-1].strip()
            
            logger.info(f"  [{i}/{len(self.major_temples)}] Processing: {temple_name[:50]}...")
            
            # Try geocoding with place name
            if place_name:
                address = f"{place_name}, {district}, Tamil Nadu, India"
                logger.info(f"    Searching for place: {place_name}")
            else:
                address = f"{temple_name}, {district}, Tamil Nadu, India"
            
            try:
                time.sleep(1)  # Rate limiting
                location = geolocator.geocode(address)
                
                if location:
                    self.coordinates[temple_id] = {
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                        "display_name": location.raw.get('display_name', ''),
                        "confidence": "high" if district in location.raw.get('display_name', '') else "medium",
                        "source": "osm_nominatim",
                        "timestamp": datetime.now().isoformat()
                    }
                    logger.info(f"    ✓ Found: {location.latitude:.4f}, {location.longitude:.4f}")
                else:
                    logger.info(f"    ✗ Not found")
                    
            except Exception as e:
                logger.error(f"    ✗ Error: {str(e)[:50]}")
        
        logger.info(f"\n  Total coordinates found: {len(self.coordinates)}/{len(self.major_temples)}")
    
    def save_results(self):
        """Save test results"""
        output_dir = Path("../enriched_data")
        output_dir.mkdir(exist_ok=True)
        
        # Save coordinates
        if self.coordinates:
            coord_file = output_dir / "test_coordinates.json"
            with open(coord_file, "w", encoding="utf-8") as f:
                json.dump(self.coordinates, f, ensure_ascii=False, indent=2)
            logger.info(f"  Saved coordinates to: {coord_file}")
        
        # Save summary
        summary = {
            "test_run": True,
            "temples_processed": len(self.major_temples),
            "coordinates_found": len(self.coordinates),
            "timestamp": datetime.now().isoformat()
        }
        
        summary_file = output_dir / "test_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        logger.info(f"  Saved summary to: {summary_file}")

def main():
    """Run test enrichment"""
    print("\n" + "="*70)
    print(" 🧪 TEST ENRICHMENT FOR 5 TEMPLES")
    print("="*70)
    
    enricher = TempleEnricherTest()
    
    # Get coordinates
    enricher.get_coordinates_osm()
    
    # Save results
    logger.info("\n💾 Saving test results...")
    enricher.save_results()
    
    print("\n" + "="*70)
    print(" ✅ TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()