#!/usr/bin/env python3
"""
Enhanced Verification File with Complete HRCE Database Fields
==============================================================
Pulls ALL data from HRCE database for comprehensive comparison
"""

import json
import sqlite3
from pathlib import Path
from difflib import SequenceMatcher
import re

def clean_name(name):
    """Clean temple name for comparison"""
    if not name:
        return ""
    if isinstance(name, list):
        name = name[0] if name else ""
    name = str(name)
    # Remove prefixes and suffixes
    name = re.sub(r'^(Arulmigu\s+|Sri\s+|Shri\s+|Shree\s+)', '', name, flags=re.I)
    name = re.sub(r'\s+(Temple|Kovil|Koil|Swamy|Swami|Samy)$', '', name, flags=re.I)
    return ' '.join(name.split()).strip()

def calculate_similarity(name1, name2):
    """Calculate name similarity"""
    clean1 = clean_name(name1).lower()
    clean2 = clean_name(name2).lower()
    if not clean1 or not clean2:
        return 0
    return SequenceMatcher(None, clean1, clean2).ratio() * 100

def normalize_district(district):
    """Normalize district names"""
    if not district:
        return ""
    district = re.sub(r'\s+District$', '', district, flags=re.I)
    district_map = {
        'tanjore': 'thanjavur',
        'tirunelveli': 'tirunelveli',
        'trichy': 'thiruchirappalli',
        'tiruchirappalli': 'thiruchirappalli',
        'madurai': 'madurai'
    }
    clean = district.lower().strip()
    return district_map.get(clean, clean)

def get_potential_matches_full(scraped_temple, conn, limit=5):
    """Get top potential matches with ALL database fields"""
    name = scraped_temple.get('name', '')
    location = scraped_temple.get('location', {})
    
    if isinstance(location, str):
        district = ''
        city = ''
        address = location
    else:
        district = normalize_district(location.get('district', ''))
        city = location.get('city', '')
        address = location.get('address', '')
    
    # Get deities
    deities = scraped_temple.get('deities', {})
    if isinstance(deities, list):
        main_deity = deities[0] if deities else ''
        goddess = ''
    else:
        main_deity = deities.get('main_deity', '')
        goddess = deities.get('goddess', '')
    
    # Query ALL available fields from database for potential matches
    query = """
    SELECT 
        temple_id,
        name,
        tamil_name,
        district,
        location,
        address,
        pincode,
        income_category,
        temple_type,
        deity_type,
        latitude,
        longitude,
        phone,
        established_year,
        historical_period,
        architectural_style,
        main_deity,
        other_deities,
        festivals,
        timings,
        raw_data,
        wikipedia_url,
        hrce_url,
        official_url
    FROM temples
    WHERE 1=1
    """
    
    params = []
    
    # Add district filter if available
    if district:
        query += " AND district LIKE ?"
        params.append(f'%{district}%')
    
    cursor = conn.execute(query, params)
    matches = []
    
    for row in cursor:
        db_temple = dict(row)
        
        # Calculate similarity
        name_sim = calculate_similarity(name, db_temple['name'])
        
        # Check if city appears in address/location
        city_match = False
        if city and db_temple.get('address'):
            if city.lower() in db_temple['address'].lower():
                city_match = True
        
        # Calculate deity similarity
        deity_sim = 0
        if main_deity and db_temple.get('main_deity'):
            deity_sim = calculate_similarity(main_deity, db_temple['main_deity'])
        
        # Overall score (no goddess field in DB)
        score = name_sim * 0.5
        if city_match:
            score += 20
        if deity_sim > 50:
            score += deity_sim * 0.3
        
        # Create comprehensive match object with ALL available database fields
        match_data = {
            # Core identification
            'temple_id': db_temple['temple_id'],
            'name': db_temple['name'],
            'tamil_name': db_temple.get('tamil_name', ''),
            
            # Location details
            'district': db_temple['district'],
            'location': db_temple.get('location', ''),
            'address': db_temple.get('address', ''),
            'pincode': db_temple.get('pincode', ''),
            'latitude': db_temple.get('latitude'),
            'longitude': db_temple.get('longitude'),
            
            # Temple classification
            'income_category': db_temple.get('income_category', ''),
            'temple_type': db_temple.get('temple_type', ''),
            'deity_type': db_temple.get('deity_type', ''),
            
            # Historical information
            'established_year': db_temple.get('established_year'),
            'historical_period': db_temple.get('historical_period', ''),
            'architectural_style': db_temple.get('architectural_style', ''),
            
            # Deities and worship
            'main_deity': db_temple.get('main_deity', ''),
            'other_deities': db_temple.get('other_deities', ''),
            'festivals': db_temple.get('festivals', ''),
            'timings': db_temple.get('timings', ''),
            
            # Contact and references
            'phone': db_temple.get('phone', ''),
            'wikipedia_url': db_temple.get('wikipedia_url', ''),
            'hrce_url': db_temple.get('hrce_url', ''),
            'official_url': db_temple.get('official_url', ''),
            
            # Raw data (may contain additional info)
            'raw_data': db_temple.get('raw_data', ''),
            
            # Similarity scores
            'name_similarity': round(name_sim, 1),
            'deity_similarity': round(deity_sim, 1),
            'city_match': city_match,
            'overall_score': round(score, 1)
        }
        
        matches.append(match_data)
    
    # Sort by score and return top matches
    matches.sort(key=lambda x: x['overall_score'], reverse=True)
    return matches[:limit]

