#!/usr/bin/env python3
"""
Integrate New Data Sources into Unified Temple Dataset
Combines Wikipedia, Dinamalar, and recent HRCE scrapes
"""

import json
from pathlib import Path
from datetime import datetime
import re
from difflib import SequenceMatcher

class DataIntegrator:
    def __init__(self):
        # Load existing unified data
        print("📂 Loading existing unified dataset...")
        with open("../integrated_data/unified_temple_data.json", "r", encoding="utf-8") as f:
            self.unified_data = json.load(f)
        
        print(f"  Loaded {len(self.unified_data)} temples")
        
        # Statistics
        self.stats = {
            "total_temples": len(self.unified_data),
            "new_data_added": 0,
            "wikipedia_matches": 0,
            "dinamalar_matches": 0,
            "hrce_subdomain_matches": 0,
            "coordinates_added": 0,
            "deities_added": 0,
            "festivals_added": 0
        }
    
    def normalize_name(self, name):
        """Normalize temple name for matching"""
        if not name:
            return ""
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove common prefixes
        prefixes = ["arulmigu", "sri", "shri", "shree", "arulmiku"]
        for prefix in prefixes:
            name = name.replace(prefix + " ", "")
        
        # Remove common suffixes
        suffixes = ["temple", "kovil", "koil", "mandir", "devasthanam"]
        for suffix in suffixes:
            name = name.replace(" " + suffix, "")
        
        # Remove special characters
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # Remove extra spaces
        name = ' '.join(name.split())
        
        return name
    
    def find_matching_temple(self, name, location=None):
        """Find matching temple in unified dataset"""
        normalized_name = self.normalize_name(name)
        
        best_match = None
        best_score = 0
        
        for temple_id, temple in self.unified_data.items():
            # Compare names
            temple_name = self.normalize_name(temple.get("name", ""))
            score = SequenceMatcher(None, normalized_name, temple_name).ratio()
            
            # Boost score if location matches
            if location and temple.get("district"):
                if location.lower() in temple["district"].lower():
                    score += 0.2
            
            if score > best_score and score > 0.7:  # 70% similarity threshold
                best_score = score
                best_match = temple_id
        
        return best_match, best_score
    
    def integrate_wikipedia_data(self):
        """Integrate Wikipedia temple data"""
        print("\n📚 Integrating Wikipedia data...")
        
        wiki_file = Path("wikipedia_data/temple_details_final.json")
        if not wiki_file.exists():
            print("  ⚠️ Wikipedia data not found")
            return
        
        with open(wiki_file, "r", encoding="utf-8") as f:
            wiki_temples = json.load(f)
        
        print(f"  Processing {len(wiki_temples)} Wikipedia temples...")
        
        for wiki_temple in wiki_temples:
            # Try to find matching temple
            name = wiki_temple.get("title", "")
            location = wiki_temple.get("location") or wiki_temple.get("district")
            
            temple_id, score = self.find_matching_temple(name, location)
            
            if temple_id:
                print(f"  ✓ Matched: {name[:40]} -> {self.unified_data[temple_id]['name'][:40]} (score: {score:.2f})")
                
                # Add Wikipedia as a source
                if "sources" not in self.unified_data[temple_id]:
                    self.unified_data[temple_id]["sources"] = {}
                
                self.unified_data[temple_id]["sources"]["wikipedia"] = {
                    "title": wiki_temple.get("title"),
                    "lang": wiki_temple.get("lang"),
                    "pageid": wiki_temple.get("pageid"),
                    "wikidata_id": wiki_temple.get("wikidata_id")
                }
                
                # Add coordinates if available
                if wiki_temple.get("coordinates") and not self.unified_data[temple_id].get("coordinates"):
                    self.unified_data[temple_id]["coordinates"] = wiki_temple["coordinates"]
                    self.stats["coordinates_added"] += 1
                
                # Add deity if available
                if wiki_temple.get("deity"):
                    if not self.unified_data[temple_id].get("deities"):
                        self.unified_data[temple_id]["deities"] = []
                    
                    deity = wiki_temple["deity"]
                    if isinstance(deity, str):
                        deity = [d.strip() for d in deity.split(",")]
                    else:
                        deity = [deity]
                    
                    for d in deity:
                        if d and d not in self.unified_data[temple_id]["deities"]:
                            self.unified_data[temple_id]["deities"].append(d)
                            self.stats["deities_added"] += 1
                
                # Add festivals if available
                if wiki_temple.get("festivals"):
                    if not self.unified_data[temple_id].get("festivals"):
                        self.unified_data[temple_id]["festivals"] = []
                    
                    festivals = wiki_temple["festivals"]
                    if isinstance(festivals, str):
                        festivals = [festivals]
                    
                    for f in festivals:
                        if f and f not in self.unified_data[temple_id]["festivals"]:
                            self.unified_data[temple_id]["festivals"].append(f)
                            self.stats["festivals_added"] += 1
                
                # Add website if available
                if wiki_temple.get("website") and not self.unified_data[temple_id].get("website"):
                    self.unified_data[temple_id]["website"] = wiki_temple["website"]
                
                # Add image if available
                if wiki_temple.get("image_url"):
                    if not self.unified_data[temple_id].get("images"):
                        self.unified_data[temple_id]["images"] = []
                    
                    if wiki_temple["image_url"] not in self.unified_data[temple_id]["images"]:
                        self.unified_data[temple_id]["images"].append(wiki_temple["image_url"])
                
                self.stats["wikipedia_matches"] += 1
                self.stats["new_data_added"] += 1
            else:
                print(f"  ? No match for: {name[:40]}")
    
    def integrate_hrce_subdomain_data(self):
        """Integrate latest HRCE subdomain scrape data"""
        print("\n🏛️ Integrating HRCE subdomain data...")
        
        hrce_file = Path("major_temples_data/successful_temples_final.json")
        if not hrce_file.exists():
            print("  ⚠️ HRCE subdomain data not found")
            return
        
        with open(hrce_file, "r", encoding="utf-8") as f:
            hrce_temples = json.load(f)
        
        print(f"  Processing {len(hrce_temples)} HRCE subdomain temples...")
        
        for hrce_temple in hrce_temples:
            temple_id = hrce_temple.get("temple_id")
            
            if temple_id and temple_id in self.unified_data:
                print(f"  ✓ Updating: {hrce_temple['temple_name'][:40]}")
                
                # Add HRCE subdomain as a source
                if "sources" not in self.unified_data[temple_id]:
                    self.unified_data[temple_id]["sources"] = {}
                
                self.unified_data[temple_id]["sources"]["hrce_subdomain_latest"] = {
                    "subdomain_url": hrce_temple.get("subdomain_url"),
                    "extraction_timestamp": hrce_temple.get("extraction_timestamp")
                }
                
                # Add deities
                if hrce_temple.get("deities"):
                    if not self.unified_data[temple_id].get("deities"):
                        self.unified_data[temple_id]["deities"] = []
                    
                    for deity in hrce_temple["deities"]:
                        if deity not in self.unified_data[temple_id]["deities"]:
                            self.unified_data[temple_id]["deities"].append(deity)
                
                # Add Tamil content
                if hrce_temple.get("tamil_content"):
                    self.unified_data[temple_id]["tamil_content"] = hrce_temple["tamil_content"]
                
                # Add contact phones
                if hrce_temple.get("contact_phones"):
                    if not self.unified_data[temple_id].get("contact_info"):
                        self.unified_data[temple_id]["contact_info"] = {}
                    self.unified_data[temple_id]["contact_info"]["phones"] = hrce_temple["contact_phones"]
                
                # Add image URLs
                if hrce_temple.get("image_urls"):
                    if not self.unified_data[temple_id].get("images"):
                        self.unified_data[temple_id]["images"] = []
                    
                    for img in hrce_temple["image_urls"]:
                        if img not in self.unified_data[temple_id]["images"]:
                            self.unified_data[temple_id]["images"].append(img)
                
                self.stats["hrce_subdomain_matches"] += 1
                self.stats["new_data_added"] += 1
    
    def save_integrated_data(self):
        """Save the integrated dataset"""
        print("\n💾 Saving integrated dataset...")
        
        # Create backup of existing data
        backup_path = f"../integrated_data/unified_temple_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open("../integrated_data/unified_temple_data.json", "r", encoding="utf-8") as f:
            backup_data = json.load(f)
        
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Backup saved to {backup_path}")
        
        # Save updated data
        with open("../integrated_data/unified_temple_data_v2.json", "w", encoding="utf-8") as f:
            json.dump(self.unified_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Updated data saved to unified_temple_data_v2.json")
        
        # Update statistics
        enriched_count = sum(1 for t in self.unified_data.values() 
                           if t.get("deities") or t.get("timings") or t.get("festivals"))
        
        self.stats["temples_with_enriched_data"] = enriched_count
        
        # Save statistics
        with open("../integrated_data/integration_stats_v2.json", "w", encoding="utf-8") as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Statistics saved")
    
    def generate_summary(self):
        """Generate integration summary"""
        print("\n" + "="*60)
        print(" INTEGRATION COMPLETE")
        print("="*60)
        
        print(f"\n📊 Summary:")
        print(f"  Total temples: {self.stats['total_temples']}")
        print(f"  New data added to: {self.stats['new_data_added']} temples")
        print(f"  Wikipedia matches: {self.stats['wikipedia_matches']}")
        print(f"  HRCE subdomain matches: {self.stats['hrce_subdomain_matches']}")
        print(f"  Coordinates added: {self.stats['coordinates_added']}")
        print(f"  Deities added: {self.stats['deities_added']}")
        print(f"  Festivals added: {self.stats['festivals_added']}")
        
        if "temples_with_enriched_data" in self.stats:
            print(f"\n  Temples with enriched data: {self.stats['temples_with_enriched_data']}")
            print(f"  Enrichment rate: {self.stats['temples_with_enriched_data']/self.stats['total_temples']*100:.2f}%")
    
    def integrate_all(self):
        """Main integration function"""
        print("\n" + "="*60)
        print(" INTEGRATING NEW DATA SOURCES")
        print("="*60)
        
        # Integrate different sources
        self.integrate_wikipedia_data()
        self.integrate_hrce_subdomain_data()
        
        # Save integrated data
        self.save_integrated_data()
        
        # Generate summary
        self.generate_summary()

def main():
    integrator = DataIntegrator()
    integrator.integrate_all()
    
    print("\n✅ Next steps:")
    print("  1. Review unified_temple_data_v2.json")
    print("  2. Check enriched temples for quality")
    print("  3. Consider additional data sources if needed")
    print("  4. Start building the calendar app!")

if __name__ == "__main__":
    main()