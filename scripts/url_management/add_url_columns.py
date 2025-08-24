#!/usr/bin/env python3
"""
Add separate URL columns for Wikipedia, HR&CE, and Official websites
Option 1: Simple separate columns approach
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

def add_url_columns():
    """Add three separate URL columns to the database"""
    
    print("\n🔄 Adding URL Columns to Database")
    print("=" * 60)
    
    conn = sqlite3.connect('database/temples.db')
    cursor = conn.cursor()
    
    # Check which columns already exist
    cursor.execute("""
        SELECT name FROM pragma_table_info('temples') 
        WHERE name IN ('wikipedia_url', 'hrce_url', 'official_url')
    """)
    existing_columns = [row[0] for row in cursor.fetchall()]
    
    # Add columns that don't exist
    columns_to_add = [
        ('wikipedia_url', 'Wikipedia URL'),
        ('hrce_url', 'HR&CE Subdomain URL'),
        ('official_url', 'Official Website URL')
    ]
    
    for column_name, description in columns_to_add:
        if column_name not in existing_columns:
            print(f"\n1. Adding {column_name} column...")
            cursor.execute(f"ALTER TABLE temples ADD COLUMN {column_name} TEXT")
            print(f"   ✓ Added {description} column")
        else:
            print(f"   ⚠️  {column_name} already exists")
    
    # Create indexes for faster queries
    print("\n2. Creating indexes for faster lookups...")
    
    indexes = [
        ('idx_wikipedia_url', 'wikipedia_url'),
        ('idx_hrce_url', 'hrce_url'),
        ('idx_official_url', 'official_url')
    ]
    
    for index_name, column_name in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON temples({column_name})")
            print(f"   ✓ Created index on {column_name}")
        except sqlite3.OperationalError:
            print(f"   ⚠️  Index {index_name} already exists")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database structure updated!")
    return True

def import_verified_urls():
    """Import the 5 verified URLs we have"""
    
    print("\n📥 Importing Verified URLs")
    print("=" * 60)
    
    conn = sqlite3.connect('database/temples.db')
    cursor = conn.cursor()
    
    # Load verified websites
    verified_file = Path('json_data/enrichments/temple_websites_verified.json')
    if not verified_file.exists():
        print("❌ No verified websites file found")
        return
    
    with open(verified_file, 'r') as f:
        data = json.load(f)
    
    verified_websites = data['verified_websites']
    
    # Clear existing website column data first (if migrating)
    print("\n1. Migrating verified URLs to new columns...")
    
    hrce_count = 0
    official_count = 0
    
    for temple_id, info in verified_websites.items():
        url = info['url']
        
        if 'hrce.tn.gov.in' in url:
            # It's an HR&CE subdomain
            cursor.execute("""
                UPDATE temples 
                SET hrce_url = ? 
                WHERE temple_id = ?
            """, (url, temple_id))
            hrce_count += 1
            print(f"   ✓ HR&CE: {temple_id} -> {url}")
        else:
            # It's an official website
            cursor.execute("""
                UPDATE temples 
                SET official_url = ? 
                WHERE temple_id = ?
            """, (url, temple_id))
            official_count += 1
            print(f"   ✓ Official: {temple_id} -> {url}")
    
    conn.commit()
    
    print(f"\n   Imported: {hrce_count} HR&CE URLs, {official_count} Official URLs")
    
    conn.close()
    return hrce_count + official_count

def prepare_wikipedia_import():
    """Prepare script to import Wikipedia URLs after validation"""
    
    print("\n📝 Creating Wikipedia Import Script")
    print("=" * 60)
    
    import_script = """#!/usr/bin/env python3
'''
Import validated Wikipedia URLs into the database
Run this after validating wikipedia_temple_validation.txt
'''

import json
import sqlite3
from pathlib import Path

