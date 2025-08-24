#!/usr/bin/env python3
"""
Fix festival data import - Import all 88 festival dates into SQLite
"""

import json
import sqlite3
from datetime import datetime

def import_all_festivals():
    """Import complete festival data into SQLite"""
    
    print("🎊 Fixing Festival Data Import...")
    
    # Load complete festival data
    with open('festivals/universal_festivals_2025.json', 'r') as f:
        festival_data = json.load(f)
    
    # Connect to database
    conn = sqlite3.connect('data/temples.db')
    cursor = conn.cursor()
    
    # Clear existing festivals to avoid duplicates
    cursor.execute("DELETE FROM festivals")
    print("  Cleared existing festival data")
    
    total_imported = 0
    
    # 1. Import major annual festivals
    major_festivals = festival_data.get('major_annual_festivals', [])
    for festival in major_festivals:
        cursor.execute('''
            INSERT INTO festivals (date, festival_name, festival_type, year)
            VALUES (?, ?, ?, ?)
        ''', (
            festival.get('date'),
            festival.get('name'),
            'major_annual',
            2025
        ))
        total_imported += 1
    print(f"  ✓ Imported {len(major_festivals)} major annual festivals")
    
    # 2. Import recurring festivals (pradosham, ekadashi, etc.)
    festivals = festival_data.get('festivals', {})
    
    # Import Pradosham dates
    pradosham_dates = festivals.get('pradosham', [])
    for event in pradosham_dates:
        cursor.execute('''
            INSERT INTO festivals (
                date, festival_name, festival_type, tamil_date, year
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            event.get('date'),
            event.get('type', 'Pradosham'),
            'pradosham',
            event.get('tamil_month', ''),
            2025
        ))
        total_imported += 1
    print(f"  ✓ Imported {len(pradosham_dates)} Pradosham dates")
    
    # Import Ekadashi dates
    ekadashi_dates = festivals.get('ekadashi', [])
    for event in ekadashi_dates:
        cursor.execute('''
            INSERT INTO festivals (
                date, festival_name, festival_type, tamil_date, year
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            event.get('date'),
            event.get('name', 'Ekadashi'),
            'ekadashi',
            event.get('tamil_month', ''),
            2025
        ))
        total_imported += 1
    print(f"  ✓ Imported {len(ekadashi_dates)} Ekadashi dates")
    
    # Import Pournami (Full Moon) dates
    pournami_dates = festivals.get('pournami', [])
    for event in pournami_dates:
        cursor.execute('''
            INSERT INTO festivals (
                date, festival_name, festival_type, tamil_date, year
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            event.get('date'),
            event.get('name', 'Pournami'),
            'pournami',
            event.get('tamil_month', ''),
            2025
        ))
        total_imported += 1
    print(f"  ✓ Imported {len(pournami_dates)} Pournami dates")
    
    # Import Amavasya (New Moon) dates
    amavasya_dates = festivals.get('amavasya', [])
    for event in amavasya_dates:
        cursor.execute('''
            INSERT INTO festivals (
                date, festival_name, festival_type, tamil_date, year
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            event.get('date'),
            event.get('name', 'Amavasya'),
            'amavasya',
            event.get('tamil_month', ''),
            2025
        ))
        total_imported += 1
    print(f"  ✓ Imported {len(amavasya_dates)} Amavasya dates")
    
    # Commit changes
    conn.commit()
    
    # Verify import
    cursor.execute("SELECT COUNT(*) FROM festivals")
    total_in_db = cursor.fetchone()[0]
    
    cursor.execute("SELECT festival_type, COUNT(*) FROM festivals GROUP BY festival_type")
    breakdown = cursor.fetchall()
    
    print(f"\n📊 Import Complete:")
    print(f"  Total festivals in database: {total_in_db}")
    print(f"\n  Breakdown by type:")
    for fest_type, count in breakdown:
        print(f"    {fest_type}: {count}")
    
    conn.close()
    
    return total_imported

def verify_festival_data():
    """Verify and show sample festival data"""
    
    print("\n🔍 Verifying Festival Data...")
    
    conn = sqlite3.connect('data/temples.db')
    cursor = conn.cursor()
    
    # Show sample of each type
    festival_types = ['major_annual', 'pradosham', 'ekadashi', 'pournami', 'amavasya']
    
    for fest_type in festival_types:
        cursor.execute('''
            SELECT date, festival_name 
            FROM festivals 
            WHERE festival_type = ? 
            ORDER BY date 
            LIMIT 3
        ''', (fest_type,))
        
        results = cursor.fetchall()
        if results:
            print(f"\n  Sample {fest_type} dates:")
            for date, name in results:
                print(f"    {date}: {name}")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print(" 🔧 FIXING FESTIVAL DATA IMPORT")
    print("=" * 60)
    
    # Import all festivals
    total = import_all_festivals()
    
    # Verify the import
    verify_festival_data()
    
    print("\n" + "=" * 60)
    print(" ✅ FESTIVAL DATA FIXED!")
    print("=" * 60)
    print(f"\n Successfully imported all {total} festival dates for 2025")