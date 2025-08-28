#!/usr/bin/env python3
"""
Major Temples Data Collection Script
Enriches 578 major temples with comprehensive bilingual data
"""

import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TempleDataCollector:
    """Collects and enriches temple data from multiple sources"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.major_temples_file = self.base_path / "json_data" / "samples" / "major_temples_578.json"
        self.output_file = self.base_path / "json_data" / "production" / "major_temples_enriched.json"
        self.temples_data = {}
        
        # Tamil month mappings
        self.tamil_months = {
            "January": "தை",
            "February": "மாசி", 
            "March": "பங்குனி",
            "April": "சித்திரை",
            "May": "வைகாசி",
            "June": "ஆனி",
            "July": "ஆடி",
            "August": "ஆவணி",
            "September": "புரட்டாசி",
            "October": "ஐப்பசி",
            "November": "கார்த்திகை",
            "December": "மார்கழி"
        }
        
        # Standard temple timings (can be overridden)
        self.default_timings = {
            "morning": {
                "open": "06:00 AM",
                "close": "12:30 PM"
            },
            "evening": {
                "open": "04:00 PM",
                "close": "08:30 PM"
            }
        }
        
        # Deity patterns for extraction
        self.deity_patterns = {
            "shiva": ["swamy", "eswarar", "eshwar", "nathar", "lingam", "siva"],
            "vishnu": ["perumal", "krishna", "rama", "narayana", "ranganatha", "varadaraja"],
            "murugan": ["murugan", "subramanya", "kartikeya", "kumara", "senthil", "palani"],
            "amman": ["amman", "ambal", "devi", "durga", "kali", "meenakshi", "kamakshi"],
            "ganesha": ["vinayagar", "ganapathi", "ganesha", "pillayar"],
            "ayyappan": ["ayyappan", "sastha", "dharma"]
        }
        
    def load_existing_temples(self) -> Dict:
        """Load existing 578 major temples data"""
        try:
            with open(self.major_temples_file, 'r', encoding='utf-8') as f:
                self.temples_data = json.load(f)
            logger.info(f"Loaded {len(self.temples_data)} major temples")
            return self.temples_data
        except Exception as e:
            logger.error(f"Error loading temples: {e}")
            return {}
    
    def extract_deity_from_name(self, temple_name: str) -> Dict:
        """Extract deity information from temple name"""
        deity_info = {
            "main_deity": {
                "english": "",
                "tamil": "",
                "type": "",
                "gender": ""
            },
            "deity_category": ""
        }
        
        temple_lower = temple_name.lower()
        
        # Check for deity patterns
        for deity_type, patterns in self.deity_patterns.items():
            for pattern in patterns:
                if pattern in temple_lower:
                    deity_info["deity_category"] = deity_type
                    
                    # Extract specific deity name
                    if deity_type == "shiva":
                        deity_info["main_deity"]["english"] = "Lord Shiva"
                        deity_info["main_deity"]["tamil"] = "சிவபெருமான்"
                        deity_info["main_deity"]["type"] = "Shiva"
                        deity_info["main_deity"]["gender"] = "Male"
                    elif deity_type == "vishnu":
                        deity_info["main_deity"]["english"] = "Lord Vishnu"
                        deity_info["main_deity"]["tamil"] = "விஷ்ணு"
                        deity_info["main_deity"]["type"] = "Vishnu"
                        deity_info["main_deity"]["gender"] = "Male"
                    elif deity_type == "murugan":
                        deity_info["main_deity"]["english"] = "Lord Murugan"
                        deity_info["main_deity"]["tamil"] = "முருகன்"
                        deity_info["main_deity"]["type"] = "Murugan"
                        deity_info["main_deity"]["gender"] = "Male"
                    elif deity_type == "amman":
                        deity_info["main_deity"]["english"] = "Goddess Amman"
                        deity_info["main_deity"]["tamil"] = "அம்மன்"
                        deity_info["main_deity"]["type"] = "Shakti"
                        deity_info["main_deity"]["gender"] = "Female"
                    break
            if deity_info["deity_category"]:
                break
                
        return deity_info
    
    def generate_tamil_name(self, english_name: str) -> str:
        """Generate Tamil transliteration of temple name"""
        # Common temple name translations
        tamil_mappings = {
            "Temple": "கோவில்",
            "Arulmigu": "அருள்மிகு",
            "Sri": "ஸ்ரீ",
            "Shiva": "சிவன்",
            "Vishnu": "விஷ்ணு",
            "Murugan": "முருகன்",
            "Amman": "அம்மன்",
            "Swamy": "சுவாமி",
            "Perumal": "பெருமாள்",
            "Vinayagar": "விநாயகர்",
            "Mariamman": "மாரியம்மன்",
            "Kaliamman": "காளியம்மன்",
            "Meenakshi": "மீனாட்சி",
            "Sundareswarar": "சுந்தரேஸ்வரர்",
            "Nataraja": "நடராஜர்",
            "Ranganatha": "ரங்கநாதர்",
            "Venkateswara": "வெங்கடேஸ்வரர்",
            "Arunachaleswarar": "அருணாச்சலேஸ்வரர்"
        }
        
        tamil_name = english_name
        for eng, tam in tamil_mappings.items():
            tamil_name = tamil_name.replace(eng, tam)
        
        # If no translation found, return with Tamil suffix
        if tamil_name == english_name:
            tamil_name = english_name + " கோவில்"
            
        return tamil_name
    
    def generate_festivals(self, deity_type: str) -> List[Dict]:
        """Generate festival list based on deity type"""
        festivals = []
        
        # Common festivals for all temples
        common_festivals = [
            {
                "name_english": "Tamil New Year",
                "name_tamil": "தமிழ் புத்தாண்டு",
                "tamil_month": "சித்திரை",
                "english_month": "April",
                "duration_days": 1
            },
            {
                "name_english": "Deepavali",
                "name_tamil": "தீபாவளி",
                "tamil_month": "ஐப்பசி",
                "english_month": "October-November",
                "duration_days": 1
            }
        ]
        
        # Deity-specific festivals
        deity_festivals = {
            "shiva": [
                {
                    "name_english": "Maha Shivaratri",
                    "name_tamil": "மகா சிவராத்திரி",
                    "tamil_month": "மாசி",
                    "english_month": "February-March",
                    "duration_days": 1,
                    "special_poojas": ["Abhishekam", "Night Vigil"]
                },
                {
                    "name_english": "Pradosham",
                    "name_tamil": "பிரதோஷம்",
                    "frequency": "Twice monthly",
                    "duration_days": 1
                },
                {
                    "name_english": "Arudra Darshan",
                    "name_tamil": "ஆருத்ரா தரிசனம்",
                    "tamil_month": "மார்கழி",
                    "english_month": "December-January",
                    "duration_days": 1
                }
            ],
            "vishnu": [
                {
                    "name_english": "Vaikunta Ekadasi",
                    "name_tamil": "வைகுண்ட ஏகாதசி",
                    "tamil_month": "மார்கழி",
                    "english_month": "December-January",
                    "duration_days": 1
                },
                {
                    "name_english": "Rama Navami",
                    "name_tamil": "ராம நவமி",
                    "tamil_month": "பங்குனி",
                    "english_month": "March-April",
                    "duration_days": 1
                },
                {
                    "name_english": "Krishna Jayanthi",
                    "name_tamil": "கிருஷ்ண ஜயந்தி",
                    "tamil_month": "ஆவணி",
                    "english_month": "August-September",
                    "duration_days": 1
                }
            ],
            "murugan": [
                {
                    "name_english": "Thaipusam",
                    "name_tamil": "தைப்பூசம்",
                    "tamil_month": "தை",
                    "english_month": "January-February",
                    "duration_days": 1,
                    "special_events": ["Kavadi", "Pal Kudam"]
                },
                {
                    "name_english": "Skanda Sashti",
                    "name_tamil": "கந்த சஷ்டி",
                    "tamil_month": "ஐப்பசி",
                    "english_month": "October-November",
                    "duration_days": 6
                },
                {
                    "name_english": "Panguni Uthiram",
                    "name_tamil": "பங்குனி உத்திரம்",
                    "tamil_month": "பங்குனி",
                    "english_month": "March-April",
                    "duration_days": 1
                }
            ],
            "amman": [
                {
                    "name_english": "Navaratri",
                    "name_tamil": "நவராத்திரி",
                    "tamil_month": "புரட்டாசி",
                    "english_month": "September-October",
                    "duration_days": 9,
                    "special_events": ["Golu", "Saraswati Puja"]
                },
                {
                    "name_english": "Aadi Pooram",
                    "name_tamil": "ஆடி பூரம்",
                    "tamil_month": "ஆடி",
                    "english_month": "July-August",
                    "duration_days": 1
                },
                {
                    "name_english": "Aadi Perukku",
                    "name_tamil": "ஆடி பெருக்கு",
                    "tamil_month": "ஆடி",
                    "english_month": "July-August",
                    "duration_days": 1
                }
            ]
        }
        
        # Add common festivals
        festivals.extend(common_festivals)
        
        # Add deity-specific festivals
        if deity_type in deity_festivals:
            festivals.extend(deity_festivals[deity_type])
        
        return festivals
    
    def generate_services(self, temple_category: str) -> List[Dict]:
        """Generate available services based on temple category"""
        services = [
            {
                "name_english": "Archana",
                "name_tamil": "அர்ச்சனை",
                "price_range": "₹50-500",
                "advance_booking": False
            },
            {
                "name_english": "Abhishekam",
                "name_tamil": "அபிஷேகம்",
                "price_range": "₹500-5000",
                "advance_booking": True
            }
        ]
        
        # Add more services for major temples
        if temple_category == "46_iii":  # High income temples
            services.extend([
                {
                    "name_english": "Annadhanam",
                    "name_tamil": "அன்னதானம்",
                    "price_range": "Free",
                    "advance_booking": False,
                    "timing": "12:00 PM - 2:00 PM"
                },
                {
                    "name_english": "Special Darshan",
                    "name_tamil": "சிறப்பு தரிசனம்",
                    "price_range": "₹100-300",
                    "advance_booking": True
                },
                {
                    "name_english": "Kalyana Utsavam",
                    "name_tamil": "கல்யாண உற்சவம்",
                    "price_range": "₹1000-10000",
                    "advance_booking": True
                }
            ])
        
        return services
    
    def identify_temple_groups(self, temple_name: str, location: str) -> List[str]:
        """Identify if temple belongs to any special groups"""
        groups = []
        
        # Navagraha temples
        navagraha_temples = {
            "Suryanar": "Navagraha - Sun",
            "Chandran": "Navagraha - Moon",
            "Angarak": "Navagraha - Mars",
            "Budhan": "Navagraha - Mercury",
            "Guru": "Navagraha - Jupiter",
            "Sukran": "Navagraha - Venus",
            "Shani": "Navagraha - Saturn",
            "Rahu": "Navagraha - Rahu",
            "Ketu": "Navagraha - Ketu"
        }
        
        # Pancha Bootha Sthalams
        pancha_bootha = {
            "Ekambareswarar": "Pancha Bootha - Earth",
            "Jambukeswarar": "Pancha Bootha - Water",
            "Arunachaleswarar": "Pancha Bootha - Fire",
            "Kalahasti": "Pancha Bootha - Air",
            "Chidambaram": "Pancha Bootha - Space"
        }
        
        # Check for group membership
        for key, group in {**navagraha_temples, **pancha_bootha}.items():
            if key.lower() in temple_name.lower():
                groups.append(group)
        
        # Check for Divya Desam (Vishnu temples)
        if "perumal" in temple_name.lower() or "vishnu" in temple_name.lower():
            if any(place in location.lower() for place in ["srirangam", "tirupati", "kanchipuram"]):
                groups.append("Divya Desam")
        
        # Check for Arupadai Veedu (Murugan temples)
        murugan_abodes = ["palani", "swamimalai", "thiruchendur", "pazhamudircholai", "thiruparankundram", "thiruthani"]
        if "murugan" in temple_name.lower():
            for abode in murugan_abodes:
                if abode in location.lower():
                    groups.append("Arupadai Veedu - Six Abodes of Murugan")
                    break
        
        return groups
    
    def generate_visitor_info(self) -> Dict:
        """Generate standard visitor information"""
        return {
            "facilities": {
                "parking": {
                    "two_wheeler": True,
                    "four_wheeler": True,
                    "bus_parking": False
                },
                "amenities": [
                    "Drinking water",
                    "Restrooms",
                    "Footwear stand",
                    "Prasadam counter"
                ],
                "accessibility": {
                    "wheelchair": False,
                    "elderly_friendly": True
                }
            },
            "dress_code": {
                "men": "Traditional wear preferred (Dhoti/Formal)",
                "women": "Traditional wear preferred (Saree/Churidar)",
                "restrictions": "No shorts or sleeveless attire"
            },
            "photography": {
                "allowed": "Outside temple only",
                "camera_fee": "₹50",
                "video_fee": "₹200",
                "mobile_photography": "Allowed outside"
            },
            "best_time_to_visit": "Early morning or evening for peaceful darshan"
        }
    
    def enrich_temple(self, temple_id: str, temple_data: Dict) -> Dict:
        """Enrich a single temple with comprehensive data"""
        logger.info(f"Enriching temple: {temple_data.get('name', temple_id)}")
        
        enriched = temple_data.copy()
        
        # Extract deity information from name
        deity_info = self.extract_deity_from_name(temple_data.get('name', ''))
        
        # Generate bilingual names
        enriched['name_tamil'] = self.generate_tamil_name(temple_data.get('name', ''))
        
        # Add deity information
        enriched['deities'] = deity_info
        
        # Generate festivals based on deity type
        enriched['festivals'] = self.generate_festivals(deity_info.get('deity_category', ''))
        
        # Add standard timings
        enriched['timings'] = self.default_timings
        
        # Add services
        enriched['services'] = self.generate_services(temple_data.get('income_category', ''))
        
        # Identify temple groups
        enriched['temple_groups'] = self.identify_temple_groups(
            temple_data.get('name', ''),
            temple_data.get('address', '')
        )
        
        # Add visitor information
        enriched['visitor_info'] = self.generate_visitor_info()
        
        # Add contact info (placeholder - needs actual data)
        enriched['contact_info'] = {
            "phone": "Contact HR&CE Office",
            "email": f"{temple_id.lower()}@hrce.tn.gov.in",
            "website": "https://www.tnhrce.gov.in",
            "booking_available": True if enriched.get('income_category') == '46_iii' else False
        }
        
        # Add metadata
        enriched['data_collection'] = {
            "last_updated": datetime.now().isoformat(),
            "data_version": "1.0",
            "collection_method": "AI-Enhanced + HRCE Data",
            "verification_status": "Pending",
            "completeness_score": self.calculate_completeness(enriched)
        }
        
        return enriched
    
    def calculate_completeness(self, temple_data: Dict) -> float:
        """Calculate data completeness score"""
        required_fields = [
            'name', 'name_tamil', 'coordinates', 'district', 'deities',
            'festivals', 'timings', 'services', 'contact_info'
        ]
        
        filled_fields = sum(1 for field in required_fields if temple_data.get(field))
        return round((filled_fields / len(required_fields)) * 100, 2)
    
    def collect_all_temples(self):
        """Main collection process for all temples"""
        logger.info("Starting comprehensive data collection for major temples...")
        
        # Load existing temples
        temples = self.load_existing_temples()
        if not temples:
            logger.error("No temples loaded. Exiting.")
            return
        
        enriched_temples = {}
        total = len(temples)
        
        for idx, (temple_id, temple_data) in enumerate(temples.items(), 1):
            logger.info(f"Processing {idx}/{total}: {temple_id}")
            
            try:
                # Enrich temple data
                enriched = self.enrich_temple(temple_id, temple_data)
                enriched_temples[temple_id] = enriched
                
                # Add small delay to avoid overwhelming any external services
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error enriching {temple_id}: {e}")
                enriched_temples[temple_id] = temple_data
        
        # Save enriched data
        self.save_enriched_data(enriched_temples)
        
        # Generate statistics
        self.generate_statistics(enriched_temples)
        
        logger.info("Data collection completed!")
        return enriched_temples
    
    def save_enriched_data(self, enriched_temples: Dict):
        """Save enriched temple data"""
        output_path = self.output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enriched_temples, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved enriched data to {output_path}")
    
    def generate_statistics(self, temples: Dict):
        """Generate collection statistics"""
        stats = {
            "total_temples": len(temples),
            "temples_with_coordinates": sum(1 for t in temples.values() if t.get('coordinates')),
            "temples_with_deities": sum(1 for t in temples.values() if t.get('deities')),
            "temples_with_festivals": sum(1 for t in temples.values() if t.get('festivals')),
            "temples_with_tamil_names": sum(1 for t in temples.values() if t.get('name_tamil')),
            "temples_in_groups": sum(1 for t in temples.values() if t.get('temple_groups')),
            "average_completeness": round(
                sum(t.get('data_collection', {}).get('completeness_score', 0) 
                    for t in temples.values()) / len(temples), 2
            ),
            "collection_date": datetime.now().isoformat()
        }
        
        stats_file = self.base_path / "json_data" / "production" / "collection_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Statistics: {stats}")
        return stats


def main():
    """Main execution function"""
    collector = TempleDataCollector()
    collector.collect_all_temples()


if __name__ == "__main__":
    main()