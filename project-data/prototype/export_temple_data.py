#!/usr/bin/env python3
"""
Export real temple data for HTML prototype
"""

import sqlite3
import json
from datetime import datetime

def export_temple_data():
    conn = sqlite3.connect('temple_app_mvp.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get navigation-ready temples
    cursor.execute("""
        SELECT id, name, tamil_name, district, latitude, longitude,
               deity_type, gm_rating, gm_address, gm_phone, gm_website,
               popular_times, is_tour_temple, data_quality
        FROM app_temples
        ORDER BY gm_rating DESC, name
    """)
    
    temples = []
    for row in cursor.fetchall():
        temple = dict(row)
        # Parse popular_times if exists
        if temple['popular_times']:
            try:
                temple['popular_times'] = json.loads(temple['popular_times'])
            except:
                temple['popular_times'] = None
        temples.append(temple)
    
    # Get tour circuits
    cursor.execute("""
        SELECT * FROM tour_circuits
    """)
    
    circuits = [dict(row) for row in cursor.fetchall()]
    
    # Get circuit temples
    for circuit in circuits:
        cursor.execute("""
            SELECT t.*, ct.sequence_order
            FROM app_temples t
            JOIN circuit_temples ct ON t.id = ct.temple_id
            WHERE ct.circuit_id = ?
            ORDER BY ct.sequence_order
        """, (circuit['id'],))
        
        circuit['temples'] = [dict(row) for row in cursor.fetchall()]
    
    # Get all temples for directory
    cursor.execute("""
        SELECT id, name, tamil_name, district, 
               navigation_available, deity_type
        FROM temple_directory
        ORDER BY district, name
    """)
    
    directory = [dict(row) for row in cursor.fetchall()]
    
    # Get district stats
    cursor.execute("""
        SELECT district, COUNT(*) as total,
               SUM(CASE WHEN navigation_available THEN 1 ELSE 0 END) as with_gps
        FROM temple_directory
        GROUP BY district
        ORDER BY total DESC
    """)
    
    districts = [dict(row) for row in cursor.fetchall()]
    
    # Create final data structure
    data = {
        'app_temples': temples,
        'tour_circuits': circuits,
        'temple_directory': directory,
        'districts': districts,
        'stats': {
            'total_temples': len(directory),
            'navigation_ready': len(temples),
            'tour_temples': sum(1 for t in temples if t['is_tour_temple']),
            'premium_temples': sum(1 for t in temples if t['data_quality'] == 'premium'),
            'districts_covered': len(districts)
        },
        'generated_at': datetime.now().isoformat()
    }
    
    # Save to JSON
    with open('demo-ui/temple_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Exported {len(temples)} navigation-ready temples")
    print(f"✅ Exported {len(circuits)} tour circuits")
    print(f"✅ Exported {len(directory)} total temples")
    print(f"📁 Saved to: demo-ui/temple_data.json")
    
    conn.close()

if __name__ == "__main__":
    export_temple_data()