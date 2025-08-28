#!/usr/bin/env python3
"""
Validate and Integrate Enriched Data into Unified Temple Dataset
Creates new version (v3) without modifying existing v2
Includes validation checks before integration
"""

import json
from datetime import datetime
from pathlib import Path
import logging
from math import radians, cos, sin, asin, sqrt
import re
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataValidator:
    """Validate enriched data before integration"""
    
    def __init__(self):
        self.validation_report = {
            "coordinates": {"valid": 0, "invalid": 0, "issues": []},
            "websites": {"valid": 0, "invalid": 0, "issues": []},
            "summary": {}
        }
        
        # Load coordinate corrections if available
        self.corrections = {}
        corrections_file = Path("../enriched_data/coordinate_corrections.json")
        if corrections_file.exists():
            with open(corrections_file, "r", encoding="utf-8") as f:
                corrections_data = json.load(f)
                for correction in corrections_data.get("corrections", []):
                    self.corrections[correction["temple_id"]] = correction["corrected_coordinates"]
            logger.info(f"  Loaded {len(self.corrections)} coordinate corrections")
    
    def validate_coordinates(self, coord_data):
        """Validate coordinate data"""
        logger.info("🔍 Validating coordinates...")
        
        valid_coords = {}
        
        # Apply corrections first
        if self.corrections:
            logger.info(f"  Applying {len(self.corrections)} coordinate corrections...")
            for temple_id, corrected_coords in self.corrections.items():
                if temple_id in coord_data:
                    coord_data[temple_id] = corrected_coords
                    logger.info(f"    ✓ Applied correction for {temple_id}")
        
        for temple_id, coords in coord_data.items():
            issues = []
            
            # Check latitude bounds (Tamil Nadu roughly 8°N to 13°N)
            lat = coords.get('latitude', 0)
            if not (8.0 <= lat <= 13.5):
                issues.append(f"Latitude {lat} outside Tamil Nadu bounds")
            
            # Check longitude bounds (Tamil Nadu roughly 76°E to 80°E)
            lon = coords.get('longitude', 0)
            if not (76.0 <= lon <= 80.5):
                issues.append(f"Longitude {lon} outside Tamil Nadu bounds")
            
            # Check if coordinates are not 0,0
            if lat == 0 or lon == 0:
                issues.append("Invalid null coordinates")
            
            # Check confidence level
            confidence = coords.get('confidence', 'low')
            if confidence == 'low':
                issues.append("Low confidence geocoding")
            
            if not issues:
                valid_coords[temple_id] = coords
                self.validation_report["coordinates"]["valid"] += 1
            else:
                self.validation_report["coordinates"]["invalid"] += 1
                self.validation_report["coordinates"]["issues"].append({
                    "temple_id": temple_id,
                    "issues": issues
                })
                
                # Still include low confidence coords but mark them
                if confidence == 'low' and len(issues) == 1:
                    coords['validation_warning'] = "Low confidence"
                    valid_coords[temple_id] = coords
        
        logger.info(f"  ✓ Valid coordinates: {self.validation_report['coordinates']['valid']}")
        logger.info(f"  ✗ Invalid coordinates: {self.validation_report['coordinates']['invalid']}")
        
        return valid_coords
    
    def validate_website(self, url):
        """Validate a single website URL"""
        try:
            # Basic URL format check
            if not re.match(r'https?://[\w\-\.]+\.\w{2,}', url):
                return False, "Invalid URL format"
            
            # Check if URL is accessible (HEAD request)
            response = requests.head(url, timeout=5, allow_redirects=True)
            
            # Check status code
            if response.status_code >= 400:
                return False, f"HTTP {response.status_code}"
            
            # Check if it's not a generic error page
            if response.headers.get('content-length', '1000000') == '0':
                return False, "Empty response"
            
            return True, "Valid"
            
        except requests.RequestException as e:
            return False, f"Connection error: {str(e)[:50]}"
        except Exception as e:
            return False, f"Validation error: {str(e)[:50]}"
    
    def validate_websites(self, website_data):
        """Validate website data"""
        logger.info("🔍 Validating websites...")
        logger.info("  (This may take a few minutes to check each URL)")
        
        valid_websites = {}
        
        for i, (temple_id, website_info) in enumerate(website_data.items(), 1):
            if i % 50 == 0:
                logger.info(f"  Progress: {i}/{len(website_data)} websites checked")
            
            url = website_info.get('url', '')
            
            # Skip validation for known/verified sites
            if website_info.get('verified', False):
                valid_websites[temple_id] = website_info
                self.validation_report["websites"]["valid"] += 1
                continue
            
            # Validate the URL
            is_valid, reason = self.validate_website(url)
            
            if is_valid:
                website_info['validation_status'] = 'verified'
                website_info['last_validated'] = datetime.now().isoformat()
                valid_websites[temple_id] = website_info
                self.validation_report["websites"]["valid"] += 1
            else:
                self.validation_report["websites"]["invalid"] += 1
                self.validation_report["websites"]["issues"].append({
                    "temple_id": temple_id,
                    "url": url,
                    "issue": reason
                })
                
                # Include with warning if it was found via search
                if website_info.get('found_method') == 'duckduckgo':
                    website_info['validation_warning'] = reason
                    website_info['validation_status'] = 'unverified'
                    valid_websites[temple_id] = website_info
        
        logger.info(f"  ✓ Valid websites: {self.validation_report['websites']['valid']}")
        logger.info(f"  ✗ Invalid websites: {self.validation_report['websites']['invalid']}")
        
        return valid_websites
    
    def generate_validation_report(self):
        """Generate validation summary"""
        self.validation_report["summary"] = {
            "total_coordinates_validated": (
                self.validation_report["coordinates"]["valid"] + 
                self.validation_report["coordinates"]["invalid"]
            ),
            "total_websites_validated": (
                self.validation_report["websites"]["valid"] + 
                self.validation_report["websites"]["invalid"]
            ),
            "validation_timestamp": datetime.now().isoformat()
        }
        
        return self.validation_report

