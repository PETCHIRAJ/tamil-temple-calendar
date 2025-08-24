#!/usr/bin/env python3
"""
Scrape All 578 Major Temples from HR&CE
Discovers subdomains and extracts all available information
Skips image downloads for now (URLs are saved for later)
"""

import requests
import json
import re
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class MajorTemplesScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ta;q=0.8",
        })
        
        Path("major_temples_data").mkdir(exist_ok=True)
        self.discovered_subdomains = []
        self.failed_temples = []
        self.successful_temples = []
        
    def generate_subdomain_patterns(self, temple_name, district=None):
        """Generate multiple subdomain patterns to try"""
        patterns = []
        
        # Clean temple name
        name = temple_name.lower()
        name = name.replace("arulmigu ", "").replace(" temple", "")
        name = name.replace(" swamy", "swamy").replace(" swami", "swami")
        name = name.replace(" amman", "amman").replace(" ", "")
        
        # Remove special characters
        clean_name = re.sub(r'[^a-z0-9]', '', name)
        
        # Pattern 1: Direct clean name
        if clean_name:
            patterns.append(clean_name)
        
        # Pattern 2: First word only
        first_word = name.split()[0] if ' ' in temple_name.lower() else clean_name
        if first_word and first_word != clean_name:
            patterns.append(re.sub(r'[^a-z0-9]', '', first_word))
        
        # Pattern 3: Key deity names
        deity_keywords = ['vinayagar', 'murugan', 'perumal', 'amman', 'swamy', 'swami', 
                         'eswarar', 'nathar', 'mariamman', 'ayyappan']
        for keyword in deity_keywords:
            if keyword in name:
                patterns.append(keyword)
                # Also try with location
                if district:
                    location = district.lower().replace(' district', '').replace(' ', '')
                    patterns.append(f"{location}{keyword}")
        
        # Pattern 4: Location-based (for famous temples)
        if district:
            location = district.lower().replace(' district', '').replace(' ', '')
            patterns.append(f"{location}{clean_name[:10]}")
        
        # Remove duplicates and return
        return list(dict.fromkeys(patterns))[:5]  # Try max 5 patterns
    
    def check_subdomain(self, url, quick_check=True):
        """Check if subdomain exists and has temple content"""
        try:
            resp = self.session.get(url, timeout=3 if quick_check else 10)
            if resp.status_code == 200:
                # Check for temple content indicators
                content = resp.text.lower()
                if len(resp.text) > 10000 and any(word in content for word in ['temple', 'kovil', 'pooja', 'deity']):
                    return True
        except:
            pass
        return False
    
    def extract_temple_data(self, url, temple):
        """Extract all data from temple subdomain (without downloading images)"""
        try:
            resp = self.session.get(url, timeout=10)
            
            # Parse with simple string operations for speed
            content = resp.text
            
            data = {
                "temple_id": temple.get('id'),
                "temple_name": temple.get('temple_name'),
                "district": temple.get('district'),
                "subdomain_url": url,
                "extraction_timestamp": datetime.now().isoformat(),
                "content_length": len(content)
            }
            
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if title_match:
                data["page_title"] = title_match.group(1).strip()
            
            # Extract deities from title or content
            deity_names = []
            deity_patterns = [
                r'Arulmigu\s+(\w+(?:\s+\w+)*?)\s+(?:Temple|Kovil)',
                r'(?:Lord|Sri|Shri)\s+(\w+(?:\s+\w+)*?)(?:\s+Temple)?',
            ]
            for pattern in deity_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                deity_names.extend(matches[:5])
            
            if deity_names:
                data["deities"] = list(dict.fromkeys(deity_names))[:10]
            
            # Extract timings
            timing_patterns = [
                r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))\s*(?:to|-)\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))',
                r'Opening Time.*?(\d{1,2}:\d{2}.*?)(?:Closing|<)',
            ]
            timings = []
            for pattern in timing_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    timings.extend([str(m) for m in matches[:5]])
            
            if timings:
                data["timings"] = timings
            
            # Extract image URLs (save for later download)
            image_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
            image_matches = re.findall(image_pattern, content, re.IGNORECASE)
            
            images = []
            for img_url in image_matches[:30]:  # Max 30 images
                # Skip common icons/logos
                if any(skip in img_url.lower() for skip in ['logo', 'icon', 'button', 'load.gif']):
                    continue
                
                # Make absolute URL
                if img_url.startswith('/'):
                    img_url = f"https://{url.split('/')[2]}{img_url}"
                elif not img_url.startswith('http'):
                    img_url = f"{'/'.join(url.split('/')[:3])}/{img_url}"
                
                images.append(img_url)
            
            if images:
                data["image_urls"] = images
                data["image_count"] = len(images)
            
            # Extract Tamil content
            tamil_pattern = re.compile(r'[\u0B80-\u0BFF]+[\u0B80-\u0BFF\s]*[\u0B80-\u0BFF]+')
            tamil_matches = tamil_pattern.findall(content)
            
            if tamil_matches:
                # Get unique Tamil phrases
                unique_tamil = list(dict.fromkeys(tamil_matches))[:30]
                data["tamil_content"] = {
                    "phrases": unique_tamil[:15],
                    "has_tamil": True
                }
            
            # Extract contact info
            phone_pattern = r'\b\d{10}\b|\b\d{5}[-\s]\d{5}\b'
            phones = re.findall(phone_pattern, content)
            if phones:
                data["contact_phones"] = list(dict.fromkeys(phones))[:3]
            
            # Extract festival mentions
            festival_keywords = ['festival', 'celebration', 'thiruvizha', 'utsavam', 'brahmotsavam']
            festival_mentions = []
            for keyword in festival_keywords:
                pattern = re.compile(rf'[^.]*{keyword}[^.]*', re.IGNORECASE)
                matches = pattern.findall(content)
                festival_mentions.extend(matches[:2])
            
            if festival_mentions:
                data["festival_mentions"] = list(dict.fromkeys(festival_mentions))[:5]
            
            # Mark as successful
            data["extraction_status"] = "success"
            
            return data
            
        except Exception as e:
            return {
                "temple_id": temple.get('id'),
                "temple_name": temple.get('temple_name'),
                "extraction_status": "error",
                "error": str(e)
            }
    
    def process_temple(self, temple):
        """Process a single temple - check for subdomain and extract data"""
        temple_id = temple.get('id')
        temple_name = temple.get('temple_name')
        district = temple.get('district')
        
        # Generate patterns to try
        patterns = self.generate_subdomain_patterns(temple_name, district)
        
        # Try each pattern
        for pattern in patterns:
            url = f"https://{pattern}.hrce.tn.gov.in/"
            
            if self.check_subdomain(url, quick_check=True):
                # Found subdomain! Extract data
                print(f"  ✓ Found: {temple_id} - {temple_name[:40]} -> {pattern}")
                
                temple_data = self.extract_temple_data(url, temple)
                temple_data["subdomain_pattern"] = pattern
                
                self.successful_temples.append(temple_id)
                return temple_data
        
        # No subdomain found
        self.failed_temples.append(temple_id)
        return {
            "temple_id": temple_id,
            "temple_name": temple_name,
            "district": district,
            "extraction_status": "no_subdomain"
        }
    
    def scrape_all_major_temples(self):
        """Main function to scrape all 578 major temples"""
        
        print("\n" + "="*60)
        print(" SCRAPING ALL 578 MAJOR TEMPLES")
        print("="*60)
        
        # Load major temples (income > 10 lakh)
        with open("../raw_data/tn_temples_full.json", "r", encoding="utf-8") as f:
            all_temples = json.load(f)
        
        # Filter major temples
        major_temples = [
            t for t in all_temples 
            if t.get('temple_12a_category') == '46_iii'
        ]
        
        print(f"\n📊 Found {len(major_temples)} major temples to process")
        
        # Process in batches for progress tracking
        batch_size = 50
        all_results = []
        
        start_time = time.time()
        
        for i in range(0, len(major_temples), batch_size):
            batch = major_temples[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(major_temples) + batch_size - 1) // batch_size
            
            print(f"\n📦 Processing Batch {batch_num}/{total_batches} ({len(batch)} temples)...")
            
            # Process batch with thread pool for speed
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(self.process_temple, temple): temple 
                          for temple in batch}
                
                for future in as_completed(futures):
                    temple = futures[future]
                    try:
                        result = future.result(timeout=30)
                        all_results.append(result)
                    except Exception as e:
                        print(f"  ❌ Error processing {temple.get('id')}: {e}")
                        all_results.append({
                            "temple_id": temple.get('id'),
                            "temple_name": temple.get('temple_name'),
                            "extraction_status": "error",
                            "error": str(e)
                        })
            
            # Progress update
            print(f"  Progress: {len(all_results)}/{len(major_temples)} temples processed")
            print(f"  Successful: {len(self.successful_temples)} | Failed: {len(self.failed_temples)}")
            
            # Save intermediate results
            if batch_num % 2 == 0:  # Every 100 temples
                self.save_results(all_results, intermediate=True)
            
            # Small delay between batches
            time.sleep(2)
        
        # Final save
        self.save_results(all_results, intermediate=False)
        
        elapsed_time = time.time() - start_time
        
        # Generate summary
        self.generate_summary(all_results, elapsed_time)
        
        return all_results
    
    def save_results(self, results, intermediate=False):
        """Save results to JSON files"""
        suffix = "_intermediate" if intermediate else "_final"
        
        # Save all results
        with open(f"major_temples_data/all_578_temples{suffix}.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Save only successful extractions
        successful = [r for r in results if r.get('extraction_status') == 'success']
        if successful:
            with open(f"major_temples_data/successful_temples{suffix}.json", "w", encoding="utf-8") as f:
                json.dump(successful, f, ensure_ascii=False, indent=2)
        
        print(f"  💾 Saved {len(results)} results ({len(successful)} successful)")
    
    def generate_summary(self, results, elapsed_time):
        """Generate detailed summary of scraping results"""
        
        successful = [r for r in results if r.get('extraction_status') == 'success']
        no_subdomain = [r for r in results if r.get('extraction_status') == 'no_subdomain']
        errors = [r for r in results if r.get('extraction_status') == 'error']
        
        # Analyze data coverage
        with_images = [r for r in successful if r.get('image_urls')]
        with_timings = [r for r in successful if r.get('timings')]
        with_deities = [r for r in successful if r.get('deities')]
        with_tamil = [r for r in successful if r.get('tamil_content')]
        with_festivals = [r for r in successful if r.get('festival_mentions')]
        with_contact = [r for r in successful if r.get('contact_phones')]
        
        summary = {
            "execution_time": f"{elapsed_time:.2f} seconds",
            "total_temples_processed": len(results),
            "successful_extractions": len(successful),
            "no_subdomain_found": len(no_subdomain),
            "errors": len(errors),
            "success_rate": f"{len(successful)/len(results)*100:.1f}%",
            
            "data_coverage": {
                "with_images": len(with_images),
                "with_timings": len(with_timings),
                "with_deities": len(with_deities),
                "with_tamil_content": len(with_tamil),
                "with_festivals": len(with_festivals),
                "with_contact": len(with_contact)
            },
            
            "image_statistics": {
                "total_image_urls": sum(len(r.get('image_urls', [])) for r in successful),
                "avg_images_per_temple": sum(len(r.get('image_urls', [])) for r in successful) / len(successful) if successful else 0
            },
            
            "district_coverage": {},
            "discovered_patterns": []
        }
        
        # District-wise analysis
        for result in successful:
            district = result.get('district', 'Unknown')
            if district not in summary['district_coverage']:
                summary['district_coverage'][district] = 0
            summary['district_coverage'][district] += 1
        
        # Collect unique subdomain patterns
        patterns = list(set(r.get('subdomain_pattern', '') for r in successful if r.get('subdomain_pattern')))
        summary['discovered_patterns'] = patterns[:20]
        
        # Save summary
        with open("major_temples_data/scraping_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print(" SCRAPING COMPLETE")
        print("="*60)
        
        print(f"\n📊 Final Results:")
        print(f"   Total Processed: {len(results)}")
        print(f"   ✅ Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
        print(f"   ❌ No Subdomain: {len(no_subdomain)}")
        print(f"   ⚠️ Errors: {len(errors)}")
        
        print(f"\n📈 Data Coverage (out of {len(successful)} successful):")
        print(f"   Images: {len(with_images)} temples")
        print(f"   Timings: {len(with_timings)} temples")
        print(f"   Deities: {len(with_deities)} temples")
        print(f"   Tamil Content: {len(with_tamil)} temples")
        print(f"   Festivals: {len(with_festivals)} temples")
        print(f"   Contact: {len(with_contact)} temples")
        
        print(f"\n⏱️ Time Taken: {elapsed_time:.2f} seconds ({elapsed_time/60:.1f} minutes)")
        
        print(f"\n📁 Output Files:")
        print(f"   1. major_temples_data/all_578_temples_final.json")
        print(f"   2. major_temples_data/successful_temples_final.json")
        print(f"   3. major_temples_data/scraping_summary.json")

def main():
    scraper = MajorTemplesScraper()
    results = scraper.scrape_all_major_temples()
    
    print("\n" + "="*60)
    print(" NEXT STEPS")
    print("="*60)
    print("\n1. Review successful_temples_final.json for quality")
    print("2. Update integrated dataset with new data")
    print("3. Download images separately if needed")
    print("4. Proceed with app development!")

if __name__ == "__main__":
    main()