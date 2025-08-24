#!/usr/bin/env python3
"""
HR&CE Temple Scraper using Selenium
Handles JavaScript-rendered content and dynamic loading
"""

import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class HRCESeleniumScraper:
    def __init__(self, headless=False):
        """Initialize Selenium WebDriver"""
        self.base_url = "https://hrce.tn.gov.in"
        
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Create driver
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Create output directory
        Path("raw_data").mkdir(exist_ok=True)
    
    def fetch_temples_by_search(self):
        """Use the temple search form to get temple data"""
        print("\n" + "="*60)
        print(" HR&CE SELENIUM SCRAPER - TEMPLE SEARCH")
        print("="*60)
        
        try:
            # Navigate to temple search page
            search_url = f"{self.base_url}/hrcehome/temples_search.php?activity=temple_search"
            print(f"\n1. Navigating to: {search_url}")
            self.driver.get(search_url)
            time.sleep(3)  # Wait for page to load
            
            # Take screenshot for debugging
            self.driver.save_screenshot("raw_data/search_page.png")
            print("   ✓ Screenshot saved: raw_data/search_page.png")
            
            # Try to find and select district dropdown
            print("\n2. Looking for district dropdown...")
            try:
                # Look for district select element
                district_select = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "district"))
                )
                
                # Create Select object
                select = Select(district_select)
                
                # Get all options
                options = select.options
                district_names = [opt.get_attribute('value') for opt in options if opt.get_attribute('value')]
                print(f"   ✓ Found {len(district_names)} districts")
                
                # Select first non-empty district (usually Ariyalur)
                if district_names:
                    test_district = district_names[0] if district_names[0] else district_names[1]
                    print(f"\n3. Selecting district: {test_district}")
                    select.select_by_value(test_district)
                    time.sleep(2)
                    
                    # Click search/submit button
                    print("\n4. Looking for search button...")
                    search_buttons = self.driver.find_elements(By.XPATH, "//input[@type='submit'] | //button[@type='submit'] | //input[@value='Search'] | //button[contains(text(), 'Search')]")
                    
                    if search_buttons:
                        print(f"   ✓ Found {len(search_buttons)} search buttons")
                        search_buttons[0].click()
                        time.sleep(5)  # Wait for results
                        
                        # Take screenshot of results
                        self.driver.save_screenshot("raw_data/search_results.png")
                        print("   ✓ Results screenshot: raw_data/search_results.png")
                        
                        # Extract temple data from results
                        temples = self.extract_temple_data()
                        return temples
                    else:
                        print("   ✗ No search button found")
                
            except TimeoutException:
                print("   ✗ District dropdown not found")
                
                # Try alternative: direct navigation with parameters
                print("\n   Trying alternative: Direct URL with parameters...")
                list_url = f"{self.base_url}/hrcehome/temple_list.php?district=Ariyalur"
                self.driver.get(list_url)
                time.sleep(5)
                
                self.driver.save_screenshot("raw_data/direct_list.png")
                temples = self.extract_temple_data()
                return temples
                
        except Exception as e:
            print(f"\n✗ Error: {e}")
            return []
        
    def extract_temple_data(self):
        """Extract temple data from current page"""
        temples = []
        
        try:
            # Save page source for debugging
            with open("raw_data/page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("\n5. Extracting temple data...")
            
            # Look for tables with temple data
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            print(f"   Found {len(tables)} tables")
            
            for i, table in enumerate(tables):
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                if len(rows) > 1:  # Has data rows
                    print(f"\n   Table {i+1}: {len(rows)} rows")
                    
                    # Process each row
                    for j, row in enumerate(rows[1:]):  # Skip header
                        cols = row.find_elements(By.TAG_NAME, "td")
                        
                        if len(cols) >= 2:
                            temple_data = {}
                            
                            # Extract text from each column
                            for k, col in enumerate(cols):
                                text = col.text.strip()
                                
                                # Try to identify columns
                                if k == 0:
                                    temple_data["sno"] = text
                                elif "TM" in text:  # Temple ID pattern
                                    temple_data["temple_id"] = text
                                elif k == 1 and "TM" not in text:
                                    temple_data["name"] = text
                                else:
                                    temple_data[f"field_{k}"] = text
                                
                                # Check for links
                                links = col.find_elements(By.TAG_NAME, "a")
                                if links:
                                    href = links[0].get_attribute("href")
                                    if href and ("tid=" in href or "temple_id=" in href):
                                        temple_data["detail_url"] = href
                                        # Extract temple ID from URL
                                        if "tid=" in href:
                                            tid = href.split("tid=")[1].split("&")[0]
                                            temple_data["temple_id"] = tid
                            
                            # Only add if we have meaningful data
                            if temple_data and not any("No matching records" in str(v) for v in temple_data.values()):
                                temples.append(temple_data)
                                
                                # Print first temple as sample
                                if len(temples) == 1:
                                    print(f"\n   Sample temple: {json.dumps(temple_data, indent=2)}")
            
            # If no tables, look for temple data in other formats
            if not temples:
                print("\n   No temple data in tables, checking for divs/lists...")
                
                # Look for temple entries in divs
                temple_divs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'temple')] | //div[contains(@id, 'temple')]")
                
                for div in temple_divs[:10]:  # First 10
                    text = div.text.strip()
                    if text and "TM" in text:
                        temples.append({"raw_text": text})
            
            print(f"\n   ✓ Extracted {len(temples)} temples")
            
        except Exception as e:
            print(f"   ✗ Error extracting data: {e}")
        
        return temples
    
    def fetch_sample_temples(self):
        """Main function to fetch sample temples"""
        temples = []
        
        try:
            # Method 1: Try search form
            temples = self.fetch_temples_by_search()
            
            # Method 2: If no results, try browsing temple list directly
            if not temples:
                print("\n6. Trying temple list page...")
                self.driver.get(f"{self.base_url}/hrcehome/temple_list.php")
                time.sleep(3)
                
                # Look for any district links or forms
                district_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'district=')]")
                
                if district_links:
                    print(f"   Found {len(district_links)} district links")
                    # Click first district
                    district_links[0].click()
                    time.sleep(5)
                    
                    temples = self.extract_temple_data()
            
            # Save results
            if temples:
                # Get first 10 temples
                sample_10 = temples[:10]
                
                with open("raw_data/selenium_sample_10_temples.json", "w", encoding="utf-8") as f:
                    json.dump(sample_10, f, ensure_ascii=False, indent=2)
                
                print("\n" + "="*60)
                print(" SUCCESS!")
                print("="*60)
                print(f"✓ Fetched {len(temples)} temples")
                print(f"✓ Saved 10 samples to: raw_data/selenium_sample_10_temples.json")
                
                print("\nFirst 3 temples:")
                for i, temple in enumerate(sample_10[:3], 1):
                    print(f"{i}. {temple}")
            else:
                print("\n" + "="*60)
                print(" NO TEMPLES FOUND")
                print("="*60)
                print("Check raw_data/ folder for screenshots and HTML")
                
        finally:
            # Close browser
            self.driver.quit()
        
        return temples

def main():
    """Run the scraper"""
    print("Starting HR&CE Selenium Scraper...")
    print("\nNOTE: This requires Chrome browser and ChromeDriver installed")
    print("Install with: brew install --cask chromedriver")
    
    scraper = HRCESeleniumScraper(headless=False)  # Set to True for headless mode
    temples = scraper.fetch_sample_temples()
    
    if temples:
        print("\n✅ Validation successful!")
        print("Next steps:")
        print("1. Verify temple data structure")
        print("2. Check if temple IDs match expected format")
        print("3. Scale up to fetch all districts")
    else:
        print("\n⚠️ No temples fetched")
        print("Troubleshooting:")
        print("1. Check screenshots in raw_data/")
        print("2. Review page_source.html for actual content")
        print("3. May need to handle captchas or additional authentication")

if __name__ == "__main__":
    main()