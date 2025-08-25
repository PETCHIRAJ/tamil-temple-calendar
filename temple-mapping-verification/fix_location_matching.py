#!/usr/bin/env python3
"""
Fix Location-Based Matching
============================
Handle temples with missing or incorrect district information
"""

import json
import sqlite3
import re
from difflib import SequenceMatcher

def fix_district_names(district):
    """Fix common district name issues"""
    
    if not district:
        return ''
    
    district = district.lower().strip()
    
    # Map cities to their actual districts
    city_to_district = {
        'kumbakonam': 'thanjavur',
        'mayiladuthurai': 'mayiladuthurai',  # Now a separate district
        'nagapattinam': 'nagapattinam',
        'thiruvarur': 'thiruvarur',
        'karur': 'karur',
        'erode': 'erode',
        'salem': 'salem',
        'namakkal': 'namakkal',
        'dharmapuri': 'dharmapuri',
        'krishnagiri': 'krishnagiri',
        'vellore': 'vellore',
        'tiruvannamalai': 'tiruvannamalai',
        'villupuram': 'villupuram',
        'cuddalore': 'cuddalore',
        'chidambaram': 'cuddalore',  # Chidambaram is in Cuddalore district
        'kanchipuram': 'kanchipuram',
        'thiruvallur': 'thiruvallur',
        'chennai': 'chennai',
        'madurai': 'madurai',
        'theni': 'theni',
        'dindigul': 'dindigul',
        'ramanathapuram': 'ramanathapuram',
        'sivaganga': 'sivaganga',
        'virudhunagar': 'virudhunagar',
        'thoothukudi': 'thoothukudi',
        'tirunelveli': 'tirunelveli',
        'kanyakumari': 'kanyakumari',
        'coimbatore': 'coimbatore',
        'tiruppur': 'tiruppur',
        'nilgiris': 'nilgiris',
        'tiruchirappalli': 'tiruchirappalli',
        'trichy': 'tiruchirappalli',
        'tanjore': 'thanjavur',
        'thanjavur': 'thanjavur',
        'pudukkottai': 'pudukkottai',
        'ariyalur': 'ariyalur',
        'perambalur': 'perambalur'
    }
    
    # Check if it's actually a city name used as district
    if district in city_to_district:
        return city_to_district[district]
    
    # Handle variations
    district = district.replace(' district', '')
    district = district.replace('nagai', 'nagapattinam')
    
    return district

def match_by_name_only(temple_name, conn):
    """Match purely by name when location is unknown"""
    
    name = temple_name.lower()
    
    # Remove prefixes and suffixes
    prefixes = ['arulmigu', 'sri', 'shri', 'shree', 'thiru']
    suffixes = ['temple', 'kovil', 'koil', 'swamy', 'swami', 'samy']
    
    for prefix in prefixes:
        name = re.sub(f'^{prefix}\\s+', '', name)
    for suffix in suffixes:
        name = re.sub(f'\\s+{suffix}$', '', name)
    
    # Extract key unique words
    key_words = [w for w in name.split() if len(w) > 4]
    
    if not key_words:
        return []
    
    matches = []
    
    # Search for temples with similar names
    query = "SELECT * FROM temples WHERE name LIKE ? LIMIT 30"
    
    for word in key_words[:2]:  # Use first 2 significant words
        cursor = conn.execute(query, (f'%{word}%',))
        
        for row in cursor:
            db_temple = dict(row)
            db_name = db_temple['name'].lower()
            
            # Calculate similarity
            similarity = SequenceMatcher(None, name, db_name).ratio() * 100
            
            if similarity > 60:  # Good name match even without location
                matches.append({
                    'temple_id': db_temple['temple_id'],
                    'name': db_temple['name'],
                    'district': db_temple['district'],
                    'score': similarity,
                    'match_type': 'name_only'
                })
    
    # Sort by score
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches[:3]

def process_unmatched_temples():
    """Try to match the remaining 131 temples"""
    
    # Load previous results
    with open('improved_matching_results.json', 'r') as f:
        results = json.load(f)
    
    conn = sqlite3.connect('../database/temples.db')
    conn.row_factory = sqlite3.Row
    
    newly_matched = []
    still_unmatched = []
    
    print("🔍 Processing unmatched temples...")
    print("=" * 60)
    
    for item in results['no_match']:
        temple = item['findmytemple']
        temple_name = temple['name']
        
        # Try name-only matching
        matches = match_by_name_only(temple_name, conn)
        
        if matches and matches[0]['score'] > 70:
            newly_matched.append({
                'findmytemple': temple,
                'match': matches[0],
                'confidence': 'name_match'
            })
            print(f"✅ Matched: {temple_name[:40]} -> {matches[0]['name'][:40]} ({matches[0]['score']:.1f}%)")
        else:
            still_unmatched.append(temple)
    
    conn.close()
    
    # Save results
    final_results = {
        'newly_matched': newly_matched,
        'still_unmatched': still_unmatched,
        'summary': {
            'newly_matched_count': len(newly_matched),
            'still_unmatched_count': len(still_unmatched)
        }
    }
    
    with open('location_fix_results.json', 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Location Fix Results:")
    print(f"   Newly matched: {len(newly_matched)}")
    print(f"   Still unmatched: {len(still_unmatched)}")
    print(f"\n💡 Total temples matched now: {153 + len(newly_matched)}/284")
    
    return final_results

if __name__ == "__main__":
    results = process_unmatched_temples()
    
    # Calculate final MVP coverage
    original_matched = 153
    new_matches = results['summary']['newly_matched_count']
    total_matched = original_matched + new_matches
    coverage = (total_matched / 284) * 100
    
    print(f"\n🎯 FINAL MVP COVERAGE: {total_matched}/284 temples ({coverage:.1f}%)")
    
    if coverage > 60:
        print("✅ This is GOOD coverage for MVP launch!")
    else:
        print("⚠️ Consider manual matching for key temples")