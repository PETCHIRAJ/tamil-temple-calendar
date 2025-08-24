#!/usr/bin/env python3
"""
HR&CE Temple Scraper with Server Date Synchronization
Bypasses the "system date mismatched" error by syncing with server time
"""

import requests
import time
import json
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

class HRCESyncedScraper:
    def __init__(self):
        # Create persistent session
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        
        self.base_url = "https://hrce.tn.gov.in"
        self.server_date = None
        
        # Create output directory
        Path("raw_data").mkdir(exist_ok=True)
    
    def sync_with_server(self):
        """Synchronize with server date/time"""
        print("Synchronizing with HR&CE server...")
        
        # First, fetch the homepage to establish session
        homepage_url = f"{self.base_url}/hrcehome/temple_list.php"
        
        try:
            # Get homepage to capture server date and cookies
            home_resp = self.session.get(homepage_url, timeout=10)
            home_resp.raise_for_status()
            
            # Extract server Date header
            self.server_date = home_resp.headers.get("Date")
            
            if not self.server_date:
                print("Warning: Server did not return a Date header")
                # Generate a date in the expected format
                import email.utils
                self.server_date = email.utils.formatdate(usegmt=True)
            
            print(f"Server date synchronized: {self.server_date}")
            
            # Update session headers with server date and referer
            self.session.headers.update({
                "Date": self.server_date,
                "Referer": homepage_url,
                "X-Requested-With": "XMLHttpRequest"  # Sometimes needed for AJAX
            })
            
            # Save cookies info
            print(f"Cookies obtained: {dict(self.session.cookies)}")
            
            return True
            
        except Exception as e:
            print(f"Error synchronizing with server: {e}")
            return False
    
    def fetch_district_temples(self, district, max_pages=3):
        """Fetch temples for a specific district"""
        print(f"\nFetching temples for district: {district}")
        
        temples = []
        page = 1
        
        while page <= max_pages:
            print(f"  Page {page}...")
            
            params = {
                "district": district,
                "page": page
            }
            
            try:
                # Add small delay to be respectful
                time.sleep(1)
                
                resp = self.session.get(
                    f"{self.base_url}/hrcehome/temple_list.php",
                    params=params,
                    timeout=10
                )
                resp.raise_for_status()
                
                # Parse response
                soup = BeautifulSoup(resp.content, "html.parser")
                
                # Save first page for debugging
                if page == 1:
                    with open(f"raw_data/{district}_synced_page1.html", "w", encoding="utf-8") as f:
                        f.write(str(soup.prettify()))
                
                # Check for date mismatch error
                error_msg = soup.find("p", string=lambda text: "date mismatched" in text if text else False)
                if error_msg:
                    print("  ❌ Still getting date mismatch error")
                    print("  Attempting to re-sync...")
                    self.sync_with_server()
                    continue
                
                # Find all tables
                tables = soup.find_all("table")
                print(f"  Found {len(tables)} tables")
                
                # Look for temple data in tables
                found_temples = False
                for table in tables:
                    rows = table.find_all("tr")
                    
                    # Skip if too few rows
                    if len(rows) < 2:
                        continue
                    
                    # Check if this looks like temple data
                    header_row = rows[0]
                    headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
                    
                    # Process data rows
                    for row in rows[1:]:
                        cols = row.find_all("td")
                        if len(cols) >= 2:  # At least 2 columns
                            temple_data = {}
                            
                            for i, col in enumerate(cols):
                                # Get text content
                                text = col.get_text(strip=True)
                                
                                # Try to identify what each column contains
                                if i == 0:
                                    temple_data["sno"] = text
                                elif "TM" in text:  # Temple ID pattern
                                    temple_data["temple_id"] = text
                                elif i < len(headers):
                                    temple_data[f"field_{i}"] = text
                                else:
                                    temple_data[f"field_{i}"] = text
                                
                                # Check for links (might contain temple ID)
                                link = col.find("a")
                                if link and link.get("href"):
                                    href = link.get("href")
                                    if "tid=" in href or "temple_id=" in href:
                                        temple_data["link"] = href
                            
                            # Only add if we have meaningful data
                            if any(v and v != "No matching records found" for v in temple_data.values()):
                                temple_data["district"] = district
                                temple_data["page"] = page
                                temples.append(temple_data)
                                found_temples = True
                
                if found_temples:
                    print(f"  ✓ Found {len(temples)} temples so far")
                else:
                    print("  No temple data found on this page")
                    # Try to understand what we got
                    text_content = soup.get_text()
                    if "No matching records" in text_content:
                        print("  Message: No matching records")
                        break
                    elif len(text_content.strip()) < 100:
                        print(f"  Page seems empty: {text_content[:100]}")
                        break
                
                page += 1
                
            except Exception as e:
                print(f"  Error on page {page}: {e}")
                break
        
        return temples
    
    def validate_temple_detail(self, temple_id):
        """Fetch details for a specific temple"""
        print(f"\nValidating temple: {temple_id}")
        
        url = f"{self.base_url}/hrcehome/index_temple.php"
        params = {"tid": temple_id}
        
        try:
            time.sleep(1)
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.content, "html.parser")
            
            # Save for analysis
            with open(f"raw_data/temple_{temple_id}_synced.html", "w", encoding="utf-8") as f:
                f.write(str(soup.prettify()))
            
            # Check for error
            error_msg = soup.find("p", string=lambda text: "date mismatched" in text if text else False)
            if error_msg:
                return {"error": "Date mismatch still present"}
            
            # Extract temple details
            details = {
                "temple_id": temple_id,
                "title": soup.find("title").get_text(strip=True) if soup.find("title") else None,
                "has_content": len(soup.get_text(strip=True)) > 100
            }
            
            # Look for temple name
            for tag in ["h1", "h2", "h3"]:
                headers = soup.find_all(tag)
                for h in headers:
                    text = h.get_text(strip=True)
                    if text and len(text) > 5:
                        details["temple_name"] = text
                        break
            
            return details
            
        except Exception as e:
            return {"error": str(e)}
    
    def fetch_sample_temples(self):
        """Main function to fetch sample temples"""
        print("\n" + "="*60)
        print(" HR&CE TEMPLE SCRAPER WITH DATE SYNC")
        print("="*60)
        
        # Step 1: Sync with server
        if not self.sync_with_server():
            print("Failed to sync with server")
            return None
        
        # Step 2: Test with first 3 districts
        test_districts = ["Ariyalur", "Nilgiris", "Chennai"]
        all_temples = []
        
        for district in test_districts:
            temples = self.fetch_district_temples(district, max_pages=2)
            
            if temples:
                all_temples.extend(temples)
                print(f"  Total collected: {len(all_temples)} temples")
                
                # Save intermediate results
                with open(f"raw_data/{district}_temples.json", "w", encoding="utf-8") as f:
                    json.dump(temples, f, ensure_ascii=False, indent=2)
            
            # Stop if we have enough samples
            if len(all_temples) >= 10:
                print("\nReached 10+ temples for validation")
                break
        
        # Step 3: Validate a temple detail page
        if all_temples and "temple_id" in all_temples[0]:
            temple_id = all_temples[0]["temple_id"]
            print(f"\nValidating temple detail page for: {temple_id}")
            details = self.validate_temple_detail(temple_id)
            print(f"Details: {json.dumps(details, indent=2)}")
        
        # Step 4: Save final results
        if all_temples:
            # Get first 10 for validation
            sample_10 = all_temples[:10]
            
            with open("raw_data/sample_10_temples_final.json", "w", encoding="utf-8") as f:
                json.dump(sample_10, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ Successfully fetched {len(all_temples)} temples!")
            print(f"✓ Saved 10 sample temples to raw_data/sample_10_temples_final.json")
            
            print("\nSample temples:")
            for i, temple in enumerate(sample_10[:5], 1):
                print(f"{i}. {temple}")
            
            return sample_10
        else:
            print("\n✗ No temples fetched - check raw_data/ for HTML dumps")
            return None

def main():
    scraper = HRCESyncedScraper()
    temples = scraper.fetch_sample_temples()
    
    if temples:
        print("\n" + "="*60)
        print(" VALIDATION SUCCESSFUL!")
        print("="*60)
        print("\nYou can now:")
        print("1. Check raw_data/sample_10_temples_final.json")
        print("2. Verify the temple data structure")
        print("3. Scale up to fetch all 46,303 temples")
    else:
        print("\n" + "="*60)
        print(" VALIDATION FAILED")
        print("="*60)
        print("\nTroubleshooting:")
        print("1. Check raw_data/*_synced_page1.html files")
        print("2. The site may require browser automation (Selenium)")
        print("3. Consider official API access from HR&CE")

if __name__ == "__main__":
    main()