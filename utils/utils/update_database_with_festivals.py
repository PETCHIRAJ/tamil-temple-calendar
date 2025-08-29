#!/usr/bin/env python3
"""
Update SQLite database with complete festival data
"""

import json
import sqlite3
from datetime import datetime

def update_database_with_festivals():
    """Add festivals table and import all 88 festivals"""
    
    print("📅 Updating database with festival data...")
    
    # Load festival data
    with open('../project-data/festivals_2025_complete.json', 'r') as f:
        data = json.load(f)
    
    # Connect to database
    conn = sqlite3.connect('../project-data/database/temple_app_mvp.db')
    cursor = conn.cursor()
    
    # Create festivals table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS festivals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            name TEXT NOT NULL,
            tamil_name TEXT,
            type TEXT,
            category TEXT,
            temples TEXT,
            tamil_month TEXT,
            year INTEGER DEFAULT 2025
        )
    ''')
    
    # Clear existing festivals
    cursor.execute("DELETE FROM festivals")
    print("  Cleared existing festival data")
    
    all_festivals = []
    
    # Process major annual festivals
    for fest in data.get('major_annual_festivals', []):
        all_festivals.append({
            'date': fest['date'],
            'name': fest['name'],
            'tamil_name': fest.get('tamil_name', ''),
            'type': 'major',
            'category': 'annual',
            'temples': 'All major temples',
            'tamil_month': '',
            'year': 2025
        })
    
    # Process Pradosham dates
    for prad in data['festivals'].get('pradosham', []):
        all_festivals.append({
            'date': prad['date'],
            'name': prad['type'],
            'tamil_name': 'பிரதோஷம்',
            'type': 'pradosham',
            'category': 'monthly',
            'temples': 'All Shiva temples - Evening prayers',
            'tamil_month': prad.get('tamil_month', ''),
            'year': 2025
        })
    
    # Process Ekadashi dates
    for ekad in data['festivals'].get('ekadashi', []):
        all_festivals.append({
            'date': ekad['date'],
            'name': ekad.get('type', 'Ekadashi'),
            'tamil_name': 'ஏகாதசி',
            'type': 'ekadashi',
            'category': 'monthly',
            'temples': 'All Vishnu temples - Fasting day',
            'tamil_month': ekad.get('tamil_month', ''),
            'year': 2025
        })
    
    # Process Pournami dates
    for pourn in data['festivals'].get('pournami', []):
        all_festivals.append({
            'date': pourn['date'],
            'name': 'Pournami (Full Moon)',
            'tamil_name': 'பௌர்ணமி',
            'type': 'pournami',
            'category': 'monthly',
            'temples': 'All temples - Full moon worship',
            'tamil_month': pourn.get('tamil_month', ''),
            'year': 2025
        })
    
    # Process Amavasya dates
    for amav in data['festivals'].get('amavasya', []):
        all_festivals.append({
            'date': amav['date'],
            'name': 'Amavasya (New Moon)',
            'tamil_name': 'அமாவாசை',
            'type': 'amavasya',
            'category': 'monthly',
            'temples': 'Ancestor worship at temples',
            'tamil_month': amav.get('tamil_month', ''),
            'year': 2025
        })
    
    # Insert all festivals
    for fest in all_festivals:
        cursor.execute('''
            INSERT INTO festivals (date, name, tamil_name, type, category, temples, tamil_month, year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fest['date'],
            fest['name'],
            fest['tamil_name'],
            fest['type'],
            fest['category'],
            fest['temples'],
            fest['tamil_month'],
            fest['year']
        ))
    
    conn.commit()
    
    # Verify the import
    cursor.execute("SELECT COUNT(*) FROM festivals")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT type, COUNT(*) FROM festivals GROUP BY type")
    breakdown = cursor.fetchall()
    
    conn.close()
    
    print(f"\n✅ Database updated successfully!")
    print(f"   Total festivals: {total}")
    for festival_type, count in breakdown:
        print(f"   - {festival_type}: {count}")
    
    return total

if __name__ == "__main__":
    update_database_with_festivals()