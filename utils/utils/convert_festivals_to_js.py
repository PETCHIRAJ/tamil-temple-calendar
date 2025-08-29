#!/usr/bin/env python3
"""
Convert recovered festival JSON to JavaScript format for HTML app integration
"""

import json
from datetime import datetime

def convert_festivals():
    # Read the recovered festival data
    with open('../recovered_festivals_2025.json', 'r') as f:
        data = json.load(f)
    
    all_festivals = []
    
    # Process major annual festivals
    for fest in data.get('major_annual_festivals', []):
        all_festivals.append({
            'date': fest['date'],
            'name': fest['name'],
            'tamil_name': fest.get('tamil_name', ''),
            'type': 'major',
            'temples': 'All major temples',
            'category': 'annual'
        })
    
    # Process Pradosham dates
    for prad in data['festivals'].get('pradosham', []):
        all_festivals.append({
            'date': prad['date'],
            'name': prad['type'],
            'tamil_name': 'பிரதோஷம்',
            'type': 'pradosham',
            'temples': 'All Shiva temples - Evening prayers',
            'tamil_month': prad.get('tamil_month', ''),
            'category': 'monthly'
        })
    
    # Process Ekadashi dates
    for ekad in data['festivals'].get('ekadashi', []):
        all_festivals.append({
            'date': ekad['date'],
            'name': ekad.get('type', 'Ekadashi'),
            'tamil_name': 'ஏகாதசி',
            'type': 'ekadashi',
            'temples': 'All Vishnu temples - Fasting day',
            'tamil_month': ekad.get('tamil_month', ''),
            'category': 'monthly'
        })
    
    # Process Pournami (Full Moon) dates
    for pourn in data['festivals'].get('pournami', []):
        all_festivals.append({
            'date': pourn['date'],
            'name': 'Pournami (Full Moon)',
            'tamil_name': 'பௌர்ணமி',
            'type': 'pournami',
            'temples': 'All temples - Full moon worship',
            'tamil_month': pourn.get('tamil_month', ''),
            'category': 'monthly'
        })
    
    # Process Amavasya (New Moon) dates
    for amav in data['festivals'].get('amavasya', []):
        all_festivals.append({
            'date': amav['date'],
            'name': 'Amavasya (New Moon)',
            'tamil_name': 'அமாவாசை',
            'type': 'amavasya',
            'temples': 'Ancestor worship at temples',
            'tamil_month': amav.get('tamil_month', ''),
            'category': 'monthly'
        })
    
    # Sort by date
    all_festivals.sort(key=lambda x: x['date'])
    
    # Generate JavaScript array format
    js_output = "const allFestivals = [\n"
    for fest in all_festivals:
        js_output += f"    {{ date: '{fest['date']}', "
        js_output += f"name: '{fest['name']}', "
        js_output += f"tamil_name: '{fest['tamil_name']}', "
        js_output += f"temples: '{fest['temples']}', "
        js_output += f"type: '{fest['type']}', "
        js_output += f"category: '{fest.get('category', 'annual')}'"
        if 'tamil_month' in fest and fest['tamil_month']:
            js_output += f", tamil_month: '{fest['tamil_month']}'"
        js_output += " },\n"
    js_output += "];\n"
    
    # Save to file
    with open('festivals_js_data.js', 'w') as f:
        f.write(js_output)
    
    print(f"✅ Converted {len(all_festivals)} festivals to JavaScript format")
    print(f"   - Major festivals: {len([f for f in all_festivals if f['type'] == 'major'])}")
    print(f"   - Pradosham: {len([f for f in all_festivals if f['type'] == 'pradosham'])}")
    print(f"   - Ekadashi: {len([f for f in all_festivals if f['type'] == 'ekadashi'])}")
    print(f"   - Pournami: {len([f for f in all_festivals if f['type'] == 'pournami'])}")
    print(f"   - Amavasya: {len([f for f in all_festivals if f['type'] == 'amavasya'])}")

if __name__ == "__main__":
    convert_festivals()