class DataIntegrator:
    """Integrate validated data into unified dataset"""
    
    def __init__(self):
        # Load current unified data (v2)
        logger.info("Loading current unified dataset (v2)...")
        with open("../integrated_data/unified_temple_data_v2.json", "r", encoding="utf-8") as f:
            self.unified_data = json.load(f)
        
        logger.info(f"  Loaded {len(self.unified_data)} temples")
        
        # Track changes
        self.changes = {
            "coordinates_added": 0,
            "coordinates_updated": 0,
            "websites_added": 0,
            "websites_updated": 0,
            "temples_modified": set()
        }
    
    def backup_current_version(self):
        """Create backup of current version"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"../integrated_data/unified_temple_data_v2_backup_{timestamp}.json"
        
        logger.info(f"Creating backup: {backup_file}")
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(self.unified_data, f, ensure_ascii=False, indent=2)
        
        return backup_file
    
    def integrate_coordinates(self, validated_coords):
        """Integrate validated coordinates"""
        logger.info("Integrating coordinates...")
        
        for temple_id, coord_data in validated_coords.items():
            if temple_id in self.unified_data:
                temple = self.unified_data[temple_id]
                
                # Check if temple already has coordinates
                if temple.get('coordinates'):
                    # Compare with existing
                    existing = temple['coordinates']
                    
                    # Calculate distance between old and new coordinates
                    if 'lat' in existing and 'lon' in existing:
                        old_lat, old_lon = existing['lat'], existing['lon']
                        new_lat, new_lon = coord_data['latitude'], coord_data['longitude']
                        
                        distance = self.haversine(old_lat, old_lon, new_lat, new_lon)
                        
                        # If distance > 1km, flag for review
                        if distance > 1:
                            coord_data['distance_from_existing'] = f"{distance:.2f} km"
                            coord_data['needs_review'] = True
                            logger.warning(f"  ⚠ {temple_id}: New coords {distance:.2f}km from existing")
                    
                    self.changes["coordinates_updated"] += 1
                else:
                    self.changes["coordinates_added"] += 1
                
                # Add coordinates
                temple['coordinates'] = coord_data
                
                # Update sources
                if 'sources' not in temple:
                    temple['sources'] = {}
                temple['sources']['osm_geocoding'] = {
                    "timestamp": datetime.now().isoformat(),
                    "confidence": coord_data.get('confidence', 'medium')
                }
                
                self.changes["temples_modified"].add(temple_id)
        
        logger.info(f"  Added: {self.changes['coordinates_added']} new coordinates")
        logger.info(f"  Updated: {self.changes['coordinates_updated']} existing coordinates")
    
    def integrate_websites(self, validated_websites):
        """Integrate validated websites"""
        logger.info("Integrating websites...")
        
        for temple_id, website_data in validated_websites.items():
            if temple_id in self.unified_data:
                temple = self.unified_data[temple_id]
                
                # Check if temple already has website
                if temple.get('website'):
                    self.changes["websites_updated"] += 1
                    website_data['previous_website'] = temple['website']
                else:
                    self.changes["websites_added"] += 1
                
                # Add website
                temple['website'] = website_data['url']
                temple['website_details'] = {
                    "found_method": website_data.get('found_method'),
                    "validation_status": website_data.get('validation_status', 'unverified'),
                    "last_validated": website_data.get('last_validated'),
                    "validation_warning": website_data.get('validation_warning')
                }
                
                # Update sources
                if 'sources' not in temple:
                    temple['sources'] = {}
                temple['sources']['website_discovery'] = {
                    "timestamp": datetime.now().isoformat(),
                    "method": website_data.get('found_method')
                }
                
                self.changes["temples_modified"].add(temple_id)
        
        logger.info(f"  Added: {self.changes['websites_added']} new websites")
        logger.info(f"  Updated: {self.changes['websites_updated']} existing websites")
    
    def haversine(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in km"""
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return R * c
    
    def save_new_version(self):
        """Save as new version (v3)"""
        output_file = "../integrated_data/unified_temple_data_v3.json"
        
        logger.info(f"Saving new version: {output_file}")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.unified_data, f, ensure_ascii=False, indent=2)
        
        # Save change log
        change_log = {
            "version": "v3",
            "timestamp": datetime.now().isoformat(),
            "changes": {
                "coordinates_added": self.changes["coordinates_added"],
                "coordinates_updated": self.changes["coordinates_updated"],
                "websites_added": self.changes["websites_added"],
                "websites_updated": self.changes["websites_updated"],
                "total_temples_modified": len(self.changes["temples_modified"])
            },
            "modified_temple_ids": list(self.changes["temples_modified"])
        }
        
        log_file = "../integrated_data/v3_change_log.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(change_log, f, ensure_ascii=False, indent=2)
        
        return output_file, log_file
    
    def generate_integration_stats(self):
        """Generate statistics after integration"""
        stats = {
            "total_temples": len(self.unified_data),
            "temples_with_coordinates": 0,
            "temples_with_websites": 0,
            "temples_with_both": 0,
            "major_temples_coverage": {}
        }
        
        # Count enrichments
        major_temples_with_coords = 0
        major_temples_with_websites = 0
        major_temples_total = 0
        
        for temple_id, temple in self.unified_data.items():
            has_coords = bool(temple.get('coordinates'))
            has_website = bool(temple.get('website'))
            
            if has_coords:
                stats["temples_with_coordinates"] += 1
            if has_website:
                stats["temples_with_websites"] += 1
            if has_coords and has_website:
                stats["temples_with_both"] += 1
            
            # Check major temples
            if temple.get('income_category') == '46_iii':
                major_temples_total += 1
                if has_coords:
                    major_temples_with_coords += 1
                if has_website:
                    major_temples_with_websites += 1
        
        stats["major_temples_coverage"] = {
            "total": major_temples_total,
            "with_coordinates": major_temples_with_coords,
            "with_websites": major_temples_with_websites,
            "coords_percentage": f"{major_temples_with_coords/major_temples_total*100:.1f}%",
            "websites_percentage": f"{major_temples_with_websites/major_temples_total*100:.1f}%"
        }
        
        return stats

