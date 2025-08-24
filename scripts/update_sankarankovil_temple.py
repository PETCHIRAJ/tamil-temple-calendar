#!/usr/bin/env python3
"""
Update Sankarankovil temple data in database with verified information
"""

import sqlite3
import json
from pathlib import Path

def update_sankarankovil_temple():
    """Update Sankarankovil temple with complete verified data"""
    
    # Connect to database
    db_path = Path('database/temples.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Prepare the update data
    temple_id = 'TM037875'
    
    # Main deity and other deities
    main_deity = 'Sankaranarayanaswamy (Sankara Narayanan - Half Shiva, Half Vishnu)'
    other_deities = json.dumps([
        'Gomathi Amman',
        'Sankaralinga Swami', 
        'Avudai Amman'
    ])
    
    # Timings
    timings = json.dumps({
        'morning': '5:00 AM - 12:30 PM',
        'evening': '4:00 PM - 9:00 PM',
        'special_notes': [
            'Fridays & Sundays: Closes at 1:00 PM',
            'Last Friday of every month: No afternoon closing'
        ]
    })
    
    # Festivals
    festivals = json.dumps([
        {
            'name': 'Adi Thabasu',
            'month': 'Adi (July)',
            'duration': '10 days',
            'significance': 'Commemorates penance of Gomathi Amman'
        },
        {
            'name': 'Pradosham',
            'frequency': 'Twice monthly',
            'timing': '4:30 PM - 6:00 PM'
        },
        {
            'name': 'Equinox Darshan',
            'dates': 'March 21-23, September 21-23',
            'significance': 'Sunlight enters sanctum'
        }
    ])
    
    # URLs
    hrce_url = 'https://sankarankovilsankaranarayanar.hrce.tn.gov.in/'
    wikipedia_url = 'https://en.wikipedia.org/wiki/Sankara_Narayanasamy_Temple'
    
    # Historical period
    historical_period = '900 BC (Ugra Pandiyan) / 10th century CE'
    
    # Update query
    update_query = """
    UPDATE temples 
    SET main_deity = ?,
        other_deities = ?,
        timings = ?,
        festivals = ?,
        hrce_url = ?,
        wikipedia_url = ?,
        historical_period = ?,
        deity_type = ?
    WHERE temple_id = ?
    """
    
    cursor.execute(update_query, (
        main_deity,
        other_deities,
        timings,
        festivals,
        hrce_url,
        wikipedia_url,
        historical_period,
        'Shiva-Vishnu',  # Unique deity type
        temple_id
    ))
    
    # Commit changes
    conn.commit()
    
    # Verify the update
    cursor.execute("""
        SELECT temple_id, name, main_deity, other_deities, timings, 
               festivals, hrce_url, wikipedia_url, historical_period
        FROM temples 
        WHERE temple_id = ?
    """, (temple_id,))
    
    result = cursor.fetchone()
    
    print("✅ Sankarankovil Temple Updated Successfully!")
    print("=" * 60)
    print(f"Temple ID: {result[0]}")
    print(f"Name: {result[1]}")
    print(f"Main Deity: {result[2]}")
    print(f"Other Deities: {json.loads(result[3]) if result[3] else 'None'}")
    print(f"Timings: {json.loads(result[4]) if result[4] else 'None'}")
    print(f"Festivals: {json.loads(result[5]) if result[5] else 'None'}")
    print(f"HR&CE URL: {result[6]}")
    print(f"Wikipedia URL: {result[7]}")
    print(f"Historical Period: {result[8]}")
    
    conn.close()
    
    return result

if __name__ == "__main__":
    update_sankarankovil_temple()
