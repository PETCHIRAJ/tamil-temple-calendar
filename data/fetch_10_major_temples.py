#!/usr/bin/env python3
"""
Fetch Complete Details for 10 Major Temples
Discovers subdomains and extracts all available information
"""

import requests
import json
import re
import time
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse

class MajorTemplesFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ta;q=0.8",
        })
        Path("raw_data/10_major_temples").mkdir(parents=True, exist_ok=True)
    
    def generate_subdomain_url(self, temple_name):
        """Generate potential subdomain URL from temple name"""
        # Clean temple name for subdomain
        name = temple_name.lower()
        
        # Remove common prefixes/suffixes
        name = name.replace("arulmigu ", "").replace(" temple", "")
        name = name.replace(" swamy", "swamy").replace(" swami", "swami")
        name = name.replace(" amman", "amman")
        
        # Common subdomain patterns
        patterns = []
        
        # Pattern 1: Direct name
        clean_name = re.sub(r'[^a-z0-9]', '', name)
        patterns.append(f"https://{clean_name}.hrce.tn.gov.in/")
        
        # Pattern 2: Split compound names
        if "and" in name:
            parts = name.split("and")
            first_part = re.sub(r'[^a-z0-9]', '', parts[0].strip())
            patterns.append(f"https://{first_part}.hrce.tn.gov.in/")
        
        # Pattern 3: Location-based (for Meenakshi Madurai style)
        words = name.split()
        if len(words) >= 2:
            # Try location + deity
            patterns.append(f"https://{words[-1]}{words[0]}.hrce.tn.gov.in/")
            # Try deity only
            patterns.append(f"https://{words[0]}.hrce.tn.gov.in/")
        
        return patterns
    
    def check_subdomain(self, url):
        """Check if subdomain exists and is valid"""
        try:
            resp = self.session.get(url, timeout=5)
            if resp.status_code == 200:
                # Check if it's a temple page (not error/redirect)
                if "temple" in resp.text.lower() and len(resp.text) > 10000:
                    return True
        except:
            pass
        return False
    
    def discover_subdomain(self, temple):
        """Discover the actual subdomain for a temple"""
        temple_name = temple.get('temple_name', '')
        temple_id = temple.get('id', '')
        
        print(f"\n  Discovering subdomain for: {temple_name}")
        
        # Generate potential URLs
        potential_urls = self.generate_subdomain_url(temple_name)
        
        # Add known patterns for specific temples
        known_subdomains = {
            "TM037875": "https://sankarankovilsankaranarayanar.hrce.tn.gov.in/",
            "TM031962": "https://maduraimeenakshi.hrce.tn.gov.in/",
            "TM000005": "https://parthasarathy.hrce.tn.gov.in/",
        }
        
        if temple_id in known_subdomains:
            return known_subdomains[temple_id]
        
        # Try each potential URL
        for url in potential_urls:
            print(f"    Trying: {url}")
            if self.check_subdomain(url):
                print(f"    ✅ Found: {url}")
                return url
        
        print(f"    ❌ No subdomain found")
        return None
    
    def extract_comprehensive_data(self, url, temple):
        """Extract all available data from temple subdomain"""
        
        temple_id = temple.get('id', '')
        temple_name = temple.get('temple_name', '')
        
        print(f"\n  Extracting data from: {url}")
        
        try:
            resp = self.session.get(url, timeout=10)
            soup = BeautifulSoup(resp.content, "html.parser")
            
            # Save HTML for reference
            with open(f"raw_data/10_major_temples/{temple_id}.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            
            data = {
                "temple_id": temple_id,
                "temple_name": temple_name,
                "district": temple.get('district', ''),
                "address": temple.get('address', ''),
                "pincode": temple.get('pincode', ''),
                "income_category": temple.get('temple_12a_category', ''),
                "subdomain_url": url,
                "extraction_status": "success"
            }
            
            # 1. Extract title and deities
            title = soup.find("title")
            if title:
                title_text = title.get_text().strip()
                data["page_title"] = title_text
                
                # Parse deities from title
                if "," in title_text:
                    parts = [p.strip() for p in title_text.split(",")]
                    data["main_deity"] = parts[0] if parts else ""
                    data["other_deities"] = parts[1:] if len(parts) > 1 else []
            
            # 2. Extract timings
            timing_table = soup.find("table")
            if timing_table:
                timing_data = []
                rows = timing_table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if cells:
                        row_text = " ".join([cell.get_text(strip=True) for cell in cells])
                        if row_text:
                            timing_data.append(row_text)
                data["timings"] = timing_data
                print(f"    ✓ Found {len(timing_data)} timing entries")
            
            # 3. Extract all headers (sections)
            headers = soup.find_all(["h1", "h2", "h3", "h4"])
            sections = []
            for header in headers:
                text = header.get_text(strip=True)
                if text and len(text) > 2:
                    sections.append(text)
            if sections:
                data["sections"] = list(set(sections))
                print(f"    ✓ Found {len(sections)} sections")
            
            # 4. Extract images with better filtering
            images = []
            img_tags = soup.find_all("img")
            for img in img_tags:
                src = img.get("src", "")
                alt = img.get("alt", "")
                
                # Skip loading/icon images
                if any(skip in src.lower() for skip in ["load.gif", "icon", "logo", "button"]):
                    continue
                
                # Make absolute URL
                if src:
                    if src.startswith("/"):
                        src = f"https://{urlparse(url).netloc}{src}"
                    elif not src.startswith("http"):
                        src = f"{url}{src}"
                    
                    images.append({
                        "url": src,
                        "alt": alt,
                        "type": "temple" if "temple" in src.lower() else "general"
                    })
            
            if images:
                data["images"] = images[:20]  # Limit to 20 images
                print(f"    ✓ Found {len(images)} images")
            
            # 5. Extract contact information
            page_text = soup.get_text()
            
            # Phone numbers
            phone_pattern = r'\b\d{10}\b|\b\d{5}[-\s]\d{5}\b'
            phones = re.findall(phone_pattern, page_text)
            if phones:
                data["phone_numbers"] = list(set(phones))[:3]
            
            # Email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_text)
            if emails:
                data["emails"] = list(set(emails))[:2]
            
            # 6. Extract Tamil content
            tamil_pattern = re.compile(r'[\u0B80-\u0BFF]+')
            tamil_texts = tamil_pattern.findall(page_text)
            tamil_phrases = []
            
            # Get meaningful Tamil phrases (not just single characters)
            for text in tamil_texts:
                if len(text) > 3:  # More than 3 Tamil characters
                    tamil_phrases.append(text)
            
            if tamil_phrases:
                # Get unique phrases
                unique_tamil = list(set(tamil_phrases))[:30]
                data["tamil_content"] = {
                    "phrases": unique_tamil[:15],
                    "count": len(unique_tamil)
                }
                print(f"    ✓ Found {len(unique_tamil)} Tamil phrases")
            
            # 7. Look for festival mentions
            festival_keywords = ["festival", "celebration", "thiruvizha", "utsavam", "vizha"]
            festival_mentions = []
            
            for keyword in festival_keywords:
                pattern = re.compile(rf'\b[^.]*{keyword}[^.]*\.', re.IGNORECASE)
                matches = pattern.findall(page_text)
                festival_mentions.extend(matches[:3])
            
            if festival_mentions:
                data["festival_mentions"] = list(set(festival_mentions))[:10]
                print(f"    ✓ Found {len(festival_mentions)} festival mentions")
            
            # 8. Look for pooja mentions
            pooja_keywords = ["pooja", "puja", "archana", "abhishekam", "homam"]
            pooja_mentions = []
            
            for keyword in pooja_keywords:
                pattern = re.compile(rf'\b[^.]*{keyword}[^.]*\.', re.IGNORECASE)
                matches = pattern.findall(page_text)
                pooja_mentions.extend(matches[:3])
            
            if pooja_mentions:
                data["pooja_mentions"] = list(set(pooja_mentions))[:10]
                print(f"    ✓ Found {len(pooja_mentions)} pooja mentions")
            
            # 9. Extract any lists (often contain facilities/features)
            lists = soup.find_all(["ul", "ol"])
            list_items = []
            for lst in lists[:3]:  # First 3 lists
                items = lst.find_all("li")
                for item in items[:5]:  # First 5 items per list
                    text = item.get_text(strip=True)
                    if text and len(text) > 5:
                        list_items.append(text)
            
            if list_items:
                data["features_list"] = list_items[:15]
                print(f"    ✓ Found {len(list_items)} list items")
            
            # 10. Check for specific information availability
            data["has_timing_info"] = bool(data.get("timings"))
            data["has_images"] = bool(data.get("images"))
            data["has_tamil_content"] = bool(data.get("tamil_content"))
            data["has_festival_info"] = bool(data.get("festival_mentions"))
            data["has_pooja_info"] = bool(data.get("pooja_mentions"))
            data["has_contact_info"] = bool(data.get("phone_numbers") or data.get("emails"))
            
            return data
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return {
                "temple_id": temple_id,
                "temple_name": temple_name,
                "extraction_status": "error",
                "error": str(e)
            }
    
    def fetch_major_temples_data(self):
        """Main function to fetch data for 10 major temples"""
        
        print("\n" + "="*60)
        print(" FETCHING COMPLETE DATA FOR 10 MAJOR TEMPLES")
        print("="*60)
        
        # Load major temples
        with open("raw_data/major_temples_test.json", "r", encoding="utf-8") as f:
            temples = json.load(f)
        
        # Process first 10 temples
        temples_to_process = temples[:10]
        all_temple_data = []
        
        for i, temple in enumerate(temples_to_process, 1):
            print(f"\n{i}. Processing: {temple.get('temple_name')}")
            print(f"   ID: {temple.get('id')}")
            print(f"   District: {temple.get('district')}")
            
            # Discover subdomain
            subdomain_url = self.discover_subdomain(temple)
            
            if subdomain_url:
                # Extract comprehensive data
                temple_data = self.extract_comprehensive_data(subdomain_url, temple)
                all_temple_data.append(temple_data)
            else:
                # No subdomain found, store basic data
                all_temple_data.append({
                    "temple_id": temple.get('id'),
                    "temple_name": temple.get('temple_name'),
                    "district": temple.get('district'),
                    "address": temple.get('address'),
                    "extraction_status": "no_subdomain"
                })
            
            # Be respectful with requests
            time.sleep(2)
        
        # Save all data
        output_file = "raw_data/10_major_temples_complete.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_temple_data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*60)
        print(" EXTRACTION COMPLETE")
        print("="*60)
        
        # Summary statistics
        successful = [t for t in all_temple_data if t.get("extraction_status") == "success"]
        
        print(f"\n📊 Summary:")
        print(f"  Total processed: {len(all_temple_data)}")
        print(f"  Successful extractions: {len(successful)}")
        print(f"  Failed/No subdomain: {len(all_temple_data) - len(successful)}")
        
        if successful:
            print(f"\n✅ Successfully extracted temples:")
            for temple in successful:
                print(f"  - {temple['temple_name']}")
                info_types = []
                if temple.get("has_timing_info"): info_types.append("Timings")
                if temple.get("has_images"): info_types.append(f"Images({len(temple.get('images', []))})")
                if temple.get("has_tamil_content"): info_types.append("Tamil")
                if temple.get("has_festival_info"): info_types.append("Festivals")
                if temple.get("has_pooja_info"): info_types.append("Poojas")
                if temple.get("has_contact_info"): info_types.append("Contact")
                print(f"    Data: {', '.join(info_types)}")
        
        print(f"\n📁 Output saved to: {output_file}")
        print(f"📁 HTML files saved in: raw_data/10_major_temples/")
        
        return all_temple_data

def main():
    fetcher = MajorTemplesFetcher()
    temple_data = fetcher.fetch_major_temples_data()
    
    print("\n" + "="*60)
    print(" FINAL SUMMARY")
    print("="*60)
    
    # Create a summary report
    summary = {
        "total_temples": len(temple_data),
        "successful": len([t for t in temple_data if t.get("extraction_status") == "success"]),
        "data_types_found": {
            "timings": len([t for t in temple_data if t.get("has_timing_info")]),
            "images": len([t for t in temple_data if t.get("has_images")]),
            "tamil_content": len([t for t in temple_data if t.get("has_tamil_content")]),
            "festivals": len([t for t in temple_data if t.get("has_festival_info")]),
            "poojas": len([t for t in temple_data if t.get("has_pooja_info")]),
            "contact": len([t for t in temple_data if t.get("has_contact_info")])
        }
    }
    
    with open("raw_data/10_temples_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Data extraction complete!")
    print(f"📊 Check these files:")
    print(f"  - raw_data/10_major_temples_complete.json (all data)")
    print(f"  - raw_data/10_temples_summary.json (summary)")
    print(f"  - raw_data/10_major_temples/*.html (HTML pages)")

if __name__ == "__main__":
    main()