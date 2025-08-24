#!/usr/bin/env python3
"""
Import validated Wikipedia URLs from the clean CSV file
"""

import csv
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def import_validated_wikipedia_urls():
    """Import Wikipedia URLs from the validated CSV"""
    
    print("\n📥 Importing Validated Wikipedia URLs")
    print("=" * 60)
    
    # Path to the validated CSV
    csv_file = Path('/Users/petchirajmanoharan/Downloads/clean_validated_temples.csv')
    
    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        return 0
    
    # Connect to database
    conn = sqlite3.connect('database/temples.db')
    cursor = conn.cursor()
    
    # Read CSV and import
    imported_count = 0
    skipped_count = 0
    duplicates = {}
    
    print("\n1. Reading validated CSV file...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        temples_to_import = list(reader)
    
    print(f"   Found {len(temples_to_import)} validated entries")
    
    print("\n2. Importing Wikipedia URLs...")
    
    for row in temples_to_import:
        temple_id = row['temple_id']
        temple_name = row['temple_name']
        wikipedia_url = row['wikipedia_url']
        match_score = float(row['match_score'])
        validation_status = row['validation_status']
        
        # Check if this temple already has a Wikipedia URL
        cursor.execute("""
            SELECT wikipedia_url 
            FROM temples 
            WHERE temple_id = ?
        """, (temple_id,))
        
        existing = cursor.fetchone()
        
        if temple_id in duplicates:
            # This temple ID appeared before - it's a duplicate match
            duplicates[temple_id].append({
                'url': wikipedia_url,
                'score': match_score
            })
            print(f"   ⚠️  Duplicate: {temple_id} - {wikipedia_url[:50]}...")
            skipped_count += 1
            continue
        
        if existing and existing[0]:
            print(f"   ⚠️  Already has URL: {temple_id} - {temple_name[:30]}")
            skipped_count += 1
            continue
        
        # Update the database
        cursor.execute("""
            UPDATE temples 
            SET wikipedia_url = ? 
            WHERE temple_id = ?
        """, (wikipedia_url, temple_id))
        
        # Track if we see this ID again
        duplicates[temple_id] = [{
            'url': wikipedia_url,
            'score': match_score
        }]
        
        imported_count += 1
        
        # Show progress with validation status
        status_indicator = "✓" if "VALID - Exact" in validation_status else "✓"
        print(f"   {status_indicator} {temple_id}: {temple_name[:30]}... -> {wikipedia_url[:50]}...")
    
    # Commit changes
    conn.commit()
    
    print(f"\n   Imported: {imported_count} URLs")
    print(f"   Skipped: {skipped_count} (duplicates or existing)")
    
    # Report any temples with multiple Wikipedia matches
    if any(len(urls) > 1 for urls in duplicates.values()):
        print("\n3. Temples with multiple Wikipedia matches:")
        for temple_id, urls in duplicates.items():
            if len(urls) > 1:
                print(f"   {temple_id}:")
                for url_info in urls:
                    print(f"      - {url_info['url']} (score: {url_info['score']})")
    
    conn.close()
    
    return imported_count

def generate_statistics():
    """Generate statistics about URL availability"""
    
    print("\n📊 URL Availability Statistics")
    print("=" * 60)
    
    conn = sqlite3.connect('database/temples.db')
    cursor = conn.cursor()
    
    # Get counts
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN wikipedia_url IS NOT NULL THEN 1 ELSE 0 END) as with_wikipedia,
            SUM(CASE WHEN hrce_url IS NOT NULL THEN 1 ELSE 0 END) as with_hrce,
            SUM(CASE WHEN official_url IS NOT NULL THEN 1 ELSE 0 END) as with_official,
            SUM(CASE WHEN wikipedia_url IS NOT NULL 
                     OR hrce_url IS NOT NULL 
                     OR official_url IS NOT NULL THEN 1 ELSE 0 END) as with_any_url
        FROM temples
    """)
    
    stats = cursor.fetchone()
    
    print(f"\nTotal temples in database: {stats[0]:,}")
    print(f"Temples with Wikipedia: {stats[1]} ({stats[1]*100/stats[0]:.1f}%)")
    print(f"Temples with HR&CE URL: {stats[2]} ({stats[2]*100/stats[0]:.1f}%)")
    print(f"Temples with Official URL: {stats[3]} ({stats[3]*100/stats[0]:.1f}%)")
    print(f"Temples with ANY URL: {stats[4]} ({stats[4]*100/stats[0]:.1f}%)")
    
    # Get distribution by district for temples with URLs
    print("\n📍 Wikipedia URLs by District:")
    cursor.execute("""
        SELECT 
            district,
            COUNT(*) as with_wikipedia
        FROM temples
        WHERE wikipedia_url IS NOT NULL
        GROUP BY district
        ORDER BY with_wikipedia DESC
        LIMIT 10
    """)
    
    for district, count in cursor.fetchall():
        print(f"   {district}: {count}")
    
    conn.close()

def create_url_report():
    """Create a report of all temples with any URL"""
    
    print("\n📝 Creating Combined URL Report")
    print("=" * 60)
    
    conn = sqlite3.connect('database/temples.db')
    cursor = conn.cursor()
    
    # Get all temples with any URL
    cursor.execute("""
        SELECT 
            temple_id,
            name,
            district,
            wikipedia_url,
            hrce_url,
            official_url
        FROM temples
        WHERE wikipedia_url IS NOT NULL 
           OR hrce_url IS NOT NULL 
           OR official_url IS NOT NULL
        ORDER BY 
            CASE 
                WHEN wikipedia_url IS NOT NULL AND hrce_url IS NOT NULL THEN 1
                WHEN wikipedia_url IS NOT NULL THEN 2
                WHEN hrce_url IS NOT NULL THEN 3
                ELSE 4
            END,
            name
    """)
    
    temples_with_urls = cursor.fetchall()
    
    # Create report
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_temples_with_urls': len(temples_with_urls)
        },
        'temples': []
    }
    
    for temple in temples_with_urls:
        temple_data = {
            'temple_id': temple[0],
            'name': temple[1],
            'district': temple[2],
            'urls': {}
        }
        
        if temple[3]:
            temple_data['urls']['wikipedia'] = temple[3]
        if temple[4]:
            temple_data['urls']['hrce'] = temple[4]
        if temple[5]:
            temple_data['urls']['official'] = temple[5]
        
        report['temples'].append(temple_data)
    
    # Save report
    report_file = Path('json_data/enrichments/temples_with_urls_final.json')
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved report to: {report_file}")
    print(f"  Total temples with URLs: {len(temples_with_urls)}")
    
    # Show summary of URL combinations
    wikipedia_only = sum(1 for t in temples_with_urls if t[3] and not t[4] and not t[5])
    hrce_only = sum(1 for t in temples_with_urls if not t[3] and t[4] and not t[5])
    official_only = sum(1 for t in temples_with_urls if not t[3] and not t[4] and t[5])
    multiple_urls = sum(1 for t in temples_with_urls if sum([bool(t[3]), bool(t[4]), bool(t[5])]) > 1)
    
    print(f"\n  URL Combinations:")
    print(f"  - Wikipedia only: {wikipedia_only}")
    print(f"  - HR&CE only: {hrce_only}")
    print(f"  - Official only: {official_only}")
    print(f"  - Multiple URLs: {multiple_urls}")
    
    conn.close()
    
    return len(temples_with_urls)

def main():
    """Main execution"""
    
    print("\n🚀 Wikipedia URL Import from Validated CSV")
    print("=" * 60)
    
    # Import URLs
    imported = import_validated_wikipedia_urls()
    
    if imported > 0:
        print(f"\n✅ Successfully imported {imported} Wikipedia URLs")
        
        # Generate statistics
        generate_statistics()
        
        # Create combined report
        total_with_urls = create_url_report()
        
        print("\n" + "=" * 60)
        print("✅ IMPORT COMPLETE!")
        print("=" * 60)
        print(f"Wikipedia URLs imported: {imported}")
        print(f"Total temples with any URL: {total_with_urls}")
    else:
        print("\n⚠️ No URLs were imported")

if __name__ == "__main__":
    main()