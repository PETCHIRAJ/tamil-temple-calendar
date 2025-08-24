"""
Tamil Nadu HR&CE Temple Data Scraper
-------------------------------------
Fetches temple data for all 38 districts from HR&CE website,
and includes a validation function to fetch details for one temple.

Requirements:
- Python 3.7+
- requests
- beautifulsoup4
- pandas

Usage:
1. Install dependencies: pip install requests beautifulsoup4 pandas
2. Run: python scrape_hrce_temples.py
"""

import requests
import time
import json
from bs4 import BeautifulSoup
from pathlib import Path

# List of all 38 districts in Tamil Nadu as per HR&CE portal
DISTRICTS = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
    "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram",
    "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
    "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
    "Ramanathapuram", "Ranipet", "Salem", "Sivagangai", "Tenkasi",
    "Thanjavur", "Theni", "Thiruchirappalli", "Thirupathur", "Thiruvarur",
    "Thoothukudi", "Tirunelveli", "Tiruppur", "Tiruvallur",
    "Tiruvannamalai", "Vellore", "Viluppuram", "Virudhunagar"
]

BASE_URL = "https://hrce.tn.gov.in/hrcehome/temple_list.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TempleScraper/1.0; +https://example.com)"
}

def scrape_district_temples(district_name, delay=2):
    """
    Scrape temple list for a given district.
    Returns a list of dicts with keys: sno, temple_id, name, officer, district.
    """
    temples = []
    page = 1
    max_pages = 5  # Limit for testing

    while page <= max_pages:
        print(f"    Fetching page {page}...")
        time.sleep(delay)
        params = {
            "district": district_name,
            "page": page
        }
        
        try:
            resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")
            
            # Debug: Save first page for analysis
            if page == 1:
                Path("raw_data").mkdir(exist_ok=True)
                with open(f"raw_data/{district_name}_page1.html", "w", encoding="utf-8") as f:
                    f.write(str(soup.prettify()))
            
            # Try different table selection methods
            tables = soup.find_all("table")
            print(f"    Found {len(tables)} tables")
            
            if not tables:
                print(f"    No tables found on page {page}")
                break
            
            # Check each table for temple data
            found_data = False
            for table in tables:
                rows = table.find_all("tr")
                if len(rows) > 1:  # Has data rows
                    for row in rows[1:]:  # Skip header
                        cols = row.find_all("td")
                        if len(cols) >= 3:  # At least 3 columns
                            temple_data = {
                                "sno": cols[0].get_text(strip=True) if len(cols) > 0 else "",
                                "temple_id": cols[1].get_text(strip=True) if len(cols) > 1 else "",
                                "name": cols[2].get_text(strip=True) if len(cols) > 2 else "",
                                "officer": cols[3].get_text(strip=True) if len(cols) > 3 else "",
                                "district": district_name
                            }
                            
                            # Only add if we have meaningful data
                            if temple_data["name"] and temple_data["name"] != "No matching records found":
                                temples.append(temple_data)
                                found_data = True
            
            if not found_data:
                print(f"    No temple data found on page {page}")
                break
                
        except Exception as e:
            print(f"    Error on page {page}: {e}")
            break
            
        page += 1

    return temples

def validate_single_temple(temple_id, delay=1):
    """
    Validate fetching details for one temple by its ID.
    Returns the HTML title of the detail page to confirm access.
    """
    detail_url = f"https://hrce.tn.gov.in/hrcehome/index_temple.php?tid={temple_id}"
    print(f"  Validating temple: {detail_url}")
    time.sleep(delay)
    
    try:
        resp = requests.get(detail_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        
        # Save for analysis
        Path("raw_data").mkdir(exist_ok=True)
        with open(f"raw_data/temple_{temple_id}.html", "w", encoding="utf-8") as f:
            f.write(str(soup.prettify()))
        
        # Extract page title or heading as validation
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "No title found"
        
        # Also look for temple name in page
        temple_name = None
        h1_tags = soup.find_all("h1")
        for h1 in h1_tags:
            text = h1.get_text(strip=True)
            if text and "temple" in text.lower():
                temple_name = text
                break
        
        return {
            "title": title,
            "temple_name": temple_name,
            "url": detail_url
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "url": detail_url
        }

def main():
    print("="*60)
    print(" HR&CE TEMPLE SCRAPER - VALIDATION TEST")
    print("="*60)
    
    # Test validation for one temple (example: TM000001)
    print("\n1. Validating single temple fetch...")
    try:
        result = validate_single_temple("TM000001")
        print(f"  Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"  Validation failed: {e}")
    
    # Test with another temple ID format
    print("\n2. Testing alternative temple ID...")
    try:
        result = validate_single_temple("TM037875")  # Sankarankovil
        print(f"  Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"  Validation failed: {e}")
    
    # Test scraping for smallest district first
    print("\n3. Testing district scraping (Nilgiris - smallest)...")
    try:
        nilgiris_temples = scrape_district_temples("Nilgiris", delay=1)
        print(f"  Found {len(nilgiris_temples)} temples in Nilgiris")
        
        if nilgiris_temples:
            # Save first 10 temples as sample
            sample = nilgiris_temples[:10]
            Path("raw_data").mkdir(exist_ok=True)
            with open("raw_data/sample_10_temples_validated.json", "w", encoding="utf-8") as f:
                json.dump(sample, f, ensure_ascii=False, indent=2)
            
            print("\n  Sample temples:")
            for i, temple in enumerate(sample[:3], 1):
                print(f"    {i}. {temple.get('name', 'N/A')} (ID: {temple.get('temple_id', 'N/A')})")
        else:
            print("  No temples found - checking saved HTML for debugging")
    
    except Exception as e:
        print(f"  Error scraping Nilgiris: {e}")
    
    print("\n" + "="*60)
    print(" VALIDATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Check raw_data/ folder for saved HTML files")
    print("2. Verify if temple_list.php returns actual data")
    print("3. Adjust scraping logic based on actual HTML structure")

if __name__ == "__main__":
    main()