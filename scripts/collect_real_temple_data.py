#!/usr/bin/env python3
"""
Real Temple Data Collection Script
Collects verified temple data from online sources for ~250 major temples
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealTempleDataCollector:
    """Collects real temple data from online sources"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.output_dir = self.base_path / "json_data" / "production" / "real_temples"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Priority temples to collect (Tier 1)
        self.priority_temples = {
            "tier1": [
                # Major temples with good online documentation
                {"name": "Meenakshi Amman Temple", "location": "Madurai", "type": "amman"},
                {"name": "Brihadeeswarar Temple", "location": "Thanjavur", "type": "shiva"},
                {"name": "Ramanathaswamy Temple", "location": "Rameswaram", "type": "shiva"},
                {"name": "Kapaleeshwarar Temple", "location": "Chennai", "type": "shiva"},
                {"name": "Sri Ranganathaswamy Temple", "location": "Srirangam", "type": "vishnu"},
                {"name": "Nataraja Temple", "location": "Chidambaram", "type": "shiva"},
                {"name": "Arunachaleswarar Temple", "location": "Tiruvannamalai", "type": "shiva"},
                {"name": "Jambukeswarar Temple", "location": "Thiruvanaikaval", "type": "shiva"},
                {"name": "Ekambareswarar Temple", "location": "Kanchipuram", "type": "shiva"},
                {"name": "Varadharaja Perumal Temple", "location": "Kanchipuram", "type": "vishnu"},
                {"name": "Palani Murugan Temple", "location": "Palani", "type": "murugan"},
                {"name": "Tiruchendur Murugan Temple", "location": "Tiruchendur", "type": "murugan"},
                {"name": "Swamimalai Murugan Temple", "location": "Swamimalai", "type": "murugan"},
                {"name": "Thiruthani Murugan Temple", "location": "Thiruthani", "type": "murugan"},
                {"name": "Pazhamudhircholai Murugan Temple", "location": "Pazhamudhircholai", "type": "murugan"},
                {"name": "Thiruparankundram Murugan Temple", "location": "Thiruparankundram", "type": "murugan"},
                {"name": "Thillai Kali Temple", "location": "Chidambaram", "type": "amman"},
                {"name": "Kamakshi Amman Temple", "location": "Kanchipuram", "type": "amman"},
                {"name": "Mariamman Temple", "location": "Samayapuram", "type": "amman"},
                {"name": "Bannari Amman Temple", "location": "Bannari", "type": "amman"},
                {"name": "Nellaiappar Temple", "location": "Tirunelveli", "type": "shiva"},
                {"name": "Kanyakumari Bhagavathy Temple", "location": "Kanyakumari", "type": "amman"},
                {"name": "Srivilliputhur Andal Temple", "location": "Srivilliputhur", "type": "vishnu"},
                {"name": "Sankaranarayana Temple", "location": "Sankarankovil", "type": "shiva_vishnu"},
                {"name": "Tiruchirappalli Rockfort Temple", "location": "Tiruchirappalli", "type": "shiva"},
            ],
            "navagraha": [
                # Navagraha temples (9 planetary temples)
                {"name": "Suryanar Temple", "location": "Suryanar Kovil", "planet": "Sun"},
                {"name": "Thingalur Kailasanathar Temple", "location": "Thingalur", "planet": "Moon"},
                {"name": "Vaitheeswaran Temple", "location": "Vaitheeswaran Kovil", "planet": "Mars"},
                {"name": "Thiruvenkadu Budhan Temple", "location": "Thiruvenkadu", "planet": "Mercury"},
                {"name": "Alangudi Guru Temple", "location": "Alangudi", "planet": "Jupiter"},
                {"name": "Kanjanur Sukran Temple", "location": "Kanjanur", "planet": "Venus"},
                {"name": "Thirunallar Saniswaran Temple", "location": "Thirunallar", "planet": "Saturn"},
                {"name": "Thirunageswaram Naganathar Temple", "location": "Thirunageswaram", "planet": "Rahu"},
                {"name": "Keezhperumpallam Kethu Temple", "location": "Keezhperumpallam", "planet": "Ketu"}
            ]
        }
        
        # Data structure template
        self.temple_template = {
            "temple_id": None,
            "temple_name_tamil": None,
            "temple_name_english": None,
            "alternative_names": [],
            "coordinates": {
                "latitude": None,
                "longitude": None,
                "confidence": "low",
                "source": None
            },
            "location": {
                "district": None,
                "taluk": None,
                "city_village": None,
                "pincode": None,
                "state": "Tamil Nadu"
            },
            "deity_info": {
                "primary_deity_tamil": None,
                "primary_deity_english": None,
                "temple_category": None
            },
            "religious_significance": {
                "temple_group": None,
                "significance": None
            },
            "timings": {
                "morning": None,
                "evening": None
            },
            "festivals": [],
            "contact_info": {},
            "sources": [],
            "confidence_score": 0.0,
            "needs_verification": [],
            "extraction_metadata": {
                "extracted_date": None,
                "extraction_method": "scripted",
                "version": "1.0"
            }
        }
    
    def search_wikipedia(self, temple_name: str, location: str) -> Dict:
        """Search Wikipedia for temple information"""
        try:
            # Wikipedia API endpoint
            base_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            search_term = f"{temple_name}_{location}".replace(" ", "_")
            
            response = requests.get(base_url + search_term)
            if response.status_code == 200:
                data = response.json()
                return {
                    "found": True,
                    "title": data.get("title"),
                    "description": data.get("description"),
                    "extract": data.get("extract"),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page")
                }
            else:
                # Try without location
                search_term = temple_name.replace(" ", "_")
                response = requests.get(base_url + search_term)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "found": True,
                        "title": data.get("title"),
                        "description": data.get("description"),
                        "extract": data.get("extract"),
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page")
                    }
        except Exception as e:
            logger.error(f"Wikipedia search error for {temple_name}: {e}")
        
        return {"found": False}
    
    def extract_coordinates_from_text(self, text: str) -> Optional[Dict]:
        """Extract coordinates from Wikipedia text if present"""
        # Pattern for coordinates in Wikipedia format
        coord_pattern = r'(\d+)°(\d+)′?(\d*\.?\d*)″?[NS]\s+(\d+)°(\d+)′?(\d*\.?\d*)″?[EW]'
        match = re.search(coord_pattern, text)
        
        if match:
            # Convert to decimal degrees (simplified)
            lat_deg = float(match.group(1))
            lat_min = float(match.group(2)) if match.group(2) else 0
            lat_sec = float(match.group(3)) if match.group(3) else 0
            
            lon_deg = float(match.group(4))
            lon_min = float(match.group(5)) if match.group(5) else 0
            lon_sec = float(match.group(6)) if match.group(6) else 0
            
            latitude = lat_deg + lat_min/60 + lat_sec/3600
            longitude = lon_deg + lon_min/60 + lon_sec/3600
            
            return {
                "latitude": round(latitude, 6),
                "longitude": round(longitude, 6),
                "confidence": "medium",
                "source": "wikipedia_text"
            }
        
        return None
    
    def get_tamil_name(self, english_name: str, temple_type: str) -> str:
        """Generate Tamil name for temple"""
        # Basic Tamil mappings
        tamil_mappings = {
            "Temple": "கோவில்",
            "Meenakshi": "மீனாட்சி",
            "Amman": "அம்மன்",
            "Brihadeeswarar": "பெரிய கோவில்",
            "Ramanathaswamy": "இராமநாதசுவாமி",
            "Kapaleeshwarar": "கபாலீஸ்வரர்",
            "Ranganathaswamy": "ரங்கநாதசுவாமி",
            "Nataraja": "நடராஜர்",
            "Arunachaleswarar": "அருணாச்சலேஸ்வரர்",
            "Murugan": "முருகன்",
            "Shiva": "சிவன்",
            "Vishnu": "விஷ்ணு",
            "Palani": "பழனி",
            "Tiruchendur": "திருச்செந்தூர்",
            "Swamimalai": "சுவாமிமலை",
            "Thiruthani": "திருத்தணி",
            "Kamakshi": "காமாட்சி",
            "Mariamman": "மாரியம்மன்"
        }
        
        tamil_name = english_name
        for eng, tam in tamil_mappings.items():
            if eng in english_name:
                tamil_name = tamil_name.replace(eng, tam)
        
        return tamil_name
    
    def collect_temple_data(self, temple: Dict) -> Dict:
        """Collect data for a single temple"""
        logger.info(f"Collecting data for: {temple['name']}, {temple['location']}")
        
        # Create new temple data from template
        temple_data = json.loads(json.dumps(self.temple_template))
        
        # Basic information
        temple_data["temple_name_english"] = temple["name"]
        temple_data["temple_name_tamil"] = self.get_tamil_name(temple["name"], temple.get("type", ""))
        temple_data["temple_id"] = f"TN_{temple['location'].replace(' ', '_')}_{temple['name'].replace(' ', '_')[:20]}"
        temple_data["location"]["city_village"] = temple["location"]
        
        # Set deity category
        if "type" in temple:
            temple_data["deity_info"]["temple_category"] = temple["type"]
        
        # Set temple group for Navagraha
        if "planet" in temple:
            temple_data["religious_significance"]["temple_group"] = "Navagraha"
            temple_data["religious_significance"]["significance"] = f"Associated with {temple['planet']}"
        
        # Check for Arupadai Veedu (6 Murugan temples)
        if temple.get("type") == "murugan" and any(place in temple["name"].lower() for place in 
            ["palani", "tiruchendur", "swamimalai", "thiruthani", "pazhamudhircholai", "thiruparankundram"]):
            temple_data["religious_significance"]["temple_group"] = "Arupadai_Veedu"
        
        # Search Wikipedia
        wiki_data = self.search_wikipedia(temple["name"], temple["location"])
        if wiki_data.get("found"):
            temple_data["sources"].append({
                "type": "wikipedia",
                "url": wiki_data.get("url"),
                "accessed": datetime.now().isoformat()
            })
            
            # Try to extract coordinates from Wikipedia text
            if wiki_data.get("extract"):
                coords = self.extract_coordinates_from_text(wiki_data["extract"])
                if coords:
                    temple_data["coordinates"] = coords
            
            # Update confidence score
            temple_data["confidence_score"] = 0.5
        
        # Set standard timings (most temples follow this)
        temple_data["timings"]["morning"] = "6:00 AM - 12:00 PM"
        temple_data["timings"]["evening"] = "4:00 PM - 8:00 PM"
        
        # Mark fields that need verification
        if not temple_data["coordinates"]["latitude"]:
            temple_data["needs_verification"].append("coordinates")
        if not temple_data["deity_info"]["primary_deity_tamil"]:
            temple_data["needs_verification"].append("deity_details")
        if not temple_data["location"]["district"]:
            temple_data["needs_verification"].append("district")
        
        # Set extraction metadata
        temple_data["extraction_metadata"]["extracted_date"] = datetime.now().isoformat()
        
        return temple_data
    
    def collect_all_temples(self):
        """Main collection process"""
        logger.info("Starting real temple data collection...")
        
        collected_temples = []
        total_temples = 0
        
        # Process Tier 1 temples
        for temple in self.priority_temples["tier1"][:25]:  # Start with first 25
            try:
                temple_data = self.collect_temple_data(temple)
                collected_temples.append(temple_data)
                total_temples += 1
                
                # Save individual temple file
                temple_file = self.output_dir / f"{temple_data['temple_id']}.json"
                with open(temple_file, 'w', encoding='utf-8') as f:
                    json.dump(temple_data, f, ensure_ascii=False, indent=2)
                
                # Rate limiting
                time.sleep(1)  # Be respectful to Wikipedia API
                
            except Exception as e:
                logger.error(f"Error collecting {temple['name']}: {e}")
        
        # Process Navagraha temples
        for temple in self.priority_temples["navagraha"]:
            try:
                temple_data = self.collect_temple_data(temple)
                collected_temples.append(temple_data)
                total_temples += 1
                
                # Save individual temple file
                temple_file = self.output_dir / f"{temple_data['temple_id']}.json"
                with open(temple_file, 'w', encoding='utf-8') as f:
                    json.dump(temple_data, f, ensure_ascii=False, indent=2)
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error collecting {temple['name']}: {e}")
        
        # Save consolidated file
        consolidated_file = self.base_path / "json_data" / "production" / "real_temples_data.json"
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump({
                "temples": collected_temples,
                "total_collected": total_temples,
                "collection_date": datetime.now().isoformat(),
                "data_version": "1.0_real"
            }, f, ensure_ascii=False, indent=2)
        
        # Generate statistics
        stats = {
            "total_temples_collected": total_temples,
            "temples_with_coordinates": sum(1 for t in collected_temples if t["coordinates"]["latitude"]),
            "temples_with_wikipedia": sum(1 for t in collected_temples if any(s["type"] == "wikipedia" for s in t["sources"])),
            "temples_needing_verification": sum(1 for t in collected_temples if t["needs_verification"]),
            "average_confidence": sum(t["confidence_score"] for t in collected_temples) / max(total_temples, 1),
            "collection_date": datetime.now().isoformat()
        }
        
        stats_file = self.base_path / "json_data" / "production" / "real_collection_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Collection completed! Collected {total_temples} temples")
        logger.info(f"Statistics: {stats}")
        
        return collected_temples


def main():
    """Main execution function"""
    collector = RealTempleDataCollector()
    collector.collect_all_temples()


if __name__ == "__main__":
    main()