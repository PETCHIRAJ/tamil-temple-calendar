#!/usr/bin/env python3
"""
Discover More Temple Subdomains
Try to find more temple subdomains beyond the initial 3
"""

import requests
import json
import re
from pathlib import Path

def check_subdomain_exists(url):
    """Quick check if subdomain exists"""
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200 and len(resp.text) > 10000:
            # Check if it's a temple page
            if "temple" in resp.text.lower():
                return True
    except:
        pass
    return False

def discover_more_subdomains():
    """Try to discover more temple subdomains"""
    
    print("\n" + "="*60)
    print(" DISCOVERING MORE TEMPLE SUBDOMAINS")
    print("="*60)
    
    # Load major temples
    with open("raw_data/major_temples_test.json", "r", encoding="utf-8") as f:
        temples = json.load(f)
    
    # Known working patterns
    known_subdomains = {
        "TM037875": "sankarankovilsankaranarayanar",
        "TM031962": "maduraimeenakshi",
        "TM000005": "parthasarathy"
    }
    
    # Try common deity names and locations
    common_patterns = [
        # Famous temples
        "kapaleeshwarar", "ekambareswarar", "ranganathar", "nataraja",
        "brihadeeswarar", "murugan", "palani", "thiruchendur",
        "srirangam", "chidambaram", "kanchipuram", "kumbakonam",
        "thiruvannamalai", "rameswaram", "kanyakumari", "velankanni",
        
        # Chennai temples (since many major temples are there)
        "mylapore", "triplicane", "vadapalani", "ashtalakshmi",
        
        # Common deity patterns
        "vinayagar", "amman", "perumal", "shiva", "vishnu",
        "subramaniya", "ayyappan", "mariamman"
    ]
    
    discovered = []
    
    print("\nTrying common temple patterns...")
    for pattern in common_patterns:
        url = f"https://{pattern}.hrce.tn.gov.in/"
        if check_subdomain_exists(url):
            print(f"  ✅ Found: {url}")
            discovered.append({
                "pattern": pattern,
                "url": url
            })
        else:
            print(f"  ✗ {pattern}", end=" ")
    
    print("\n\nTrying temple names from dataset...")
    # Try more temples from our list
    for temple in temples[3:20]:  # Skip first 3 we already have
        temple_name = temple.get('temple_name', '').lower()
        temple_id = temple.get('id', '')
        
        # Clean name for subdomain
        name = temple_name.replace("arulmigu ", "").replace(" temple", "")
        name = re.sub(r'[^a-z0-9]', '', name)
        
        # Try different variations
        variations = [
            name[:20],  # First 20 chars
            name.split("swam")[0] if "swam" in name else None,
            name.split("amman")[0] + "amman" if "amman" in name else None,
        ]
        
        for variant in variations:
            if variant:
                url = f"https://{variant}.hrce.tn.gov.in/"
                if check_subdomain_exists(url):
                    print(f"  ✅ Found: {temple_name[:30]} -> {url}")
                    discovered.append({
                        "temple_id": temple_id,
                        "temple_name": temple.get('temple_name'),
                        "pattern": variant,
                        "url": url
                    })
                    break
    
    # Save discoveries
    if discovered:
        with open("raw_data/discovered_subdomains.json", "w", encoding="utf-8") as f:
            json.dump(discovered, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Discovered {len(discovered)} new subdomains!")
        print(f"   Saved to: raw_data/discovered_subdomains.json")
    else:
        print(f"\n❌ No new subdomains discovered")
    
    return discovered

if __name__ == "__main__":
    discovered = discover_more_subdomains()
    
    print("\n" + "="*60)
    print(" SUMMARY")
    print("="*60)
    
    if discovered:
        print(f"\nDiscovered subdomains:")
        for item in discovered:
            print(f"  - {item.get('temple_name', item['pattern'])}: {item['url']}")
    
    print(f"\nTotal known subdomains: {3 + len(discovered)}")
    print(f"\nNote: Many temples may not have dedicated subdomains")
    print(f"      Only the most famous/high-income temples have them")