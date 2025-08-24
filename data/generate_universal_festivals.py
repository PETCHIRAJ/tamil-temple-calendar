#!/usr/bin/env python3
"""
Generate Universal Festival Data
Creates separated JSON files for festivals that don't depend on specific temples
"""

import json
import swisseph as swe
from datetime import datetime, timedelta
from pathlib import Path
import math

# Import our existing calculator functions
from temple_calendar_calculator import (
    init_ephemeris,
    calculate_sun_position,
    calculate_moon_position,
    calculate_tithi,
    get_nakshatra,
    tamil_months,
    get_tamil_date
)

class UniversalFestivalGenerator:
    def __init__(self, year=2025):
        self.year = year
        init_ephemeris()
        Path("../festivals").mkdir(exist_ok=True)
        
        # Standard location for calculations (Tamil Nadu center)
        self.latitude = 10.7905  # Tamil Nadu approximate center
        self.longitude = 78.7047
        
    def calculate_all_tithis(self):
        """Calculate all tithi-based festivals for the year"""
        festivals = {
            "pradosham": [],
            "ekadashi": [],
            "pournami": [],
            "amavasya": [],
            "chaturthi": [],
            "shashti": [],
            "ashtami": [],
            "navami": [],
            "dwadashi": []
        }
        
        # Scan every day of the year
        start_date = datetime(self.year, 1, 1)
        end_date = datetime(self.year, 12, 31)
        current_date = start_date
        
        while current_date <= end_date:
            tithi = calculate_tithi(current_date, self.latitude, self.longitude)
            tamil_date = get_tamil_date(current_date)
            nakshatra = get_nakshatra(current_date, self.latitude, self.longitude)
            
            # Pradosham (13th tithi of both fortnights)
            if tithi in [12, 27]:  # 13th day (0-indexed)
                day_name = current_date.strftime("%A")
                pradosham_type = "Pradosham"
                if day_name == "Saturday":
                    pradosham_type = "Shani Pradosham"
                elif day_name == "Monday":
                    pradosham_type = "Soma Pradosham"
                elif day_name == "Tuesday":
                    pradosham_type = "Bhauma Pradosham"
                    
                festivals["pradosham"].append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": day_name,
                    "type": pradosham_type,
                    "tamil_month": tamil_date["month"],
                    "tamil_date": tamil_date["date"],
                    "nakshatra": nakshatra,
                    "tithi_index": tithi
                })
            
            # Ekadashi (11th tithi)
            if tithi in [10, 25]:  # 11th day
                ekadashi_type = "Ekadashi"
                # Special Ekadashis
                if current_date.month == 12 and tithi == 10:
                    ekadashi_type = "Vaikunta Ekadashi"
                elif current_date.month == 7 and tithi == 10:
                    ekadashi_type = "Aadi Ekadashi"
                    
                festivals["ekadashi"].append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": current_date.strftime("%A"),
                    "type": ekadashi_type,
                    "tamil_month": tamil_date["month"],
                    "tamil_date": tamil_date["date"],
                    "nakshatra": nakshatra
                })
            
            # Pournami (Full moon - 15th tithi of bright fortnight)
            if tithi == 14:  # 15th day
                pournami_type = "Pournami"
                # Special full moons
                if tamil_date["month"] == "Thai":
                    pournami_type = "Thai Pusam"
                elif tamil_date["month"] == "Aadi":
                    pournami_type = "Aadi Pooram"
                elif tamil_date["month"] == "Panguni":
                    pournami_type = "Panguni Uthiram"
                    
                festivals["pournami"].append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": current_date.strftime("%A"),
                    "type": pournami_type,
                    "tamil_month": tamil_date["month"],
                    "tamil_date": tamil_date["date"],
                    "nakshatra": nakshatra
                })
            
            # Amavasya (New moon - 30th tithi)
            if tithi == 29:  # 30th day
                amavasya_type = "Amavasya"
                # Special new moons
                if tamil_date["month"] == "Aadi":
                    amavasya_type = "Aadi Amavasya"
                elif tamil_date["month"] == "Thai":
                    amavasya_type = "Thai Amavasya"
                    
                festivals["amavasya"].append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": current_date.strftime("%A"),
                    "type": amavasya_type,
                    "tamil_month": tamil_date["month"],
                    "tamil_date": tamil_date["date"],
                    "nakshatra": nakshatra
                })
            
            # Chaturthi (4th tithi - Ganesha)
            if tithi in [3, 18]:  # 4th day
                chaturthi_type = "Chaturthi"
                if tithi == 18:  # Krishna paksha
                    chaturthi_type = "Sankashti Chaturthi"
                if current_date.month == 8:  # Vinayagar Chaturthi
                    chaturthi_type = "Vinayagar Chaturthi"
                    
                festivals["chaturthi"].append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": current_date.strftime("%A"),
                    "type": chaturthi_type,
                    "tamil_month": tamil_date["month"],
                    "tamil_date": tamil_date["date"]
                })
            
            # Shashti (6th tithi - Murugan)
            if tithi in [5, 20]:  # 6th day
                shashti_type = "Shashti"
                if current_date.month == 10:  # Skanda Shashti
                    shashti_type = "Skanda Shashti"
                    
                festivals["shashti"].append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": current_date.strftime("%A"),
                    "type": shashti_type,
                    "tamil_month": tamil_date["month"],
                    "tamil_date": tamil_date["date"]
                })
            
            # Ashtami (8th tithi - Durga)
            if tithi in [7, 22]:  # 8th day
                ashtami_type = "Ashtami"
                if current_date.month == 9:  # Durga Ashtami
                    ashtami_type = "Durga Ashtami"
                    
                festivals["ashtami"].append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": current_date.strftime("%A"),
                    "type": ashtami_type,
                    "tamil_month": tamil_date["month"],
                    "tamil_date": tamil_date["date"]
                })
            
            # Navami (9th tithi)
            if tithi in [8, 23]:  # 9th day
                navami_type = "Navami"
                if current_date.month == 3:  # Ram Navami
                    navami_type = "Ram Navami"
                    
                festivals["navami"].append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": current_date.strftime("%A"),
                    "type": navami_type,
                    "tamil_month": tamil_date["month"],
                    "tamil_date": tamil_date["date"]
                })
            
            # Dwadashi (12th tithi)
            if tithi in [11, 26]:  # 12th day
                festivals["dwadashi"].append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": current_date.strftime("%A"),
                    "type": "Dwadashi",
                    "tamil_month": tamil_date["month"],
                    "tamil_date": tamil_date["date"]
                })
            
            current_date += timedelta(days=1)
        
        return festivals
    
    def calculate_major_festivals(self):
        """Calculate major annual festivals"""
        festivals = []
        
        # Tamil New Year (Sun enters Aries)
        # Approximate date - needs precise calculation
        festivals.append({
            "date": "2025-04-14",
            "name": "Tamil New Year",
            "tamil_name": "தமிழ் புத்தாண்டு",
            "type": "major_annual",
            "description": "Sun enters Mesha Rasi (Aries)"
        })
        
        # Pongal (Fixed date)
        festivals.append({
            "date": "2025-01-14",
            "name": "Thai Pongal",
            "tamil_name": "தை பொங்கல்",
            "type": "harvest_festival",
            "description": "Harvest festival"
        })
        
        # Deepavali (New moon in Aippasi)
        festivals.append({
            "date": "2025-10-20",
            "name": "Deepavali",
            "tamil_name": "தீபாவளி",
            "type": "major_annual",
            "description": "Festival of lights"
        })
        
        # Maha Shivaratri
        festivals.append({
            "date": "2025-02-26",
            "name": "Maha Shivaratri",
            "tamil_name": "மகா சிவராத்திரி",
            "type": "major_annual",
            "description": "Great night of Shiva"
        })
        
        # Navaratri start
        festivals.append({
            "date": "2025-09-21",
            "name": "Navaratri Begins",
            "tamil_name": "நவராத்திரி",
            "type": "major_annual",
            "duration_days": 9,
            "description": "Nine nights festival"
        })
        
        # Vijayadashami
        festivals.append({
            "date": "2025-09-30",
            "name": "Vijayadashami",
            "tamil_name": "விஜயதசமி",
            "type": "major_annual",
            "description": "Victory day"
        })
        
        return festivals
    
    def generate_deity_specific_patterns(self):
        """Generate deity-specific festival patterns"""
        deity_patterns = {
            "SHIVA": {
                "primary_deity": "Shiva",
                "tamil_name": "சிவன்",
                "special_weekday": "monday",
                "monthly_festivals": ["pradosham", "shivaratri"],
                "annual_festivals": [
                    "maha_shivaratri",
                    "arudra_darshan",
                    "panguni_uthiram",
                    "thiruvathirai"
                ],
                "special_months": ["karthigai", "margazhi"],
                "identifier_keywords": [
                    "easwara", "eswara", "eshwar", "ishwar",
                    "natha", "nathar", "nathan",
                    "shiva", "siva", "shiv", "siv",
                    "lingam", "linga",
                    "swamy", "swami"
                ]
            },
            "MURUGAN": {
                "primary_deity": "Murugan",
                "tamil_name": "முருகன்",
                "special_weekday": "tuesday",
                "monthly_festivals": ["shashti"],
                "annual_festivals": [
                    "thai_pusam",
                    "vaikasi_visakam",
                    "skanda_shashti",
                    "panguni_uthiram"
                ],
                "special_months": ["thai", "vaikasi", "aippasi"],
                "identifier_keywords": [
                    "murugan", "muruga",
                    "subramanya", "subramania", "subramani",
                    "karthikeya", "kartikeya",
                    "dandayudhapani", "dandayuthapani",
                    "palani", "thiruchendur",
                    "kumara", "kumaran",
                    "senthil", "saravana"
                ]
            },
            "AMMAN": {
                "primary_deity": "Amman/Devi",
                "tamil_name": "அம்மன்",
                "special_weekday": "friday",
                "secondary_weekday": "tuesday",
                "monthly_festivals": ["pournami"],
                "annual_festivals": [
                    "navaratri",
                    "aadi_pooram",
                    "aadi_fridays",
                    "amman_thiruvizha"
                ],
                "special_months": ["aadi", "purattasi"],
                "identifier_keywords": [
                    "amman", "amma",
                    "mariamman", "mari",
                    "kali", "kaali",
                    "durga", "durgai",
                    "meenakshi", "kamakshi",
                    "visalakshi", "parvathi",
                    "bhagavathi", "devi"
                ]
            },
            "VISHNU": {
                "primary_deity": "Vishnu/Perumal",
                "tamil_name": "விஷ்ணு/பெருமாள்",
                "special_weekday": "saturday",
                "monthly_festivals": ["ekadashi"],
                "annual_festivals": [
                    "vaikunta_ekadashi",
                    "rama_navami",
                    "krishna_jayanthi",
                    "purattasi_saturdays",
                    "panguni_uthiram"
                ],
                "special_months": ["purattasi", "margazhi"],
                "identifier_keywords": [
                    "perumal", "perumal",
                    "vishnu", "visnu",
                    "krishna", "krishnan",
                    "rama", "raman", "ramar",
                    "narayana", "narayanan",
                    "ranganatha", "ranganathar",
                    "venkatesa", "venkateswara",
                    "srinivasa", "balaji",
                    "varadaraja", "parthasarathy"
                ]
            },
            "GANESHA": {
                "primary_deity": "Ganesha/Vinayagar",
                "tamil_name": "விநாயகர்/கணபதி",
                "special_weekday": null,
                "monthly_festivals": ["chaturthi", "sankashti_chaturthi"],
                "annual_festivals": [
                    "vinayagar_chaturthi",
                    "ganesh_jayanthi"
                ],
                "special_months": ["avani"],
                "identifier_keywords": [
                    "vinayagar", "vinayaka",
                    "ganapathi", "ganapathy", "ganesh",
                    "ganesha", "ganesa",
                    "pillayar", "pillaiyar",
                    "vigneswara", "vigneshwara"
                ]
            }
        }
        
        return deity_patterns
    
    def generate_district_patterns(self):
        """Generate district-specific festival patterns"""
        district_patterns = {
            "Chennai District": {
                "special_festivals": [
                    {
                        "name": "Kapaleeshwarar Panguni Festival",
                        "month": "Panguni",
                        "duration": 10
                    },
                    {
                        "name": "Mylapore Festival",
                        "month": "Thai",
                        "duration": 10
                    }
                ],
                "emphasis": ["urban_celebrations", "coastal_festivals"],
                "major_temples": ["Kapaleeshwarar", "Parthasarathy", "Vadapalani"]
            },
            "Madurai District": {
                "special_festivals": [
                    {
                        "name": "Meenakshi Thirukalyanam",
                        "month": "Chithirai",
                        "duration": 12
                    },
                    {
                        "name": "Float Festival",
                        "month": "Thai",
                        "duration": 3
                    }
                ],
                "emphasis": ["temple_city_festivals", "traditional_celebrations"],
                "major_temples": ["Meenakshi", "Koodal Azhagar"]
            },
            "Thanjavur District": {
                "special_festivals": [
                    {
                        "name": "Thyagaraja Aradhana",
                        "month": "Thai",
                        "duration": 5
                    }
                ],
                "emphasis": ["cultural_festivals", "harvest_celebrations"],
                "major_temples": ["Brihadeeswarar", "Thyagarajar"]
            },
            "Kanchipuram District": {
                "special_festivals": [
                    {
                        "name": "Brahmotsavam",
                        "month": "Vaikasi",
                        "duration": 10
                    }
                ],
                "emphasis": ["temple_festivals", "silk_city_celebrations"],
                "major_temples": ["Ekambareswarar", "Kamakshi", "Varadaraja"]
            },
            "Rameswaram District": {
                "special_festivals": [
                    {
                        "name": "Masi Sivaratri",
                        "month": "Masi",
                        "duration": 1
                    }
                ],
                "emphasis": ["pilgrimage_festivals", "coastal_rituals"],
                "major_temples": ["Ramanathaswamy"]
            }
        }
        
        # Add generic pattern for other districts
        district_patterns["default"] = {
            "special_festivals": [],
            "emphasis": ["local_traditions", "agricultural_festivals"],
            "major_temples": []
        }
        
        return district_patterns
    
    def save_all_data(self):
        """Generate and save all festival data"""
        print("📅 Generating Universal Festival Data...")
        
        # 1. Calculate tithi-based festivals
        print("  Calculating tithi-based festivals...")
        tithi_festivals = self.calculate_all_tithis()
        
        # Save universal festivals
        universal_data = {
            "year": self.year,
            "generated_on": datetime.now().isoformat(),
            "location_reference": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "description": "Tamil Nadu center (for astronomical calculations)"
            },
            "festivals": tithi_festivals,
            "major_annual_festivals": self.calculate_major_festivals()
        }
        
        with open(f"../festivals/universal_festivals_{self.year}.json", "w", encoding="utf-8") as f:
            json.dump(universal_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Saved universal festivals ({sum(len(v) for v in tithi_festivals.values())} dates)")
        
        # 2. Save deity patterns
        print("  Generating deity patterns...")
        deity_patterns = self.generate_deity_specific_patterns()
        
        with open("../festivals/deity_patterns.json", "w", encoding="utf-8") as f:
            json.dump(deity_patterns, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Saved deity patterns ({len(deity_patterns)} deity types)")
        
        # 3. Save district patterns
        print("  Generating district patterns...")
        district_patterns = self.generate_district_patterns()
        
        with open("../festivals/district_patterns.json", "w", encoding="utf-8") as f:
            json.dump(district_patterns, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Saved district patterns ({len(district_patterns)} districts)")
        
        # 4. Generate summary
        summary = {
            "year": self.year,
            "statistics": {
                "pradosham_days": len(tithi_festivals["pradosham"]),
                "ekadashi_days": len(tithi_festivals["ekadashi"]),
                "pournami_days": len(tithi_festivals["pournami"]),
                "amavasya_days": len(tithi_festivals["amavasya"]),
                "total_recurring": sum(len(v) for v in tithi_festivals.values()),
                "major_festivals": len(self.calculate_major_festivals()),
                "deity_types": len(deity_patterns),
                "districts_covered": len(district_patterns)
            },
            "files_generated": [
                f"universal_festivals_{self.year}.json",
                "deity_patterns.json",
                "district_patterns.json"
            ]
        }
        
        with open("../festivals/generation_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print("\n📊 Summary:")
        for key, value in summary["statistics"].items():
            print(f"  {key}: {value}")
        
        return summary

def main():
    generator = UniversalFestivalGenerator(2025)
    summary = generator.save_all_data()
    
    print("\n✅ Festival data generation complete!")
    print("  Files saved in ../festivals/ directory")
    print("\nNext steps:")
    print("  1. Create deity inference logic for temples")
    print("  2. Build API to serve festivals dynamically")
    print("  3. Add user feedback mechanism for corrections")

if __name__ == "__main__":
    main()