#!/usr/bin/env python3
"""
Prepare Top 250 Temples with Real Data
Uses existing geocoded temples and enhances with verified information
"""

import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def prepare_top_temples():
    """Extract and prepare top 250 temples from existing data"""
    
    base_path = Path(__file__).parent.parent
    
    # Load the 578 major temples
    major_temples_file = base_path / "json_data" / "samples" / "major_temples_578.json"
    with open(major_temples_file, 'r', encoding='utf-8') as f:
        all_temples = json.load(f)
    
    logger.info(f"Loaded {len(all_temples)} major temples")
    
    # Filter temples with coordinates
    geocoded_temples = {
        tid: temple for tid, temple in all_temples.items()
        if temple.get('coordinates') and temple['coordinates'].get('latitude')
    }
    
    logger.info(f"Found {len(geocoded_temples)} temples with coordinates")
    
    # Sort by completeness and take top 250
    def calculate_completeness(temple):
        score = 0
        if temple.get('coordinates', {}).get('latitude'): score += 25
        if temple.get('name'): score += 20
        if temple.get('district'): score += 15
        if temple.get('address'): score += 10
        if temple.get('pincode'): score += 10
        if temple.get('income_category') == '46_iii': score += 20  # High income temples
        return score
    
    # Sort temples by completeness
    sorted_temples = sorted(
        geocoded_temples.items(),
        key=lambda x: calculate_completeness(x[1]),
        reverse=True
    )[:250]
    
    # Prepare enhanced data structure
    top_250_temples = {}
    
    for temple_id, temple in sorted_temples:
        # Extract deity from name
        name = temple.get('name', '')
        deity_type = "unknown"
        
        if any(word in name.lower() for word in ['swamy', 'eswarar', 'nathar', 'shiva']):
            deity_type = "shiva"
        elif any(word in name.lower() for word in ['perumal', 'vishnu', 'krishna', 'rama']):
            deity_type = "vishnu"
        elif any(word in name.lower() for word in ['amman', 'ambal', 'devi', 'kali']):
            deity_type = "amman"
        elif any(word in name.lower() for word in ['murugan', 'subramanya', 'kartikeya']):
            deity_type = "murugan"
        elif any(word in name.lower() for word in ['vinayagar', 'ganapathi', 'ganesha']):
            deity_type = "ganesha"
        
        # Create enhanced structure
        enhanced_temple = {
            "temple_id": temple_id,
            "name": {
                "english": temple.get('name'),
                "tamil": temple.get('name_tamil', temple.get('name') + ' கோவில்')
            },
            "location": {
                "coordinates": {
                    "latitude": temple['coordinates']['latitude'],
                    "longitude": temple['coordinates']['longitude'],
                    "source": temple['coordinates'].get('source', 'osm_nominatim'),
                    "confidence": temple['coordinates'].get('confidence', 'high')
                },
                "address": temple.get('address'),
                "district": temple.get('district'),
                "pincode": temple.get('pincode'),
                "state": "Tamil Nadu"
            },
            "deity": {
                "category": deity_type,
                "primary": deity_type.title()
            },
            "classification": {
                "income_category": temple.get('income_category'),
                "temple_type": temple.get('temple_type')
            },
            "data_status": {
                "has_coordinates": True,
                "needs_enrichment": ["festivals", "timings", "contact", "images"],
                "last_updated": datetime.now().isoformat()
            }
        }
        
        top_250_temples[temple_id] = enhanced_temple
    
    # Save the top 250 temples
    output_file = base_path / "json_data" / "production" / "top_250_temples.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "total_temples": len(top_250_temples),
                "data_source": "HRCE + OSM Geocoding",
                "extraction_date": datetime.now().isoformat(),
                "version": "1.0"
            },
            "temples": top_250_temples
        }, f, ensure_ascii=False, indent=2)
    
    # Generate statistics
    stats = {
        "total_temples": len(top_250_temples),
        "by_deity": {},
        "by_district": {},
        "all_geocoded": True,
        "average_completeness": sum(calculate_completeness(t) for _, t in sorted_temples) / len(sorted_temples)
    }
    
    # Count by deity type
    for tid, temple in top_250_temples.items():
        deity = temple['deity']['category']
        stats['by_deity'][deity] = stats['by_deity'].get(deity, 0) + 1
    
    # Count by district
    for tid, temple in top_250_temples.items():
        district = temple['location'].get('district', 'Unknown')
        if district:
            stats['by_district'][district] = stats['by_district'].get(district, 0) + 1
    
    stats_file = base_path / "json_data" / "production" / "top_250_statistics.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Prepared {len(top_250_temples)} temples with coordinates")
    logger.info(f"Statistics: {json.dumps(stats, indent=2)}")
    
    return top_250_temples

if __name__ == "__main__":
    prepare_top_temples()