#!/usr/bin/env python3
"""
Fetch Temple Data from Tamil & English Wikipedia APIs
Plus Wikidata SPARQL queries for structured data
"""

import requests
import json
import time
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import unquote

class WikipediaTempleFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "TempleCalendarApp/1.0 (Tamil Nadu Temple Data Collection)"
        })
        
        Path("wikipedia_data").mkdir(exist_ok=True)
        
        # API endpoints
        self.ta_wiki_api = "https://ta.wikipedia.org/w/api.php"
        self.en_wiki_api = "https://en.wikipedia.org/w/api.php"
        self.wikidata_api = "https://www.wikidata.org/w/api.php"
        self.wikidata_sparql = "https://query.wikidata.org/sparql"
        
        self.temples = []
        self.temple_details = []
        
    def fetch_tamil_temple_list(self):
        """Fetch list of temples from Tamil Wikipedia category"""
        print("\n📚 Fetching Tamil Wikipedia temple list...")
        
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": "Category:தமிழ்நாட்டுக் கோயில்கள்",  # Tamil Nadu temples
            "cmlimit": 500,
            "format": "json",
            "cmtype": "page"
        }
        
        temples = []
        continue_token = None
        
        while True:
            if continue_token:
                params["cmcontinue"] = continue_token
            
            try:
                resp = self.session.get(self.ta_wiki_api, params=params)
                data = resp.json()
                
                if "query" in data and "categorymembers" in data["query"]:
                    for member in data["query"]["categorymembers"]:
                        temples.append({
                            "pageid": member["pageid"],
                            "title_ta": member["title"],
                            "source": "ta.wikipedia"
                        })
                
                # Check for continuation
                if "continue" in data:
                    continue_token = data["continue"]["cmcontinue"]
                    print(f"  Fetched {len(temples)} temples so far...")
                    time.sleep(0.5)
                else:
                    break
                    
            except Exception as e:
                print(f"  Error fetching category members: {e}")
                break
        
        print(f"  ✓ Found {len(temples)} temples in Tamil Wikipedia")
        return temples
    
    def fetch_page_details(self, page_title, lang="ta"):
        """Fetch detailed information from a Wikipedia page"""
        api_url = self.ta_wiki_api if lang == "ta" else self.en_wiki_api
        
        # First, get the page content and wikidata item
        params = {
            "action": "query",
            "titles": page_title,
            "prop": "revisions|pageprops|coordinates|langlinks",
            "rvprop": "content",
            "rvslots": "main",
            "lllang": "en" if lang == "ta" else "ta",
            "format": "json"
        }
        
        try:
            resp = self.session.get(api_url, params=params)
            data = resp.json()
            
            pages = data.get("query", {}).get("pages", {})
            for pageid, page_data in pages.items():
                if pageid == "-1":  # Page doesn't exist
                    continue
                
                details = {
                    "title": page_title,
                    "pageid": pageid,
                    "lang": lang
                }
                
                # Get Wikidata ID
                if "pageprops" in page_data:
                    details["wikidata_id"] = page_data["pageprops"].get("wikibase_item")
                
                # Get coordinates
                if "coordinates" in page_data:
                    coords = page_data["coordinates"][0]
                    details["coordinates"] = {
                        "lat": coords.get("lat"),
                        "lon": coords.get("lon")
                    }
                
                # Get language links
                if "langlinks" in page_data:
                    for link in page_data["langlinks"]:
                        if link["lang"] == ("en" if lang == "ta" else "ta"):
                            details["linked_title"] = link["*"]
                
                # Parse infobox from content
                if "revisions" in page_data:
                    content = page_data["revisions"][0]["slots"]["main"]["*"]
                    details.update(self.parse_infobox(content, lang))
                
                return details
                
        except Exception as e:
            print(f"    Error fetching page details: {e}")
            return None
    
    def parse_infobox(self, content, lang="ta"):
        """Extract information from Wikipedia infobox"""
        info = {}
        
        # Tamil patterns
        if lang == "ta":
            patterns = {
                "deity": [r"கடவுள்\s*=\s*([^\n|]+)", r"மூலவர்\s*=\s*([^\n|]+)"],
                "location": [r"இடம்\s*=\s*([^\n|]+)", r"முகவரி\s*=\s*([^\n|]+)"],
                "district": [r"மாவட்டம்\s*=\s*([^\n|]+)"],
                "festivals": [r"திருவிழா\s*=\s*([^\n|]+)", r"விழா\s*=\s*([^\n|]+)"],
                "architecture": [r"கட்டிடக்கலை\s*=\s*([^\n|]+)"],
                "built_by": [r"கட்டியவர்\s*=\s*([^\n|]+)"],
            }
        else:  # English
            patterns = {
                "deity": [r"deity\s*=\s*([^\n|]+)", r"primary_deity\s*=\s*([^\n|]+)"],
                "location": [r"location\s*=\s*([^\n|]+)", r"address\s*=\s*([^\n|]+)"],
                "district": [r"district\s*=\s*([^\n|]+)"],
                "festivals": [r"festivals\s*=\s*([^\n|]+)"],
                "architecture": [r"architecture\s*=\s*([^\n|]+)"],
                "built_by": [r"creator\s*=\s*([^\n|]+)", r"built_by\s*=\s*([^\n|]+)"],
                "year_completed": [r"year_completed\s*=\s*([^\n|]+)"],
            }
        
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    # Clean up the value
                    value = match.group(1).strip()
                    value = re.sub(r'\[\[([^|\]]+)\|?[^\]]*\]\]', r'\1', value)  # Remove wiki links
                    value = re.sub(r'<[^>]+>', '', value)  # Remove HTML tags
                    info[field] = value
                    break
        
        return info
    
    def fetch_wikidata_details(self, wikidata_id):
        """Fetch structured data from Wikidata SPARQL"""
        if not wikidata_id:
            return {}
        
        query = f"""
        SELECT ?coords ?phone ?website ?image ?inception WHERE {{
          OPTIONAL {{ wd:{wikidata_id} wdt:P625 ?coords. }}
          OPTIONAL {{ wd:{wikidata_id} wdt:P1329 ?phone. }}
          OPTIONAL {{ wd:{wikidata_id} wdt:P856 ?website. }}
          OPTIONAL {{ wd:{wikidata_id} wdt:P18 ?image. }}
          OPTIONAL {{ wd:{wikidata_id} wdt:P571 ?inception. }}
        }}
        """
        
        try:
            resp = self.session.get(self.wikidata_sparql, 
                                   params={"query": query, "format": "json"})
            data = resp.json()
            
            if data["results"]["bindings"]:
                result = data["results"]["bindings"][0]
                details = {}
                
                if "coords" in result:
                    # Parse coordinate string
                    coord_str = result["coords"]["value"]
                    match = re.search(r'Point\(([-\d.]+) ([-\d.]+)\)', coord_str)
                    if match:
                        details["coordinates"] = {
                            "lon": float(match.group(1)),
                            "lat": float(match.group(2))
                        }
                
                if "phone" in result:
                    details["phone"] = result["phone"]["value"]
                
                if "website" in result:
                    details["website"] = result["website"]["value"]
                
                if "image" in result:
                    details["image_url"] = result["image"]["value"]
                
                if "inception" in result:
                    details["year_established"] = result["inception"]["value"][:4]
                
                return details
                
        except Exception as e:
            print(f"    Error fetching Wikidata: {e}")
            return {}
    
    def process_temples(self, limit=100):
        """Process temples to get full details"""
        print(f"\n📖 Processing first {limit} temples for details...")
        
        for i, temple in enumerate(self.temples[:limit]):
            if i % 10 == 0:
                print(f"  Progress: {i}/{limit} temples...")
            
            # Check which type of page we have
            if "title_ta" in temple:
                # Get Tamil Wikipedia details
                ta_details = self.fetch_page_details(temple["title_ta"], lang="ta")
            elif "title_en" in temple:
                # Get English Wikipedia details
                ta_details = self.fetch_page_details(temple["title_en"], lang="en")
            else:
                continue
            
            if ta_details:
                temple.update(ta_details)
                
                # Get English Wikipedia details if linked
                if "linked_title" in ta_details:
                    en_details = self.fetch_page_details(ta_details["linked_title"], lang="en")
                    if en_details:
                        # Merge English details
                        for key, value in en_details.items():
                            if key not in temple or not temple[key]:
                                temple[key] = value
                
                # Get Wikidata details
                if "wikidata_id" in ta_details:
                    wd_details = self.fetch_wikidata_details(ta_details["wikidata_id"])
                    temple.update(wd_details)
                
                self.temple_details.append(temple)
            
            time.sleep(0.5)  # Be respectful to APIs
            
            # Save progress every 20 temples
            if (i + 1) % 20 == 0:
                self.save_progress()
        
        self.save_progress(final=True)
        return self.temple_details
    
    def save_progress(self, final=False):
        """Save fetched data"""
        suffix = "_final" if final else "_progress"
        
        with open(f"wikipedia_data/temple_details{suffix}.json", "w", encoding="utf-8") as f:
            json.dump(self.temple_details, f, ensure_ascii=False, indent=2)
        
        print(f"  💾 Saved {len(self.temple_details)} temple details")
    
    def fetch_english_temple_list(self):
        """Fetch list of temples from English Wikipedia category"""
        print("\n📚 Fetching English Wikipedia temple list...")
        
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": "Category:Hindu_temples_in_Tamil_Nadu",
            "cmlimit": 500,
            "format": "json",
            "cmtype": "page"
        }
        
        temples = []
        continue_token = None
        
        while True:
            if continue_token:
                params["cmcontinue"] = continue_token
            
            try:
                resp = self.session.get(self.en_wiki_api, params=params)
                data = resp.json()
                
                if "query" in data and "categorymembers" in data["query"]:
                    for member in data["query"]["categorymembers"]:
                        temples.append({
                            "pageid": member["pageid"],
                            "title_en": member["title"],
                            "source": "en.wikipedia"
                        })
                
                # Check for continuation
                if "continue" in data:
                    continue_token = data["continue"]["cmcontinue"]
                    print(f"  Fetched {len(temples)} temples so far...")
                    time.sleep(0.5)
                else:
                    break
                    
            except Exception as e:
                print(f"  Error fetching category members: {e}")
                break
        
        print(f"  ✓ Found {len(temples)} temples in English Wikipedia")
        return temples
    
    def fetch_all(self):
        """Main function to fetch all temple data"""
        print("\n" + "="*60)
        print(" FETCHING WIKIPEDIA TEMPLE DATA")
        print("="*60)
        
        # Step 1: Get Tamil Wikipedia temple list
        ta_temples = self.fetch_tamil_temple_list()
        
        # Step 2: Get English Wikipedia temple list
        en_temples = self.fetch_english_temple_list()
        
        # Combine both lists
        self.temples = ta_temples + en_temples
        print(f"\n📊 Total temples from both sources: {len(self.temples)}")
        
        # Save temple list
        with open("wikipedia_data/temple_list.json", "w", encoding="utf-8") as f:
            json.dump(self.temples, f, ensure_ascii=False, indent=2)
        
        # Step 3: Process temples for details
        self.process_temples(limit=50)  # Start with 50 for testing
        
        # Generate summary
        self.generate_summary()
        
        return self.temple_details
    
    def generate_summary(self):
        """Generate summary of fetched data"""
        summary = {
            "total_temples_found": len(self.temples),
            "details_fetched": len(self.temple_details),
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Analyze data coverage
        has_coords = sum(1 for t in self.temple_details if "coordinates" in t)
        has_deity = sum(1 for t in self.temple_details if "deity" in t)
        has_location = sum(1 for t in self.temple_details if "location" in t)
        has_festivals = sum(1 for t in self.temple_details if "festivals" in t)
        has_image = sum(1 for t in self.temple_details if "image_url" in t)
        has_english = sum(1 for t in self.temple_details if "linked_title" in t)
        has_wikidata = sum(1 for t in self.temple_details if "wikidata_id" in t)
        
        summary["data_coverage"] = {
            "with_coordinates": has_coords,
            "with_deity": has_deity,
            "with_location": has_location,
            "with_festivals": has_festivals,
            "with_image": has_image,
            "with_english_page": has_english,
            "with_wikidata": has_wikidata
        }
        
        with open("wikipedia_data/fetch_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*60)
        print(" FETCHING COMPLETE")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  Total temples in category: {summary['total_temples_found']}")
        print(f"  Details fetched: {summary['details_fetched']}")
        print(f"  With coordinates: {has_coords}")
        print(f"  With deity info: {has_deity}")
        print(f"  With location: {has_location}")
        print(f"  With festivals: {has_festivals}")
        print(f"  With images: {has_image}")
        print(f"  With English page: {has_english}")
        print(f"  With Wikidata: {has_wikidata}")
        
        return summary

def main():
    fetcher = WikipediaTempleFetcher()
    temples = fetcher.fetch_all()
    
    print("\n✅ Next steps:")
    print("  1. Review temple_details_final.json")
    print("  2. Match with existing temple database")
    print("  3. Fetch remaining temples if needed")
    print("  4. Query Google Places API for opening hours")

if __name__ == "__main__":
    main()