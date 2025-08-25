#!/usr/bin/env python3
"""
Create Verification File for Temple Matching
=============================================
Generates a JSON file with scraped temples and their potential DB matches
for manual or LLM verification.
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

def get_potential_matches(scraped_temple, conn, limit=5):
    """Get top potential matches from database"""
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
    
    # Query database for potential matches
    query = """
    SELECT temple_id, name, district, location, address, main_deity, latitude, longitude
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
        
        # Overall score
        score = name_sim * 0.6
        if city_match:
            score += 20
        if deity_sim > 50:
            score += deity_sim * 0.2
        
        matches.append({
            'temple_id': db_temple['temple_id'],
            'name': db_temple['name'],
            'district': db_temple['district'],
            'location': db_temple.get('location', ''),
            'address': db_temple.get('address', ''),
            'main_deity': db_temple.get('main_deity', ''),
            'name_similarity': round(name_sim, 1),
            'deity_similarity': round(deity_sim, 1),
            'city_match': city_match,
            'overall_score': round(score, 1)
        })
    
    # Sort by score and return top matches
    matches.sort(key=lambda x: x['overall_score'], reverse=True)
    return matches[:limit]

def main():
    """Generate verification file"""
    print("🔍 Creating Temple Verification File...")
    print("=" * 60)
    
    # Load scraped data
    with open('findmytemple_master_scraped_data.json', 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)
    
    # Connect to database
    conn = sqlite3.connect('database/temples.db')
    conn.row_factory = sqlite3.Row
    
    verification_data = {
        'metadata': {
            'purpose': 'Manual or LLM verification of temple matches',
            'total_temples': len(scraped_data['temples_scraped']),
            'instructions': 'Review each temple and its potential matches. Select the correct match or mark as new temple.',
            'verification_guidelines': [
                'Score > 80: Likely correct match',
                'Score 60-80: Possible match, verify details',
                'Score < 60: Probably different temple',
                'Consider name variations, location, and deity',
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
            address = location
        else:
            district = location.get('district', '')
            city = location.get('city', '')
            address = location.get('address', '')
        
        # Get deities
        deities = temple.get('deities', {})
        if isinstance(deities, list):
            main_deity = ', '.join(deities) if deities else ''
            goddess = ''
        else:
            main_deity = deities.get('main_deity', '')
            goddess = deities.get('goddess', '')
        
        # Get holy elements
        holy_elements = temple.get('holy_elements', {})
        if isinstance(holy_elements, dict):
            holy_water = holy_elements.get('holy_water', '')
            if isinstance(holy_water, list):
                holy_water = ', '.join(holy_water)
            sacred_tree = holy_elements.get('sacred_tree', '')
        else:
            holy_water = ''
            sacred_tree = ''
        
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
        timings = practical.get('timings', '') if isinstance(practical, dict) else ''
        
        # Create verification entry
        entry = {
            'findmytemple_id': temple['temple_id'],
            'findmytemple_data': {
                'name': temple.get('name', ''),
                'district': district,
                'city': city,
                'address': address,
                'main_deity': main_deity,
                'goddess': goddess,
                'holy_water': holy_water,
                'sacred_tree': sacred_tree,
                'festivals': festivals_str,
                'timings': timings,
                'data_completeness': temple.get('data_completeness', 0)
            },
            'potential_db_matches': get_potential_matches(temple, conn),
            'verification_status': 'pending',
            'verified_match': None,
            'verification_notes': ''
        }
        
        verification_data['temples_to_verify'].append(entry)
        
        if i % 50 == 0:
            print(f"Processed {i}/{len(scraped_data['temples_scraped'])} temples...")
    
    # Save verification file
    with open('temple_verification_manual.json', 'w', encoding='utf-8') as f:
        json.dump(verification_data, f, indent=2, ensure_ascii=False)
    
    # Create a simplified CSV version for easier review
    import csv
    with open('temple_verification_simple.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'FindMyTemple_ID', 'Temple_Name', 'District', 'City', 'Main_Deity',
            'Best_Match_ID', 'Best_Match_Name', 'Match_Score', 'Match_District'
        ])
        
        for temple in verification_data['temples_to_verify']:
            fmt_data = temple['findmytemple_data']
            best_match = temple['potential_db_matches'][0] if temple['potential_db_matches'] else {}
            
            writer.writerow([
                temple['findmytemple_id'],
                fmt_data['name'],
                fmt_data['district'],
                fmt_data['city'],
                fmt_data['main_deity'],
                best_match.get('temple_id', ''),
                best_match.get('name', ''),
                best_match.get('overall_score', 0),
                best_match.get('district', '')
            ])
    
    conn.close()
    
    print("\n✅ Verification files created:")
    print("  - temple_verification_manual.json (full details)")
    print("  - temple_verification_simple.csv (quick review)")
    
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