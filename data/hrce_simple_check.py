#!/usr/bin/env python3
"""
Simple check of what HR&CE website returns for major temples
"""

import requests
import json
from bs4 import BeautifulSoup
from pathlib import Path

def check_temple_urls():
    """Check what HR&CE returns for major temple URLs"""
    
    print("\n" + "="*60)
    print(" HR&CE WEBSITE CONTENT CHECK")
    print("="*60)
    
    # Load major temples
    with open("raw_data/major_temples_test.json", "r", encoding="utf-8") as f:
        temples = json.load(f)
    
    # Setup session
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    
    # Test first 3 temples
    for temple in temples[:3]:
        temple_id = temple.get("id")
        temple_name = temple.get("temple_name")
        
        print(f"\n{'='*50}")
        print(f"Temple: {temple_name}")
        print(f"ID: {temple_id}")
        print('='*50)
        
        # Try different URL patterns
        urls = [
            f"https://hrce.tn.gov.in/hrcehome/index_temple.php?tid={temple_id}",
            f"https://sankarankovilsankaranarayanar.hrce.tn.gov.in/"  # Some temples have subdomains
        ]
        
        for url in urls:
            print(f"\nTrying: {url}")
            
            try:
                resp = session.get(url, timeout=5, allow_redirects=True)
                print(f"  Status: {resp.status_code}")
                
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, "html.parser")
                    
                    # Check content length
                    print(f"  Content length: {len(resp.text)} chars")
                    
                    # Check for error messages
                    text = soup.get_text().strip()
                    
                    if "date mismatched" in text.lower():
                        print("  ❌ Date mismatch error")
                    elif "no matching records" in text.lower():
                        print("  ❌ No matching records")
                    elif len(text) < 100:
                        print("  ❌ Empty or minimal content")
                    else:
                        print("  ✅ Has content!")
                        
                        # Look for useful elements
                        print("\n  Content Analysis:")
                        
                        # Tables
                        tables = soup.find_all("table")
                        print(f"    Tables: {len(tables)}")
                        
                        # Headers
                        headers = soup.find_all(["h1", "h2", "h3"])
                        if headers:
                            print(f"    Headers: {len(headers)}")
                            for h in headers[:3]:
                                print(f"      - {h.get_text().strip()[:50]}")
                        
                        # Images
                        images = soup.find_all("img")
                        print(f"    Images: {len(images)}")
                        
                        # Links
                        links = soup.find_all("a")
                        print(f"    Links: {len(links)}")
                        
                        # Sample text
                        print(f"\n    Sample text (first 300 chars):")
                        print(f"    {text[:300]}...")
                        
                        # Save for analysis
                        Path("raw_data/url_tests").mkdir(exist_ok=True)
                        with open(f"raw_data/url_tests/{temple_id}.html", "w", encoding="utf-8") as f:
                            f.write(soup.prettify())
                        print(f"\n    Saved to: raw_data/url_tests/{temple_id}.html")
                
            except requests.exceptions.Timeout:
                print("  ❌ Timeout")
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    # Check if there are temple-specific subdomains
    print(f"\n{'='*60}")
    print(" CHECKING FOR TEMPLE SUBDOMAINS")
    print('='*60)
    
    # Try Sankarankovil subdomain
    subdomain_tests = [
        "https://sankarankovilsankaranarayanar.hrce.tn.gov.in/",
        "https://maduraimeenakshi.hrce.tn.gov.in/",
        "https://parthasarathy.hrce.tn.gov.in/"
    ]
    
    for url in subdomain_tests:
        print(f"\nTrying: {url}")
        try:
            resp = session.get(url, timeout=5)
            if resp.status_code == 200:
                print(f"  ✅ Subdomain exists! Status: {resp.status_code}")
                print(f"  Content length: {len(resp.text)} chars")
                
                soup = BeautifulSoup(resp.content, "html.parser")
                title = soup.find("title")
                if title:
                    print(f"  Title: {title.get_text().strip()}")
            else:
                print(f"  ❌ Status: {resp.status_code}")
        except:
            print(f"  ❌ Subdomain not accessible")
    
    print(f"\n{'='*60}")
    print(" SUMMARY")
    print('='*60)
    print("\nFindings:")
    print("1. Direct temple URLs may have date synchronization issues")
    print("2. Some major temples might have dedicated subdomains")
    print("3. Content may be JavaScript-rendered requiring Selenium")
    print("4. Check raw_data/url_tests/ for any successful HTML captures")

if __name__ == "__main__":
    check_temple_urls()