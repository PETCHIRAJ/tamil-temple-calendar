#!/usr/bin/env python3
"""
Sync temple data from JSON to SQLite database
Ensures consistency between temple_data.json and app_temples_unified.db
"""

import json
import sqlite3
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent

def sync_json_to_database():
    """Sync enriched temple data from JSON to SQLite database"""
    
    # Paths
    json_path = PROJECT_ROOT / 'design' / 'mockups' / 'temple_data.json'
    db_path = PROJECT_ROOT / 'project-data' / 'database' / 'app_temples_unified.db'
    
    if not json_path.exists():
        print(f"Error: JSON file not found at {json_path}")
        return False
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return False
    
    # Load JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    temples_updated = 0
    temples_inserted = 0
    
    # Process each temple
    for temple in json_data['app_temples']:
        # Check if temple has enrichment data
        has_enrichment = any([
            temple.get('timings'),
            temple.get('festivals'),
            temple.get('special_features'),
            temple.get('holy_water'),
            temple.get('sacred_tree'),
            temple.get('history'),
            temple.get('prayer_benefits'),
            temple.get('other_deities'),
            temple.get('architecture'),
            temple.get('how_to_reach')
        ])
        
        if has_enrichment:
            # Check if enrichment exists
            cursor.execute('SELECT temple_id FROM temple_enrichments WHERE temple_id = ?', (temple['id'],))
            exists = cursor.fetchone()
            
            # Prepare prayer_benefits as part of special_features if it exists
            special_features = temple.get('special_features', [])
            if temple.get('prayer_benefits'):
                # Add prayer benefits to special features with a header
                special_features = special_features + ['Prayer Benefits:'] + temple.get('prayer_benefits', [])
            
            if exists:
                # Update existing enrichment
                cursor.execute('''
                    UPDATE temple_enrichments 
                    SET timings = ?,
                        festivals = ?,
                        special_features = ?,
                        holy_water = ?,
                        sacred_tree = ?,
                        historical_info = ?,
                        how_to_reach = ?,
                        deity_others = ?,
                        deity_main = ?
                    WHERE temple_id = ?
                ''', (
                    temple.get('timings'),
                    json.dumps(temple.get('festivals', []), ensure_ascii=False),
                    json.dumps(special_features, ensure_ascii=False),
                    json.dumps(temple.get('holy_water', []), ensure_ascii=False),
                    temple.get('sacred_tree'),
                    temple.get('history'),
                    temple.get('how_to_reach'),
                    json.dumps(temple.get('other_deities', []), ensure_ascii=False),
                    temple.get('deity_main'),
                    temple['id']
                ))
                temples_updated += 1
                print(f"Updated: {temple['name']}")
            else:
                # Insert new enrichment
                cursor.execute('''
                    INSERT INTO temple_enrichments 
                    (temple_id, timings, festivals, special_features, holy_water, 
                     sacred_tree, historical_info, how_to_reach, deity_others, deity_main)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    temple['id'],
                    temple.get('timings'),
                    json.dumps(temple.get('festivals', []), ensure_ascii=False),
                    json.dumps(special_features, ensure_ascii=False),
                    json.dumps(temple.get('holy_water', []), ensure_ascii=False),
                    temple.get('sacred_tree'),
                    temple.get('history'),
                    temple.get('how_to_reach'),
                    json.dumps(temple.get('other_deities', []), ensure_ascii=False),
                    temple.get('deity_main')
                ))
                temples_inserted += 1
                print(f"Inserted: {temple['name']}")
        
        # Update main temples table with GPS and other data
        if temple.get('latitude') and temple.get('longitude'):
            cursor.execute('''
                UPDATE temples 
                SET latitude = ?, 
                    longitude = ?,
                    gm_rating = ?,
                    gm_phone = ?,
                    gm_website = ?,
                    gm_popular_times = ?
                WHERE id = ?
            ''', (
                temple.get('latitude'),
                temple.get('longitude'),
                temple.get('gm_rating'),
                temple.get('gm_phone'),
                temple.get('gm_website'),
                json.dumps(temple.get('popular_times', []), ensure_ascii=False),
                temple['id']
            ))
    
    # Commit changes
    conn.commit()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM temple_enrichments')
    total_enriched = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM temples WHERE latitude != 0 AND longitude != 0')
    total_with_gps = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n=== Sync Complete ===")
    print(f"Temples updated: {temples_updated}")
    print(f"Temples inserted: {temples_inserted}")
    print(f"Total enriched temples in DB: {total_enriched}")
    print(f"Total temples with GPS: {total_with_gps}")
    
    return True

if __name__ == "__main__":
    success = sync_json_to_database()
    sys.exit(0 if success else 1)