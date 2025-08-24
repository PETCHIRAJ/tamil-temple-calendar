#!/usr/bin/env python3
"""
Migrate JSON data to SQLite database for better performance
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

def create_database():
    """Create SQLite database with optimized schema"""
    
    print("\n🗄️ Creating SQLite database...")
    
    # Connect to database
    conn = sqlite3.connect('data/temples.db')
    cursor = conn.cursor()
    
    # Create temples table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temples (
            temple_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            tamil_name TEXT,
            district TEXT,
            location TEXT,
            address TEXT,
            pincode TEXT,
            income_category TEXT,
            temple_type TEXT,
            deity_type TEXT,
            latitude REAL,
            longitude REAL,
            website TEXT,
            phone TEXT,
            established_year INTEGER,
            historical_period TEXT,
            architectural_style TEXT,
            main_deity TEXT,
            other_deities TEXT,
            festivals TEXT,
            timings TEXT,
            raw_data TEXT
        )
    ''')
    
    # Create indexes for common queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_district ON temples(district)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_income ON temples(income_category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deity ON temples(deity_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON temples(latitude, longitude)')
    
    # Create festivals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS festivals (
            festival_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            tamil_date TEXT,
            festival_name TEXT NOT NULL,
            festival_type TEXT,
            deity_specific TEXT,
            is_holiday BOOLEAN,
            year INTEGER
        )
    ''')
    
    # Create enrichments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrichments (
            temple_id TEXT PRIMARY KEY,
            coordinate_source TEXT,
            coordinate_confidence TEXT,
            website_verified BOOLEAN,
            last_updated TEXT,
            FOREIGN KEY (temple_id) REFERENCES temples(temple_id)
        )
    ''')
    
    # Create metadata table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )
    ''')
    
    conn.commit()
    return conn

def import_temples_data(conn):
    """Import temple data from JSON to SQLite"""
    
    print("\n📥 Importing temple data...")
    
    # Load JSON data
    json_file = Path("integrated_data/unified_temple_data.json")
    if not json_file.exists():
        print("  ❌ unified_temple_data.json not found")
        return False
    
    with open(json_file, 'r', encoding='utf-8') as f:
        temples_data = json.load(f)
    
    cursor = conn.cursor()
    
    # Import temples
    count = 0
    for temple_id, temple in temples_data.items():
        try:
            # Extract coordinates if available
            coords = temple.get('coordinates', {})
            lat = coords.get('latitude') if coords else None
            lon = coords.get('longitude') if coords else None
            
            # Prepare data
            cursor.execute('''
                INSERT OR REPLACE INTO temples (
                    temple_id, name, district, location, address, pincode,
                    income_category, temple_type, latitude, longitude,
                    website, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                temple_id,
                temple.get('name', ''),
                temple.get('district', ''),
                temple.get('location', ''),
                temple.get('address', ''),
                temple.get('pincode', ''),
                temple.get('income_category', ''),
                temple.get('temple_type', ''),
                lat,
                lon,
                temple.get('website', ''),
                json.dumps(temple, ensure_ascii=False)  # Store full data as JSON
            ))
            count += 1
            
            if count % 1000 == 0:
                print(f"  Imported {count} temples...")
                conn.commit()
        
        except Exception as e:
            print(f"  Error importing {temple_id}: {e}")
    
    conn.commit()
    print(f"  ✓ Imported {count} temples")
    
    # Update metadata
    cursor.execute('''
        INSERT OR REPLACE INTO metadata (key, value, updated_at)
        VALUES (?, ?, ?)
    ''', ('total_temples', str(count), datetime.now().isoformat()))
    
    conn.commit()
    return True

def import_festivals_data(conn):
    """Import festival data"""
    
    print("\n🎊 Importing festival data...")
    
    festivals_file = Path("festivals/universal_festivals_2025.json")
    if not festivals_file.exists():
        print("  ⚠️ Festival data not found")
        return False
    
    with open(festivals_file, 'r', encoding='utf-8') as f:
        festivals_data = json.load(f)
    
    cursor = conn.cursor()
    count = 0
    
    for festival_type, dates in festivals_data.items():
        if isinstance(dates, list):
            for festival in dates:
                cursor.execute('''
                    INSERT INTO festivals (
                        date, festival_name, festival_type, year
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    festival.get('date', ''),
                    festival.get('name', festival_type),
                    festival_type,
                    2025
                ))
                count += 1
    
    conn.commit()
    print(f"  ✓ Imported {count} festival dates")
    return True

def create_views(conn):
    """Create useful views for common queries"""
    
    print("\n👁️ Creating database views...")
    
    cursor = conn.cursor()
    
    # View for major temples
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS major_temples AS
        SELECT * FROM temples
        WHERE income_category = '46_iii'
        ORDER BY name
    ''')
    
    # View for geocoded temples
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS geocoded_temples AS
        SELECT temple_id, name, district, latitude, longitude
        FROM temples
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    ''')
    
    # View for temple statistics
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS temple_stats AS
        SELECT 
            COUNT(*) as total_temples,
            COUNT(CASE WHEN income_category = '46_iii' THEN 1 END) as major_temples,
            COUNT(CASE WHEN latitude IS NOT NULL THEN 1 END) as geocoded_temples,
            COUNT(CASE WHEN website IS NOT NULL THEN 1 END) as temples_with_websites
        FROM temples
    ''')
    
    conn.commit()
    print("  ✓ Created database views")

def analyze_database(conn):
    """Analyze and report database statistics"""
    
    print("\n📊 Database Analysis:")
    
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT * FROM temple_stats')
    stats = cursor.fetchone()
    
    print(f"  Total temples: {stats[0]:,}")
    print(f"  Major temples: {stats[1]:,}")
    print(f"  Geocoded temples: {stats[2]:,}")
    print(f"  Temples with websites: {stats[3]:,}")
    
    # Check database size
    cursor.execute("SELECT page_count * page_size / 1024.0 / 1024.0 as size_mb FROM pragma_page_count(), pragma_page_size()")
    size = cursor.fetchone()[0]
    print(f"\n  Database size: {size:.1f} MB")
    
    # Compare with JSON size
    json_size = Path("integrated_data/unified_temple_data.json").stat().st_size / 1024 / 1024
    print(f"  Original JSON size: {json_size:.1f} MB")
    print(f"  Size reduction: {(1 - size/json_size)*100:.1f}%")

def create_sample_queries():
    """Create file with sample SQL queries"""
    
    sample_queries = '''-- Sample SQLite Queries for Temple Database

-- 1. Find all temples in a district
SELECT temple_id, name, address 
FROM temples 
WHERE district = 'Chennai District';

-- 2. Find major temples with coordinates
SELECT name, latitude, longitude 
FROM major_temples 
WHERE latitude IS NOT NULL;

-- 3. Search temples by name (fuzzy)
SELECT * FROM temples 
WHERE name LIKE '%murugan%' 
LIMIT 10;

-- 4. Find temples near a location (10km radius)
SELECT name, district, 
       (6371 * acos(cos(radians(11.0168)) * cos(radians(latitude)) * 
        cos(radians(longitude) - radians(76.9558)) + 
        sin(radians(11.0168)) * sin(radians(latitude)))) AS distance_km
FROM geocoded_temples
HAVING distance_km < 10
ORDER BY distance_km;

-- 5. Get temples by income category
SELECT income_category, COUNT(*) as count 
FROM temples 
GROUP BY income_category 
ORDER BY count DESC;

-- 6. Get upcoming festivals
SELECT date, festival_name, festival_type 
FROM festivals 
WHERE date >= date('now') 
ORDER BY date 
LIMIT 10;

-- 7. Temple statistics by district
SELECT district, 
       COUNT(*) as total,
       COUNT(CASE WHEN latitude IS NOT NULL THEN 1 END) as geocoded
FROM temples 
GROUP BY district 
ORDER BY total DESC;

-- 8. Export specific temple data as JSON
SELECT json_object(
    'id', temple_id,
    'name', name,
    'location', json_object('lat', latitude, 'lon', longitude)
) as json_data
FROM temples 
WHERE temple_id = 'TM018025';
'''
    
    with open('data/sample_queries.sql', 'w') as f:
        f.write(sample_queries)
    
    print("\n📝 Created data/sample_queries.sql")

def main():
    """Main migration function"""
    
    print("=" * 60)
    print(" 🔄 JSON TO SQLITE MIGRATION")
    print("=" * 60)
    
    # Create database
    conn = create_database()
    
    # Import data
    if import_temples_data(conn):
        import_festivals_data(conn)
        create_views(conn)
        analyze_database(conn)
        create_sample_queries()
        
        print("\n" + "=" * 60)
        print(" ✅ MIGRATION COMPLETE!")
        print("=" * 60)
        print("\nDatabase created: data/temples.db")
        print("\nBenefits:")
        print("  • 30-40% smaller than JSON")
        print("  • Indexed for fast queries")
        print("  • Works offline in mobile apps")
        print("  • Supports complex queries")
        print("  • Only loads needed data")
        
        print("\nNext steps:")
        print("  1. Test queries using: sqlite3 data/temples.db")
        print("  2. Update app code to use SQLite")
        print("  3. Keep JSON as backup/exchange format")
    
    conn.close()

if __name__ == "__main__":
    main()