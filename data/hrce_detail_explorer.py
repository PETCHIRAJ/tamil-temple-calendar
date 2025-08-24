#!/usr/bin/env python3
"""
HR&CE Temple Detail Explorer using Selenium
Explores what information is available for major temples
"""

import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class HRCEDetailExplorer:
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
        Path("raw_data/temple_details").mkdir(parents=True, exist_ok=True)
    
    def explore_temple_detail(self, temple_id, temple_name):
        """Explore what information is available for a specific temple"""
        
        print(f"\n{'='*60}")
        print(f"Exploring: {temple_name}")
        print(f"ID: {temple_id}")
        print('='*60)
        
        results = {
            "temple_id": temple_id,
            "temple_name": temple_name,
            "urls_tried": [],
            "data_found": {}
        }
        
        # Try different URL patterns
        url_patterns = [
            f"{self.base_url}/hrcehome/index_temple.php?tid={temple_id}",
            f"{self.base_url}/hrcehome/temple_details.php?id={temple_id}",
            f"{self.base_url}/hrcehome/temple.php?id={temple_id}",
        ]
        
        for url in url_patterns:
            print(f"\nTrying URL: {url}")
            results["urls_tried"].append(url)
            
            try:
                self.driver.get(url)
                time.sleep(3)  # Wait for page to load
                
                # Check for error messages
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                
                if "date mismatched" in page_text.lower():
                    print("  ❌ Date mismatch error")
                    continue
                
                if "no matching records" in page_text.lower():
                    print("  ❌ No matching records")
                    continue
                
                if len(page_text.strip()) < 100:
                    print("  ❌ Empty or minimal content")
                    continue
                
                # Page loaded successfully, explore content
                print("  ✅ Page loaded successfully")
                
                # Save screenshot
                screenshot_path = f"raw_data/temple_details/{temple_id}_screenshot.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"  📸 Screenshot saved: {screenshot_path}")
                
                # Save HTML for analysis
                html_path = f"raw_data/temple_details/{temple_id}_page.html"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print(f"  📄 HTML saved: {html_path}")
                
                # Extract available information
                info = self.extract_temple_info()
                results["data_found"] = info
                
                if info:
                    print("\n  📊 Information Found:")
                    for key, value in info.items():
                        if value:
                            print(f"    ✓ {key}: {str(value)[:100]}...")
                
                break  # Success, no need to try other URLs
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                continue
        
        return results
    
    def extract_temple_info(self):
        """Extract all available information from current page"""
        
        info = {}
        
        try:
            # Look for common data patterns
            
            # 1. Headers (temple name, deity names)
            headers = self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4")
            temple_headers = []
            for h in headers:
                text = h.text.strip()
                if text and len(text) > 3:
                    temple_headers.append(text)
            if temple_headers:
                info["headers"] = temple_headers[:5]
            
            # 2. Tables (often contain structured data)
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            if tables:
                info["tables_count"] = len(tables)
                table_data = []
                for i, table in enumerate(tables[:3]):  # First 3 tables
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if rows:
                        # Get headers
                        headers = []
                        header_row = rows[0].find_elements(By.CSS_SELECTOR, "th, td")
                        for cell in header_row:
                            headers.append(cell.text.strip())
                        
                        # Get sample data
                        sample_rows = []
                        for row in rows[1:3]:  # First 2 data rows
                            cells = row.find_elements(By.TAG_NAME, "td")
                            row_data = [cell.text.strip() for cell in cells]
                            if any(row_data):
                                sample_rows.append(row_data)
                        
                        if headers or sample_rows:
                            table_data.append({
                                "headers": headers,
                                "sample_rows": sample_rows
                            })
                
                if table_data:
                    info["table_samples"] = table_data
            
            # 3. Look for specific keywords
            keywords_to_find = {
                "deity": ["deity", "god", "goddess", "swamy", "amman", "perumal"],
                "festival": ["festival", "celebration", "thiruvizha", "utsavam"],
                "timing": ["timing", "time", "pooja", "puja", "worship"],
                "history": ["history", "legend", "story", "sthala"],
                "contact": ["contact", "phone", "email", "address"],
                "facility": ["facility", "amenity", "parking", "annadhanam"]
            }
            
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            for category, keywords in keywords_to_find.items():
                for keyword in keywords:
                    if keyword in page_text:
                        info[f"has_{category}"] = True
                        break
            
            # 4. Images (gallery, deity photos)
            images = self.driver.find_elements(By.TAG_NAME, "img")
            image_info = []
            for img in images[:5]:  # First 5 images
                src = img.get_attribute("src")
                alt = img.get_attribute("alt")
                if src and not "logo" in src.lower():
                    image_info.append({
                        "src": src,
                        "alt": alt or "No description"
                    })
            if image_info:
                info["images"] = image_info
            
            # 5. Lists (often contain features, facilities)
            lists = self.driver.find_elements(By.CSS_SELECTOR, "ul li, ol li")
            if lists:
                list_items = []
                for item in lists[:10]:  # First 10 items
                    text = item.text.strip()
                    if text and len(text) > 5:
                        list_items.append(text)
                if list_items:
                    info["list_items"] = list_items
            
            # 6. Paragraphs (temple description, history)
            paragraphs = self.driver.find_elements(By.TAG_NAME, "p")
            descriptions = []
            for p in paragraphs:
                text = p.text.strip()
                if len(text) > 50:  # Meaningful paragraphs
                    descriptions.append(text[:200])
                    if len(descriptions) >= 3:
                        break
            if descriptions:
                info["descriptions"] = descriptions
            
        except Exception as e:
            print(f"    Error extracting info: {e}")
        
        return info
    
    def explore_major_temples(self):
        """Explore information for major temples"""
        
        print("\n" + "="*60)
        print(" HR&CE TEMPLE DETAIL EXPLORATION")
        print("="*60)
        
        # Load major temples
        with open("raw_data/major_temples_test.json", "r", encoding="utf-8") as f:
            temples = json.load(f)
        
        print(f"\n🎯 Testing {len(temples[:3])} temples...")
        
        all_results = []
        
        # Test first 3 temples
        for temple in temples[:3]:
            result = self.explore_temple_detail(
                temple.get("id"),
                temple.get("temple_name")
            )
            all_results.append(result)
            time.sleep(2)  # Be respectful between requests
        
        # Save results
        with open("raw_data/temple_exploration_results.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # Analyze findings
        print("\n" + "="*60)
        print(" EXPLORATION SUMMARY")
        print("="*60)
        
        successful = [r for r in all_results if r.get("data_found")]
        
        if successful:
            print(f"\n✅ Successfully accessed {len(successful)} temples")
            
            # Check what types of data are available
            data_types = set()
            for result in successful:
                data = result.get("data_found", {})
                data_types.update(data.keys())
            
            print(f"\n📊 Types of Information Available:")
            for dtype in sorted(data_types):
                print(f"  - {dtype}")
            
            # Sample successful result
            if successful:
                sample = successful[0]
                print(f"\n📝 Sample Data from {sample['temple_name']}:")
                for key, value in sample.get("data_found", {}).items():
                    print(f"  {key}: {str(value)[:100]}...")
        else:
            print(f"\n❌ Could not access temple details")
            print(f"   The site may require:")
            print(f"   - Authentication/login")
            print(f"   - Different URL patterns")
            print(f"   - Browser automation with interaction")
        
        return all_results
    
    def cleanup(self):
        """Close the browser"""
        self.driver.quit()

def main():
    print("Starting HR&CE Detail Explorer...")
    print("NOTE: This requires Chrome and ChromeDriver")
    
    try:
        explorer = HRCEDetailExplorer(headless=False)  # Set True for headless
        results = explorer.explore_major_temples()
        
        print("\n" + "="*60)
        print(" EXPLORATION COMPLETE")
        print("="*60)
        
        print("\n📁 Check these files for details:")
        print("  - raw_data/temple_exploration_results.json")
        print("  - raw_data/temple_details/*.png (screenshots)")
        print("  - raw_data/temple_details/*.html (page source)")
        
        explorer.cleanup()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Install Chrome: brew install --cask google-chrome")
        print("2. Install ChromeDriver: brew install --cask chromedriver")
        print("3. Allow ChromeDriver in Security settings")
        print("4. Install Selenium: pip install selenium")

if __name__ == "__main__":
    main()