def main():
    """Main integration pipeline"""
    print("\n" + "="*70)
    print(" 🔄 VALIDATE AND INTEGRATE ENRICHED DATA")
    print("="*70)
    
    # Check if enriched data exists
    enriched_file = Path("../enriched_data/578_temples_enriched_final.json")
    coords_file = Path("../enriched_data/578_temples_coordinates_final.json")
    websites_file = Path("../enriched_data/578_temples_websites_final.json")
    
    if not enriched_file.exists():
        logger.error("Enriched data not found! Run enrich_578_temples_free.py first.")
        return
    
    # Load enriched data
    logger.info("\nLoading enriched data...")
    
    coords_data = {}
    if coords_file.exists():
        with open(coords_file, "r", encoding="utf-8") as f:
            coords_data = json.load(f)
        logger.info(f"  Loaded {len(coords_data)} coordinates")
    
    websites_data = {}
    if websites_file.exists():
        with open(websites_file, "r", encoding="utf-8") as f:
            websites_data = json.load(f)
        logger.info(f"  Loaded {len(websites_data)} websites")
    
    # Step 1: Validate
    validator = DataValidator()
    
    logger.info("\n📋 STEP 1: VALIDATION")
    validated_coords = validator.validate_coordinates(coords_data) if coords_data else {}
    validated_websites = validator.validate_websites(websites_data) if websites_data else {}
    
    validation_report = validator.generate_validation_report()
    
    # Save validation report
    with open("../enriched_data/validation_report.json", "w", encoding="utf-8") as f:
        json.dump(validation_report, f, ensure_ascii=False, indent=2)
    
    # Step 2: Integrate
    logger.info("\n📦 STEP 2: INTEGRATION")
    integrator = DataIntegrator()
    
    # Backup current version
    backup_file = integrator.backup_current_version()
    logger.info(f"  Backup created: {backup_file}")
    
    # Integrate validated data
    integrator.integrate_coordinates(validated_coords)
    integrator.integrate_websites(validated_websites)
    
    # Save new version
    output_file, log_file = integrator.save_new_version()
    
    # Generate statistics
    stats = integrator.generate_integration_stats()
    
    # Save statistics
    stats_file = "../integrated_data/v3_statistics.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    # Final report
    print("\n" + "="*70)
    print(" ✅ INTEGRATION COMPLETE")
    print("="*70)
    
    print(f"\n📊 Integration Summary:")
    print(f"  Temples with coordinates: {stats['temples_with_coordinates']} / {stats['total_temples']}")
    print(f"  Temples with websites: {stats['temples_with_websites']} / {stats['total_temples']}")
    print(f"  Temples with both: {stats['temples_with_both']}")
    
    print(f"\n🏛️ Major Temples Coverage (578 temples):")
    print(f"  With coordinates: {stats['major_temples_coverage']['with_coordinates']} ({stats['major_temples_coverage']['coords_percentage']})")
    print(f"  With websites: {stats['major_temples_coverage']['with_websites']} ({stats['major_temples_coverage']['websites_percentage']})")
    
    print(f"\n📁 Output Files:")
    print(f"  1. New dataset: {output_file}")
    print(f"  2. Change log: {log_file}")
    print(f"  3. Statistics: {stats_file}")
    print(f"  4. Validation report: ../enriched_data/validation_report.json")
    print(f"  5. Backup: {backup_file}")
    
    print(f"\n✨ Version v3 created successfully!")
    print(f"   v2 remains unchanged at: integrated_data/unified_temple_data_v2.json")

if __name__ == "__main__":
    main()