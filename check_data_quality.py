#!/usr/bin/env python3
"""
Check temple data for invalid characters in phone numbers and addresses
"""

import json
import re

def check_invalid_characters(data):
    """Check for invalid/special characters in temple data"""
    
    issues = {
        'phone_issues': [],
        'address_issues': [],
        'special_chars_found': set()
    }
    
    # Pattern for detecting non-standard characters
    # Allow: letters, numbers, spaces, common punctuation, Tamil characters
    valid_pattern = re.compile(r'^[a-zA-Z0-9\s\-\.,\(\)\+\/\#&\':;இஈஉஊஎஏஐஒஓஔகஙசஞடணதநபமயரலவழளறனஜஷஸஹாிீுூெேைொோௌ்ஃ]+$')
    
    # Check phone numbers - should only have numbers, spaces, +, -, ()
    phone_pattern = re.compile(r'^[\d\s\+\-\(\)]+$')
    
    for temple in data.get('app_temples', []):
        temple_id = temple.get('id', 'unknown')
        name = temple.get('name', 'unknown')
        
        # Check phone number
        phone = temple.get('gm_phone', '')
        if phone and phone != 'N/A':
            # Check for invalid characters
            if not phone_pattern.match(phone):
                # Find the invalid characters
                invalid_chars = set()
                for char in phone:
                    if not phone_pattern.match(char) and char not in ' ':
                        invalid_chars.add(char)
                        issues['special_chars_found'].add(f"'{char}' (ord: {ord(char)})")
                
                issues['phone_issues'].append({
                    'temple_id': temple_id,
                    'temple_name': name,
                    'phone': phone,
                    'phone_repr': repr(phone),  # Show escaped characters
                    'invalid_chars': list(invalid_chars),
                    'char_codes': [ord(c) for c in invalid_chars]
                })
        
        # Check address
        address = temple.get('gm_address', '')
        if address and address != 'N/A':
            # Look for common problematic characters
            problematic_chars = [
                '\u200b',  # Zero-width space
                '\u200c',  # Zero-width non-joiner
                '\u200d',  # Zero-width joiner
                '\xa0',    # Non-breaking space
                '\u2028',  # Line separator
                '\u2029',  # Paragraph separator
                '\ufeff',  # Zero-width no-break space
            ]
            
            found_problems = []
            for prob_char in problematic_chars:
                if prob_char in address:
                    found_problems.append(f"U+{ord(prob_char):04X}")
                    issues['special_chars_found'].add(f"U+{ord(prob_char):04X} (invisible)")
            
            # Also check for other non-ASCII characters that might be problematic
            non_standard = []
            for char in address:
                if ord(char) > 127 and not any(c in char for c in 'இஈஉஊஎஏஐஒஓஔகஙசஞடணதநபமயரலவழளறனஜஷஸஹாிீுூெேைொோௌ்ஃ'):
                    if ord(char) not in [8211, 8217, 8220, 8221]:  # Allow em-dash and smart quotes
                        non_standard.append(char)
            
            if found_problems or non_standard:
                issues['address_issues'].append({
                    'temple_id': temple_id,
                    'temple_name': name,
                    'address': address[:100] + ('...' if len(address) > 100 else ''),
                    'address_repr': repr(address[:100]),
                    'problematic_chars': found_problems,
                    'non_standard_chars': list(set(non_standard))
                })
    
    return issues

def main():
    # Load temple data
    with open('design/mockups/temple_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🔍 Checking Temple Data Quality...")
    print("=" * 60)
    
    issues = check_invalid_characters(data)
    
    # Report phone issues
    print(f"\n📞 Phone Number Issues: {len(issues['phone_issues'])} temples")
    print("-" * 60)
    for issue in issues['phone_issues'][:10]:  # Show first 10
        print(f"\n Temple: {issue['temple_name']}")
        print(f"   ID: {issue['temple_id']}")
        print(f"   Phone: {issue['phone']}")
        print(f"   Repr: {issue['phone_repr']}")
        print(f"   Invalid chars: {issue['invalid_chars']}")
        print(f"   Char codes: {issue['char_codes']}")
    
    if len(issues['phone_issues']) > 10:
        print(f"\n   ... and {len(issues['phone_issues']) - 10} more temples with phone issues")
    
    # Report address issues
    print(f"\n📍 Address Issues: {len(issues['address_issues'])} temples")
    print("-" * 60)
    for issue in issues['address_issues'][:10]:  # Show first 10
        print(f"\n Temple: {issue['temple_name']}")
        print(f"   ID: {issue['temple_id']}")
        print(f"   Address snippet: {issue['address']}")
        print(f"   Repr: {issue['address_repr']}")
        if issue['problematic_chars']:
            print(f"   Invisible chars: {issue['problematic_chars']}")
        if issue['non_standard_chars']:
            print(f"   Non-standard: {issue['non_standard_chars']}")
    
    if len(issues['address_issues']) > 10:
        print(f"\n   ... and {len(issues['address_issues']) - 10} more temples with address issues")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total temples checked: {len(data.get('app_temples', []))}")
    print(f"Temples with phone issues: {len(issues['phone_issues'])}")
    print(f"Temples with address issues: {len(issues['address_issues'])}")
    print(f"\nUnique problematic characters found:")
    for char in sorted(issues['special_chars_found']):
        print(f"  - {char}")
    
    # Save detailed report
    with open('data_quality_report.json', 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 Detailed report saved to data_quality_report.json")
    
    return issues

if __name__ == "__main__":
    main()