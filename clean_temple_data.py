#!/usr/bin/env python3
"""
Clean invalid characters from temple data
"""

import json
import re

def clean_string(text):
    """Remove problematic Unicode characters from text"""
    if not text:
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
    
    cleaned = text
    for char in chars_to_remove:
        cleaned = cleaned.replace(char, '')
    
    # Also clean up any leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned

def clean_temple_data(data):
    """Clean all temple data"""
    
    cleaned_count = {
        'phones': 0,
        'addresses': 0
    }
    
    for temple in data.get('app_temples', []):
        # Clean phone number
        if 'gm_phone' in temple and temple['gm_phone']:
            original = temple['gm_phone']
            cleaned = clean_string(original)
            if original != cleaned:
                temple['gm_phone'] = cleaned
                cleaned_count['phones'] += 1
                print(f"✅ Cleaned phone for {temple['name']}")
                print(f"   Before: {repr(original)}")
                print(f"   After:  {repr(cleaned)}")
        
        # Clean address
        if 'gm_address' in temple and temple['gm_address']:
            original = temple['gm_address']
            cleaned = clean_string(original)
            if original != cleaned:
                temple['gm_address'] = cleaned
                cleaned_count['addresses'] += 1
                print(f"✅ Cleaned address for {temple['name']}")
                print(f"   Before: {repr(original[:50])}")
                print(f"   After:  {repr(cleaned[:50])}")
    
    return data, cleaned_count

def main():
    # Load temple data
    with open('design/mockups/temple_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🧹 Cleaning Temple Data...")
    print("=" * 60)
    
    # Clean the data
    cleaned_data, counts = clean_temple_data(data)
    
    # Save cleaned data
    with open('design/mockups/temple_data_cleaned.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ CLEANING COMPLETE")
    print("=" * 60)
    print(f"Phone numbers cleaned: {counts['phones']}")
    print(f"Addresses cleaned: {counts['addresses']}")
    print("\n📝 Cleaned data saved to temple_data_cleaned.json")
    
    # Now update the original file
    print("\n🔄 Updating original temple_data.json...")
    with open('design/mockups/temple_data.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    print("✅ Original file updated!")

if __name__ == "__main__":
    main()