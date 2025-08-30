#!/usr/bin/env python3
"""
Update temple districts for temples currently showing 'Tamil Nadu' as district
"""

import json
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent

# Known temple locations
TEMPLE_DISTRICTS = {
    # TOUR temples - famous pilgrimage sites
    'TOUR_001': {
        'name': 'Thiruchendur Murugan Temple',
        'district': 'Thoothukudi District',
        'location': 'Thiruchendur, Thoothukudi District',
        'pincode': '628215'
    },
    'TOUR_002': {
        'name': 'Swamimalai Murugan Temple',
        'district': 'Thanjavur District',
        'location': 'Swamimalai, Kumbakonam, Thanjavur District',
        'pincode': '612302'
    },
    'TOUR_003': {
        'name': 'Thiruthani Murugan Temple',
        'district': 'Tiruvallur District',
        'location': 'Thiruthani, Tiruvallur District',
        'pincode': '631209'
    },
    'TOUR_004': {
        'name': 'Pazhamudircholai Murugan Temple',
        'district': 'Madurai District',
        'location': 'Pazhamudircholai, Madurai District',
        'pincode': '625107'
    },
    'TOUR_005': {
        'name': 'Palani Murugan Temple',
        'district': 'Dindigul District',
        'location': 'Palani, Dindigul District',
        'pincode': '624601'
    },
    'TOUR_006': {
        'name': 'Nataraja Temple Chidambaram',
        'district': 'Cuddalore District',
        'location': 'Chidambaram, Cuddalore District',
        'pincode': '608001'
    },
    'TOUR_007': {
        'name': 'Suryanar Kovil',
        'district': 'Thanjavur District',
        'location': 'Suryanar Kovil, Kumbakonam, Thanjavur District',
        'pincode': '612702'
    },
    'TOUR_008': {
        'name': 'Thingalur Chandran Temple',
        'district': 'Thanjavur District',
        'location': 'Thingalur, Thanjavur District',
        'pincode': '612204'
    },
    'TOUR_009': {
        'name': 'Vaitheeswaran Kovil',
        'district': 'Mayiladuthurai District',
        'location': 'Vaitheeswaran Kovil, Mayiladuthurai District',
        'pincode': '609117'
    },
    'TOUR_010': {
        'name': 'Thiruvenkadu Budhan Temple',
        'district': 'Mayiladuthurai District',
        'location': 'Thiruvenkadu, Mayiladuthurai District',
        'pincode': '609115'
    },
    # Navagraha temples we added
    'TM090001': {
        'name': 'Alangudi Guru Temple',
        'district': 'Tiruvarur District',
        'location': 'Alangudi, Tiruvarur District',
        'pincode': '612801'
    },
    'TM090002': {
        'name': 'Kanjanur Sukran Temple',
        'district': 'Thanjavur District',
        'location': 'Kanjanur, Thanjavur District',
        'pincode': '612703'
    },
    'TM090003': {
        'name': 'Thirunallar Sani Temple',
        'district': 'Karaikal District',
        'location': 'Thirunallar, Karaikal, Puducherry',
        'pincode': '609607'
    },
    'TM090004': {
        'name': 'Thirunageswaram Rahu Temple',
        'district': 'Thanjavur District',
        'location': 'Thirunageswaram, Kumbakonam, Thanjavur District',
        'pincode': '612204'
    },
    'TM090005': {
        'name': 'Keezhperumpallam Ketu Temple',
        'district': 'Mayiladuthurai District',
        'location': 'Keezhperumpallam, Poompuhar, Mayiladuthurai District',
        'pincode': '609115'
    }
}

def update_temple_districts():
    """Update temple districts in JSON file"""
    
    # Load JSON data
    json_path = PROJECT_ROOT / 'design' / 'mockups' / 'temple_data.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated_count = 0
    
    # Update temples
    for temple in data['app_temples']:
        if temple['id'] in TEMPLE_DISTRICTS:
            updates = TEMPLE_DISTRICTS[temple['id']]
            
            # Update district
            old_district = temple.get('district', '')
            temple['district'] = updates['district']
            
            # Add location if missing
            if not temple.get('location'):
                temple['location'] = updates['location']
            
            # Add address with pincode
            if not temple.get('gm_address'):
                temple['gm_address'] = f"{updates['location']} - {updates['pincode']}"
            
            print(f"Updated {temple['id']}: {temple['name']}")
            print(f"  District: {old_district} -> {updates['district']}")
            updated_count += 1
    
    # Save updated JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Updated {updated_count} temples with correct districts")
    return updated_count

if __name__ == "__main__":
    update_temple_districts()