def import_wikipedia_urls(validated_ids_file='validated_wikipedia_ids.txt'):
    '''Import Wikipedia URLs for validated temple IDs'''
    
    print("\\n📥 Importing Wikipedia URLs")
    print("=" * 60)
    
    # Load the mapping data
    mapping_file = Path('json_data/enrichments/wikipedia_temple_mapping.json')
    with open(mapping_file, 'r') as f:
        data = json.load(f)
    
    # Create lookup dictionary
    wiki_lookup = {m['temple_id']: m['wikipedia_url'] 
                   for m in data['matched_temples']}
    
    # Read validated IDs (one per line)
    validated_file = Path(validated_ids_file)
    if not validated_file.exists():
        print(f"❌ Please create {validated_ids_file} with validated temple IDs (one per line)")
        return
    
    with open(validated_file, 'r') as f:
        validated_ids = [line.strip() for line in f if line.strip()]
    
    # Update database
    conn = sqlite3.connect('database/temples.db')
    cursor = conn.cursor()
    
    imported = 0
    for temple_id in validated_ids:
        if temple_id in wiki_lookup:
            url = wiki_lookup[temple_id]
            cursor.execute('''
                UPDATE temples 
                SET wikipedia_url = ? 
                WHERE temple_id = ?
            ''', (url, temple_id))
            imported += 1
            print(f"   ✓ {temple_id}: {url}")
    
    conn.commit()
    conn.close()
    
    print(f"\\n✅ Imported {imported} Wikipedia URLs")
    return imported

if __name__ == "__main__":
    # Instructions
    print("\\n📋 INSTRUCTIONS:")
    print("1. Review wikipedia_temple_validation.txt")
    print("2. Create validated_wikipedia_ids.txt with approved temple IDs (one per line)")
    print("3. Run this script to import the URLs")
    print()
    
    response = input("Have you created validated_wikipedia_ids.txt? (y/n): ")
    if response.lower() == 'y':
        import_wikipedia_urls()
    else:
        print("\\nPlease create the file first with validated temple IDs")
"""
    
    with open('scripts/import_wikipedia_urls.py', 'w') as f:
        f.write(import_script)
    
    print("✓ Created scripts/import_wikipedia_urls.py")
    print("  Run this after you validate the Wikipedia matches")

def show_query_examples():
    """Show how to query the new structure"""
    
    print("\n📊 Query Examples for New Structure")
    print("=" * 60)
    
    print("""
    -- Find temples with Wikipedia pages
    SELECT temple_id, name, wikipedia_url 
    FROM temples 
    WHERE wikipedia_url IS NOT NULL;
    
    -- Find temples with HR&CE websites
    SELECT temple_id, name, hrce_url 
    FROM temples 
    WHERE hrce_url IS NOT NULL;
    
    -- Get any available URL (prioritized)
    SELECT temple_id, name,
           COALESCE(hrce_url, official_url, wikipedia_url) as primary_url,
           CASE 
               WHEN hrce_url IS NOT NULL THEN 'hrce'
               WHEN official_url IS NOT NULL THEN 'official'
               WHEN wikipedia_url IS NOT NULL THEN 'wikipedia'
           END as url_type
    FROM temples
    WHERE hrce_url IS NOT NULL 
       OR official_url IS NOT NULL 
       OR wikipedia_url IS NOT NULL;
    
    -- Count temples by URL availability
    SELECT 
        SUM(CASE WHEN wikipedia_url IS NOT NULL THEN 1 ELSE 0 END) as with_wikipedia,
        SUM(CASE WHEN hrce_url IS NOT NULL THEN 1 ELSE 0 END) as with_hrce,
        SUM(CASE WHEN official_url IS NOT NULL THEN 1 ELSE 0 END) as with_official,
        COUNT(*) as total_temples
    FROM temples;
    """)

def main():
    """Execute the migration"""
    
    print("\n🚀 URL Storage Migration - Option 1: Separate Columns")
    print("=" * 60)
    
    # Step 1: Add columns
    if add_url_columns():
        
        # Step 2: Import verified URLs
        imported = import_verified_urls()
        
        # Step 3: Prepare Wikipedia import
        prepare_wikipedia_import()
        
        # Step 4: Show examples
        show_query_examples()
        
        print("\n✅ Migration Complete!")
        print(f"   - Added 3 URL columns with indexes")
        print(f"   - Imported {imported} verified URLs")
        print(f"   - Created import script for Wikipedia URLs")
        print("\n📋 Next Steps:")
        print("   1. Complete validation of wikipedia_temple_validation.txt")
        print("   2. Create validated_wikipedia_ids.txt with approved IDs")
        print("   3. Run scripts/import_wikipedia_urls.py")

if __name__ == "__main__":
    main()