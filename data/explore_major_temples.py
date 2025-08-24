#!/usr/bin/env python3
"""
Explore Major Temples from Dataset
Identify high-income temples to test detailed data scraping
"""

import json
from pathlib import Path

def get_major_temples():
    """Get list of major temples (income > 10 lakh)"""
    
    print("\n" + "="*60)
    print(" MAJOR TEMPLES ANALYSIS")
    print("="*60)
    
    # Load the full dataset
    with open("raw_data/tn_temples_full.json", "r", encoding="utf-8") as f:
        temples = json.load(f)
    
    # Filter major temples (category 46_iii)
    major_temples = [t for t in temples if t.get('temple_12a_category') == '46_iii']
    
    print(f"\n📊 Found {len(major_temples)} major temples (income > ₹10 lakh)")
    
    # Group by district
    districts = {}
    for temple in major_temples:
        district = temple.get('district', 'Unknown')
        if district not in districts:
            districts[district] = []
        districts[district].append(temple)
    
    print(f"\n📍 District Distribution:")
    for district, temples_list in sorted(districts.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"   {district}: {len(temples_list)} temples")
    
    # Select diverse temples for testing
    test_temples = []
    
    # 1. Add Sankarankovil (we know this one)
    sankarankovil = [t for t in major_temples if t.get('id') == 'TM037875']
    if sankarankovil:
        test_temples.append(sankarankovil[0])
    
    # 2. Add famous temples (search by keywords)
    famous_keywords = [
        'meenakshi', 'parthasarathy', 'kapaleeshwarar', 'ranganathaswamy',
        'murugan', 'mariamman', 'perumal', 'vinayagar', 'kasi viswanathar'
    ]
    
    for keyword in famous_keywords:
        matches = [t for t in major_temples 
                  if keyword in t.get('temple_name', '').lower() 
                  and t not in test_temples]
        if matches:
            test_temples.append(matches[0])
            if len(test_temples) >= 10:
                break
    
    # 3. Add temples from different districts if needed
    for district, temples_list in districts.items():
        if len(test_temples) >= 10:
            break
        for temple in temples_list:
            if temple not in test_temples:
                test_temples.append(temple)
                break
    
    # Display selected temples
    print(f"\n🎯 Selected {len(test_temples)} Major Temples for Testing:")
    print("="*60)
    
    for i, temple in enumerate(test_temples[:10], 1):
        print(f"\n{i}. {temple.get('temple_name')}")
        print(f"   ID: {temple.get('id')}")
        print(f"   District: {temple.get('district')}")
        print(f"   Address: {temple.get('address')}")
        print(f"   Pincode: {temple.get('pincode')}")
    
    # Save test temples
    with open("raw_data/major_temples_test.json", "w", encoding="utf-8") as f:
        json.dump(test_temples[:10], f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved to: raw_data/major_temples_test.json")
    
    # Generate URL patterns to test
    print(f"\n🔗 HR&CE URLs to Test:")
    print("="*60)
    
    for temple in test_temples[:3]:
        temple_id = temple.get('id')
        print(f"\nTemple: {temple.get('temple_name')}")
        print(f"URLs to try:")
        print(f"  1. https://hrce.tn.gov.in/hrcehome/index_temple.php?tid={temple_id}")
        print(f"  2. https://hrce.tn.gov.in/hrcehome/temple_details.php?id={temple_id}")
        print(f"  3. https://hrce.tn.gov.in/temple/{temple_id}")
        print(f"  4. https://hrce.tn.gov.in/hrcehome/temple.php?id={temple_id}")
    
    return test_temples

def analyze_temple_categories():
    """Analyze what types of temples have rich data"""
    
    print(f"\n📊 TEMPLE CATEGORY ANALYSIS")
    print("─"*40)
    
    with open("raw_data/tn_temples_full.json", "r", encoding="utf-8") as f:
        temples = json.load(f)
    
    # Analyze by income category
    categories = {}
    for temple in temples:
        cat = temple.get('temple_12a_category')
        cat_desc = temple.get('temple_12a_category_description')
        if cat not in categories:
            categories[cat] = {
                'count': 0,
                'description': cat_desc,
                'samples': []
            }
        categories[cat]['count'] += 1
        if len(categories[cat]['samples']) < 3:
            categories[cat]['samples'].append({
                'id': temple.get('id'),
                'name': temple.get('temple_name')
            })
    
    print(f"\nIncome Categories with Sample Temples:")
    for cat in ['46_iii', '46_ii', '46_i', '49_i']:
        if cat in categories:
            info = categories[cat]
            print(f"\n{cat}: {info['description']}")
            print(f"  Count: {info['count']} temples")
            print(f"  Samples:")
            for sample in info['samples']:
                print(f"    - {sample['id']}: {sample['name']}")

def main():
    # Get major temples
    test_temples = get_major_temples()
    
    # Analyze categories
    analyze_temple_categories()
    
    print(f"\n" + "="*60)
    print(" NEXT STEPS")
    print("="*60)
    print(f"\n1. Use Selenium to visit these temple URLs")
    print(f"2. Check what information is available:")
    print(f"   - Deity details")
    print(f"   - Festival calendar")
    print(f"   - Pooja timings")
    print(f"   - Temple history")
    print(f"   - Contact information")
    print(f"   - Photos/gallery")
    print(f"3. Extract and structure the data")
    print(f"4. Create enriched temple database")

if __name__ == "__main__":
    main()