def main():
    """Generate enhanced verification file with complete HRCE data"""
    print("🔍 Creating Enhanced Temple Verification File with Full HRCE Data...")
    print("=" * 60)
    
    # Load scraped data
    with open('../findmytemple_master_scraped_data.json', 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)
    
    # Connect to database
    conn = sqlite3.connect('../database/temples.db')
    conn.row_factory = sqlite3.Row
    
    # First, let's check what columns we have in the database
    cursor = conn.execute("PRAGMA table_info(temples)")
    columns = cursor.fetchall()
    print("\n📊 Available HRCE Database Columns:")
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")
    
    verification_data = {
        'metadata': {
            'purpose': 'Enhanced verification with complete HRCE database fields',
            'total_temples': len(scraped_data['temples_scraped']),
            'hrce_fields_included': [col['name'] for col in columns],
            'instructions': 'Review each temple with FULL data from both sources',
            'verification_guidelines': [
                'Score > 80: Likely correct match',
                'Score 60-80: Possible match, verify details',
                'Score < 60: Probably different temple',
                'Compare ALL fields: deities, location, festivals, holy elements',
                'Mark as "new_temple" if no good match exists'
            ]
        },
        'temples_to_verify': []
    }
    
    # Process each scraped temple
    for i, temple in enumerate(scraped_data['temples_scraped'], 1):
        location = temple.get('location', {})
        if isinstance(location, str):
            district = ''
            city = ''
            taluk = ''
            village = ''
            state = 'Tamil Nadu'
            country = 'India'
            pincode = ''
            address = location
            latitude = None
            longitude = None
        else:
            district = location.get('district', '')
            city = location.get('city', '')
            taluk = location.get('taluk', '')
            village = location.get('village', '')
            state = location.get('state', 'Tamil Nadu')
            country = location.get('country', 'India')
            pincode = location.get('pincode', '')
            address = location.get('address', '')
            coordinates = location.get('coordinates', {})
            if isinstance(coordinates, dict):
                latitude = coordinates.get('latitude')
                longitude = coordinates.get('longitude')
            else:
                latitude = None
                longitude = None
        
        # Get deities
        deities = temple.get('deities', {})
        if isinstance(deities, list):
            main_deity = ', '.join(deities) if deities else ''
            goddess = ''
            other_deities_list = []
        else:
            main_deity = deities.get('main_deity', '')
            goddess = deities.get('goddess', '')
            other_deities = deities.get('other_deities', [])
            if isinstance(other_deities, list):
                other_deities_list = other_deities
            else:
                other_deities_list = []
        
        # Get holy elements
        holy_elements = temple.get('holy_elements', {})
        if isinstance(holy_elements, dict):
            holy_water = holy_elements.get('holy_water', '')
            if isinstance(holy_water, list):
                holy_water = ', '.join(holy_water)
            sacred_tree = holy_elements.get('sacred_tree', '')
            temple_tank = holy_elements.get('temple_tank', '')
        else:
            holy_water = ''
            sacred_tree = ''
            temple_tank = ''
        
        # Get festivals
        festivals = temple.get('festivals', [])
        if isinstance(festivals, list):
            festival_names = []
            for f in festivals:
                if isinstance(f, dict):
                    festival_names.append(f.get('festival', f.get('name', '')))
                else:
                    festival_names.append(str(f))
            festivals_str = ', '.join(filter(None, festival_names))
        else:
            festivals_str = str(festivals)
        
        # Get practical info
        practical = temple.get('practical_info', {})
        if isinstance(practical, dict):
            timings = practical.get('timings', '')
            pooja_schedule = practical.get('pooja_schedule', '')
            how_to_reach = practical.get('how_to_reach', '')
            phone = practical.get('phone', '')
        else:
            timings = ''
            pooja_schedule = ''
            how_to_reach = ''
            phone = ''
        
        # Get historical info
        historical_info = temple.get('historical_info', '')
        special_features = temple.get('special_features', [])
        if isinstance(special_features, list):
            special_features_str = ', '.join(special_features)
        else:
            special_features_str = str(special_features)
        
        # Create verification entry with all location data
        entry = {
            'findmytemple_id': temple['temple_id'],
            'findmytemple_data': {
                'name': temple.get('name', ''),
                'location': {
                    'district': district,
                    'city': city,
                    'taluk': taluk,
                    'village': village,
                    'state': state,
                    'country': country,
                    'pincode': pincode,
                    'full_address': address,
                    'latitude': latitude,
                    'longitude': longitude
                },
                'deities': {
                    'main_deity': main_deity,
                    'goddess': goddess,
                    'other_deities': other_deities_list
                },
                'holy_elements': {
                    'holy_water': holy_water,
                    'sacred_tree': sacred_tree,
                    'temple_tank': temple_tank
                },
                'worship_info': {
                    'timings': timings,
                    'pooja_schedule': pooja_schedule,
                    'phone': phone,
                    'how_to_reach': how_to_reach
                },
                'cultural_info': {
                    'festivals': festivals_str,
                    'historical_info': historical_info,
                    'special_features': special_features_str
                },
                'data_completeness': temple.get('data_completeness', 0)
            },
            'potential_db_matches': get_potential_matches_full(temple, conn),
            'verification_status': 'pending',
            'verified_match': None,
            'verification_notes': ''
        }
        
        verification_data['temples_to_verify'].append(entry)
        
        if i % 50 == 0:
            print(f"Processed {i}/{len(scraped_data['temples_scraped'])} temples...")
    
    # Save enhanced verification file
    with open('temple_verification_full.json', 'w', encoding='utf-8') as f:
        json.dump(verification_data, f, indent=2, ensure_ascii=False)
    
    conn.close()
    
    print("\n✅ Enhanced verification file created: temple_verification_full.json")
    print("📊 This file includes ALL fields from HRCE database for comprehensive comparison")
    
    # Statistics
    high_confidence = sum(1 for t in verification_data['temples_to_verify'] 
                          if t['potential_db_matches'] and t['potential_db_matches'][0]['overall_score'] > 80)
    medium_confidence = sum(1 for t in verification_data['temples_to_verify'] 
                           if t['potential_db_matches'] and 60 <= t['potential_db_matches'][0]['overall_score'] <= 80)
    low_confidence = sum(1 for t in verification_data['temples_to_verify'] 
                        if t['potential_db_matches'] and t['potential_db_matches'][0]['overall_score'] < 60)
    no_matches = sum(1 for t in verification_data['temples_to_verify'] 
                    if not t['potential_db_matches'])
    
    print(f"\n📊 Verification Statistics:")
    print(f"  High confidence (>80): {high_confidence}")
    print(f"  Medium confidence (60-80): {medium_confidence}")
    print(f"  Low confidence (<60): {low_confidence}")
    print(f"  No potential matches: {no_matches}")

if __name__ == "__main__":
    main()