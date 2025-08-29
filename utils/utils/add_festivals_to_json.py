#!/usr/bin/env python3
"""
Add festival data to temple_data.json for the HTML app
"""

import json

def add_festivals_to_json():
    """Add festival data to temple_data.json"""
    
    print("📅 Adding festivals to temple_data.json...")
    
    # Load existing temple data
    with open('../design/mockups/temple_data.json', 'r') as f:
        temple_data = json.load(f)
    
    # Load festival data
    with open('../project-data/festivals_2025_complete.json', 'r') as f:
        festival_data = json.load(f)
    
    # Prepare festivals array
    all_festivals = []
    
    # Process major annual festivals
    for fest in festival_data.get('major_annual_festivals', []):
        all_festivals.append({
            'date': fest['date'],
            'name': fest['name'],
            'tamil_name': fest.get('tamil_name', ''),
            'type': 'major',
            'category': 'annual',
            'temples': 'All major temples'
        })
    
    # Process Pradosham dates
    for prad in festival_data['festivals'].get('pradosham', []):
        all_festivals.append({
            'date': prad['date'],
            'name': prad['type'],
            'tamil_name': 'பிரதோஷம்',
            'type': 'pradosham',
            'category': 'monthly',
            'temples': 'All Shiva temples',
            'tamil_month': prad.get('tamil_month', '')
        })
    
    # Process Ekadashi dates
    for ekad in festival_data['festivals'].get('ekadashi', []):
        all_festivals.append({
            'date': ekad['date'],
            'name': ekad.get('type', 'Ekadashi'),
            'tamil_name': 'ஏகாதசி',
            'type': 'ekadashi',
            'category': 'monthly',
            'temples': 'All Vishnu temples',
            'tamil_month': ekad.get('tamil_month', '')
        })
    
    # Process Pournami dates
    for pourn in festival_data['festivals'].get('pournami', []):
        all_festivals.append({
            'date': pourn['date'],
            'name': 'Pournami',
            'tamil_name': 'பௌர்ணமி',
            'type': 'pournami',
            'category': 'monthly',
            'temples': 'Full moon worship',
            'tamil_month': pourn.get('tamil_month', '')
        })
    
    # Process Amavasya dates
    for amav in festival_data['festivals'].get('amavasya', []):
        all_festivals.append({
            'date': amav['date'],
            'name': 'Amavasya',
            'tamil_name': 'அமாவாசை',
            'type': 'amavasya',
            'category': 'monthly',
            'temples': 'New moon observance',
            'tamil_month': amav.get('tamil_month', '')
        })
    
    # Sort by date
    all_festivals.sort(key=lambda x: x['date'])
    
    # Add festivals to temple data
    temple_data['festivals'] = all_festivals
    
    # Add summary
    temple_data['festival_summary'] = {
        'total': len(all_festivals),
        'major': len([f for f in all_festivals if f['type'] == 'major']),
        'pradosham': len([f for f in all_festivals if f['type'] == 'pradosham']),
        'ekadashi': len([f for f in all_festivals if f['type'] == 'ekadashi']),
        'pournami': len([f for f in all_festivals if f['type'] == 'pournami']),
        'amavasya': len([f for f in all_festivals if f['type'] == 'amavasya']),
        'year': 2025
    }
    
    # Save updated temple data
    with open('../design/mockups/temple_data.json', 'w', encoding='utf-8') as f:
        json.dump(temple_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Added {len(all_festivals)} festivals to temple_data.json")
    print(f"   - Major: {temple_data['festival_summary']['major']}")
    print(f"   - Pradosham: {temple_data['festival_summary']['pradosham']}")
    print(f"   - Ekadashi: {temple_data['festival_summary']['ekadashi']}")
    print(f"   - Pournami: {temple_data['festival_summary']['pournami']}")
    print(f"   - Amavasya: {temple_data['festival_summary']['amavasya']}")

if __name__ == "__main__":
    add_festivals_to_json()