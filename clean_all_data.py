#!/usr/bin/env python3
"""
Clean invalid characters from both SQLite database and JSON files
"""

import sqlite3
import json
import re

def clean_string(text):
    """Remove problematic Unicode characters from text"""
    if not text or text == 'N/A' or text == 'NULL':
        return text
    
    # Characters to remove (Private Use Area and other problematic ones)
    chars_to_remove = [
        '\ue0b0',  # Private Use Area character found in phone numbers
        '\ue0c8',  # Private Use Area character found in addresses
        '\u200b',  # Zero-width space
        '\u200c',  # Zero-width non-joiner
        '\u200d',  # Zero-width joiner
        '\ufeff',  # Zero-width no-break space
    ]
    
    cleaned = str(text)
    for char in chars_to_remove:
        cleaned = cleaned.replace(char, '')
    
    # Also clean up any leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned

def clean_database():
    """Clean the SQLite database"""
    print("\n🗄️ Cleaning SQLite Database...")
    print("=" * 60)
    
    conn = sqlite3.connect('project-data/database/temple_app_mvp.db')
    cursor = conn.cursor()
    
    # Clean app_temples table
    cursor.execute("SELECT id, name, gm_phone, gm_address FROM app_temples")
    temples = cursor.fetchall()
    
    phone_cleaned = 0
    address_cleaned = 0
    
    for temple_id, name, phone, address in temples:
        updates = []
        params = []
        
        # Check and clean phone
        if phone:
            cleaned_phone = clean_string(phone)
            if cleaned_phone != phone:
                updates.append("gm_phone = ?")
                params.append(cleaned_phone)
                phone_cleaned += 1
                print(f"✅ Cleaned phone for {name}")
                print(f"   Before: {repr(phone)}")
                print(f"   After:  {repr(cleaned_phone)}")
        
        # Check and clean address
        if address:
            cleaned_address = clean_string(address)
            if cleaned_address != address:
                updates.append("gm_address = ?")
                params.append(cleaned_address)
                address_cleaned += 1
                print(f"✅ Cleaned address for {name}")
                print(f"   Before: {repr(address[:50])}")
                print(f"   After:  {repr(cleaned_address[:50])}")
        
        # Update if needed
        if updates:
            params.append(temple_id)
            query = f"UPDATE app_temples SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
    
    # Also clean temple_directory table
    cursor.execute("SELECT id, name, gm_phone, gm_address FROM temple_directory WHERE gm_phone IS NOT NULL OR gm_address IS NOT NULL")
    directory_temples = cursor.fetchall()
    
    for temple_id, name, phone, address in directory_temples:
        updates = []
        params = []
        
        if phone:
            cleaned_phone = clean_string(phone)
            if cleaned_phone != phone:
                updates.append("gm_phone = ?")
                params.append(cleaned_phone)
        
        if address:
            cleaned_address = clean_string(address)
            if cleaned_address != address:
                updates.append("gm_address = ?")
                params.append(cleaned_address)
        
        if updates:
            params.append(temple_id)
            query = f"UPDATE temple_directory SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
    
    conn.commit()
    conn.close()
    
    print(f"\nDatabase cleaning complete:")
    print(f"  Phone numbers cleaned: {phone_cleaned}")
    print(f"  Addresses cleaned: {address_cleaned}")
    
    return phone_cleaned, address_cleaned

def verify_json_clean():
    """Verify the JSON file is clean"""
    print("\n📄 Verifying JSON Data...")
    print("=" * 60)
    
    with open('design/mockups/temple_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    issues_found = 0
    
    for temple in data.get('app_temples', []):
        phone = temple.get('gm_phone', '')
        address = temple.get('gm_address', '')
        
        # Check for problematic characters
        if phone and ('\ue0b0' in phone or '\ue0c8' in phone):
            print(f"❌ Still has issues in phone: {temple['name']}")
            issues_found += 1
        
        if address and ('\ue0b0' in address or '\ue0c8' in address):
            print(f"❌ Still has issues in address: {temple['name']}")
            issues_found += 1
    
    if issues_found == 0:
        print("✅ JSON data is clean - no problematic characters found!")
    else:
        print(f"⚠️ Found {issues_found} remaining issues in JSON")
    
    return issues_found == 0

def main():
    print("🧹 Complete Data Cleanup Process")
    print("=" * 60)
    
    # Clean database
    db_phones, db_addresses = clean_database()
    
    # Verify JSON is clean
    json_clean = verify_json_clean()
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ CLEANUP COMPLETE")
    print("=" * 60)
    print(f"Database:")
    print(f"  - Phone numbers cleaned: {db_phones}")
    print(f"  - Addresses cleaned: {db_addresses}")
    print(f"\nJSON:")
    print(f"  - Status: {'✅ Clean' if json_clean else '❌ Has issues'}")
    print("\n✅ All data sources are now synchronized and clean!")

if __name__ == "__main__":
    main()