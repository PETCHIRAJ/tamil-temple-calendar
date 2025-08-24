#!/usr/bin/env python3
"""
HR&CE Temple Subdomain Scraper
Extract detailed information from temple-specific subdomains
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from pathlib import Path

class HRCESubdomainScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        Path("raw_data/temple_details").mkdir(parents=True, exist_ok=True)
    
    def extract_temple_details(self, url, temple_id):
        """Extract detailed information from temple subdomain"""
        
        print(f"\n{'='*60}")
        print(f"Extracting from: {url}")
        print('='*60)
        
        try:
            resp = self.session.get(url, timeout=10)
            soup = BeautifulSoup(resp.content, "html.parser")
            
            temple_info = {
                "temple_id": temple_id,
                "url": url,
                "status": "success"
            }
            
            # 1. Extract title and basic info
            title = soup.find("title")
            if title:
                temple_info["full_title"] = title.get_text().strip()
                # Parse title for temple names
                title_parts = title.get_text().split(",")
                if title_parts:
                    temple_info["main_temple"] = title_parts[0].strip()
                    if len(title_parts) > 1:
                        temple_info["other_deities"] = [p.strip() for p in title_parts[1:]]
            
            # 2. Extract Poojas section
            poojas_section = soup.find("h2", string=re.compile("Pooja", re.I))
            if poojas_section:
                pooja_content = []
                next_elem = poojas_section.find_next_sibling()
                while next_elem and next_elem.name != "h2":
                    text = next_elem.get_text(strip=True)
                    if text:
                        pooja_content.append(text)
                    next_elem = next_elem.find_next_sibling()
                
                temple_info["poojas"] = pooja_content
                print(f"  ✓ Found {len(pooja_content)} pooja entries")
            
            # 3. Extract Festivals section
            festivals_section = soup.find("h2", string=re.compile("Festival", re.I))
            if festivals_section:
                festival_content = []
                next_elem = festivals_section.find_next_sibling()
                while next_elem and next_elem.name != "h2":
                    text = next_elem.get_text(strip=True)
                    if text:
                        festival_content.append(text)
                    next_elem = next_elem.find_next_sibling()
                
                temple_info["festivals"] = festival_content
                print(f"  ✓ Found {len(festival_content)} festival entries")
            
            # 4. Extract images
            images = soup.find_all("img")
            image_urls = []
            for img in images:
                src = img.get("src")
                if src and not any(skip in src.lower() for skip in ["logo", "icon", "button"]):
                    # Make absolute URL if relative
                    if src.startswith("/"):
                        src = f"https://{url.split('/')[2]}{src}"
                    elif not src.startswith("http"):
                        src = f"{'/'.join(url.split('/')[:3])}/{src}"
                    
                    image_urls.append({
                        "url": src,
                        "alt": img.get("alt", "")
                    })
            
            if image_urls:
                temple_info["images"] = image_urls[:10]  # First 10 images
                print(f"  ✓ Found {len(image_urls)} images")
            
            # 5. Extract contact information
            contact_patterns = [
                r'\b\d{10}\b',  # Phone numbers
                r'\b\d{6}\b',    # Pincode
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email
            ]
            
            page_text = soup.get_text()
            contacts = {}
            
            for pattern in contact_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    if '@' in pattern:
                        contacts["emails"] = list(set(matches))
                    elif len(matches[0]) == 10:
                        contacts["phones"] = list(set(matches))[:3]
                    elif len(matches[0]) == 6:
                        contacts["pincodes"] = list(set(matches))[:2]
            
            if contacts:
                temple_info["contact_info"] = contacts
                print(f"  ✓ Found contact information")
            
            # 6. Extract any tables
            tables = soup.find_all("table")
            if tables:
                table_data = []
                for table in tables[:3]:  # First 3 tables
                    rows = table.find_all("tr")
                    table_content = []
                    for row in rows[:10]:  # First 10 rows
                        cells = row.find_all(["td", "th"])
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        if any(row_data):
                            table_content.append(row_data)
                    if table_content:
                        table_data.append(table_content)
                
                if table_data:
                    temple_info["tables"] = table_data
                    print(f"  ✓ Found {len(table_data)} tables")
            
            # 7. Extract temple timings
            timing_keywords = ["timing", "time", "open", "close", "darshan"]
            timing_texts = []
            
            for keyword in timing_keywords:
                elements = soup.find_all(string=re.compile(keyword, re.I))
                for elem in elements[:5]:
                    parent = elem.parent
                    if parent:
                        text = parent.get_text(strip=True)
                        if len(text) > 10 and len(text) < 200:
                            timing_texts.append(text)
            
            if timing_texts:
                temple_info["timing_info"] = list(set(timing_texts))[:5]
                print(f"  ✓ Found timing information")
            
            # 8. Extract any Tamil content
            tamil_pattern = re.compile(r'[\u0B80-\u0BFF]+')
            tamil_texts = tamil_pattern.findall(page_text)
            if tamil_texts:
                # Get unique Tamil words/phrases
                unique_tamil = list(set([t for t in tamil_texts if len(t) > 2]))[:20]
                temple_info["tamil_content"] = unique_tamil
                print(f"  ✓ Found {len(unique_tamil)} Tamil terms")
            
            # Save detailed HTML for reference
            with open(f"raw_data/temple_details/{temple_id}_subdomain.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            
            return temple_info
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return {"temple_id": temple_id, "status": "error", "error": str(e)}
    
    def scrape_major_temples(self):
        """Scrape information from known temple subdomains"""
        
        print("\n" + "="*60)
        print(" HR&CE TEMPLE SUBDOMAIN SCRAPER")
        print("="*60)
        
        # Known temple subdomains
        temples_with_subdomains = [
            {
                "id": "TM037875",
                "name": "Sankarankovil",
                "url": "https://sankarankovilsankaranarayanar.hrce.tn.gov.in/"
            },
            {
                "id": "TM031962",
                "name": "Madurai Meenakshi",
                "url": "https://maduraimeenakshi.hrce.tn.gov.in/"
            },
            {
                "id": "TM000005",
                "name": "Parthasarathy",
                "url": "https://parthasarathy.hrce.tn.gov.in/"
            }
        ]
        
        all_temple_data = []
        
        for temple in temples_with_subdomains:
            print(f"\nProcessing: {temple['name']}")
            data = self.extract_temple_details(temple["url"], temple["id"])
            data["temple_name"] = temple["name"]
            all_temple_data.append(data)
        
        # Save all data
        with open("raw_data/temple_subdomain_data.json", "w", encoding="utf-8") as f:
            json.dump(all_temple_data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*60)
        print(" EXTRACTION SUMMARY")
        print("="*60)
        
        for temple in all_temple_data:
            if temple.get("status") == "success":
                print(f"\n✅ {temple.get('temple_name', temple['temple_id'])}:")
                
                # Show what data was extracted
                data_types = []
                if temple.get("poojas"):
                    data_types.append(f"Poojas ({len(temple['poojas'])})")
                if temple.get("festivals"):
                    data_types.append(f"Festivals ({len(temple['festivals'])})")
                if temple.get("images"):
                    data_types.append(f"Images ({len(temple['images'])})")
                if temple.get("contact_info"):
                    data_types.append("Contact info")
                if temple.get("timing_info"):
                    data_types.append("Timings")
                if temple.get("tamil_content"):
                    data_types.append(f"Tamil content ({len(temple['tamil_content'])} terms)")
                
                print(f"   Data extracted: {', '.join(data_types)}")
                
                # Sample festival data
                if temple.get("festivals"):
                    print(f"\n   Sample Festivals:")
                    for fest in temple["festivals"][:3]:
                        print(f"     - {fest[:100]}...")
                
                # Sample pooja data  
                if temple.get("poojas"):
                    print(f"\n   Sample Poojas:")
                    for pooja in temple["poojas"][:3]:
                        print(f"     - {pooja[:100]}...")
        
        return all_temple_data

def main():
    scraper = HRCESubdomainScraper()
    temple_data = scraper.scrape_major_temples()
    
    print("\n" + "="*60)
    print(" FINAL RESULTS")
    print("="*60)
    
    print(f"\n✅ Successfully extracted detailed data from {len(temple_data)} temples")
    print(f"\n📁 Files generated:")
    print(f"   - raw_data/temple_subdomain_data.json (structured data)")
    print(f"   - raw_data/temple_details/*.html (full HTML pages)")
    
    print(f"\n📊 Available Information Types:")
    print(f"   - Temple names and deities")
    print(f"   - Festival calendars")
    print(f"   - Pooja details and timings")
    print(f"   - Contact information")
    print(f"   - Temple images")
    print(f"   - Tamil language content")
    
    print(f"\n🎯 This data can be used to:")
    print(f"   1. Build rich temple profiles in the app")
    print(f"   2. Create festival calendar features")
    print(f"   3. Show pooja timings and services")
    print(f"   4. Display temple images and galleries")
    print(f"   5. Provide contact details for devotees")

if __name__ == "__main__":
    main()