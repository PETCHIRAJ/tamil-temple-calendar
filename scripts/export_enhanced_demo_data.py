#!/usr/bin/env python3
"""
Enhanced Demo Data Exporter with Coordinates
=============================================
Exports temple data with GPS coordinates and festival calendar for location-based features
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any
import re

class EnhancedDataExporter:
    def __init__(self):
        self.db_path = '../database/temples.db'
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Load coordinate data
        with open('../json_data/enrichments/578_temples_coordinates_final.json', 'r') as f:
            self.coordinates = json.load(f)
        
        # Load festival calendar
        with open('../json_data/festivals/festivals_2025.json', 'r') as f:
            self.festival_calendar = json.load(f)
        
        # Stats
        self.stats = {
            'total_exported': 0,
            'with_coordinates': 0,
            'with_pincode': 0,
            'with_festivals': 0,
            'districts': set(),
            'pincodes': set()
        }
    
    def export_all_temples(self) -> Dict[str, Any]:
        """Export all temples with available data"""
        
        print("🔄 Exporting all temple data with coordinates...")
        
        # Query all temples
        query = """
        SELECT temple_id, name, tamil_name, district, address, main_deity, deity_type,
               income_category, temple_type, goddess, holy_water, sacred_tree, 
               special_rituals, temple_tank, inscriptions, temple_age, raw_data
        FROM temples 
        ORDER BY name
        """
        
        cursor = self.conn.execute(query)
        temples = []
        temples_with_coords = []
        pincode_groups = {}
        district_groups = {}
        
        for row in cursor:
            row_dict = dict(row)
            
            # Parse raw_data for additional info
            raw_data = {}
            if row_dict['raw_data']:
                try:
                    raw_data = json.loads(row_dict['raw_data'])
                except:
                    pass
            
            # Extract pincode
            pincode = None
            if 'pincode' in raw_data:
                pincode = str(raw_data['pincode'])
                self.stats['pincodes'].add(pincode)
            
            # Build temple object
            temple = {
                'temple_id': row_dict['temple_id'],
                'name': self.clean_text(row_dict['name']),
                'tamil_name': row_dict['tamil_name'] or self.get_tamil_name(row_dict['name']),
                'district': self.clean_district(row_dict['district']),
                'address': self.clean_text(row_dict['address']),
                'pincode': pincode,
                'deity_type': row_dict['deity_type'] or self.extract_deity_type(row_dict),
                'main_deity': self.clean_text(row_dict['main_deity']),
                'goddess': self.clean_text(row_dict['goddess']),
                'income_category': row_dict['income_category'],
                'temple_type': row_dict['temple_type']
            }
            
            # Add coordinates if available
            if row_dict['temple_id'] in self.coordinates:
                coord_data = self.coordinates[row_dict['temple_id']]
                temple['latitude'] = coord_data['latitude']
                temple['longitude'] = coord_data['longitude']
                temple['location_confidence'] = coord_data.get('confidence', 'medium')
                temples_with_coords.append(temple)
                self.stats['with_coordinates'] += 1
            else:
                temple['latitude'] = None
                temple['longitude'] = None
            
            # Enhanced fields from FindMyTemple integration
            fmt_data = raw_data.get('findmytemple', {})
            if fmt_data:
                # Extract festivals
                festivals = fmt_data.get('festivals', [])
                if isinstance(festivals, list) and festivals:
                    temple['festivals'] = [str(f) for f in festivals[:5]]
                    self.stats['with_festivals'] += 1
                
                # Extract timings
                timings = fmt_data.get('timings', {})
                if isinstance(timings, dict):
                    temple['timings'] = timings.get('general', '')
                elif isinstance(timings, str):
                    temple['timings'] = timings
                
                # Contact info
                contact = fmt_data.get('contact', {})
                if isinstance(contact, dict):
                    temple['phone'] = contact.get('phone', '')
            
            # Add enhanced spiritual fields
            temple['holy_water'] = self.clean_text(row_dict['holy_water'])
            temple['sacred_tree'] = self.clean_text(row_dict['sacred_tree'])
            temple['special_rituals'] = self.clean_text(row_dict['special_rituals'])
            temple['temple_tank'] = self.clean_text(row_dict['temple_tank'])
            temple['inscriptions'] = self.clean_text(row_dict['inscriptions'])
            temple['historical_period'] = self.clean_text(row_dict['temple_age'])
            
            # Calculate data completeness
            temple['data_completeness'] = self.calculate_completeness(temple)
            
            # Track statistics
            if temple['district']:
                self.stats['districts'].add(temple['district'])
                if temple['district'] not in district_groups:
                    district_groups[temple['district']] = []
                district_groups[temple['district']].append(temple)
            
            if pincode:
                self.stats['with_pincode'] += 1
                if pincode not in pincode_groups:
                    pincode_groups[pincode] = []
                pincode_groups[pincode].append(temple)
            
            temples.append(temple)
            self.stats['total_exported'] += 1
        
        # Sort temples with coordinates by data completeness
        temples_with_coords.sort(key=lambda x: x['data_completeness'], reverse=True)
        
        # Get featured temples (top quality with coordinates)
        featured_temples = temples_with_coords[:30] if len(temples_with_coords) >= 30 else temples_with_coords
        
        # Build district statistics
        district_stats = {}
        for district, district_temples in district_groups.items():
            district_stats[district] = {
                'total': len(district_temples),
                'with_coordinates': sum(1 for t in district_temples if t['latitude']),
                'top_deity': self.get_top_deity(district_temples)
            }
        
        # Build pincode index (for efficient lookup)
        pincode_index = {
            pincode: len(temples_list) 
            for pincode, temples_list in pincode_groups.items()
        }
        
        # Build export structure
        export_data = {
            'metadata': {
                'source': 'Complete HRCE Database with Coordinates',
                'export_date': datetime.now().isoformat(),
                'total_temples': len(temples),
                'temples_with_coordinates': self.stats['with_coordinates'],
                'temples_with_pincode': self.stats['with_pincode'],
                'temples_with_festivals': self.stats['with_festivals'],
                'total_districts': len(self.stats['districts']),
                'total_pincodes': len(self.stats['pincodes']),
                'coordinate_coverage': f"{(self.stats['with_coordinates']/len(temples)*100):.1f}%",
                'pincode_coverage': f"{(self.stats['with_pincode']/len(temples)*100):.1f}%"
            },
            'featured_temples': featured_temples,
            'temples_with_coordinates': temples_with_coords,
            'all_temples': temples[:1000],  # Limit for demo - full data too large
            'district_statistics': district_stats,
            'pincode_index': pincode_index,
            'festival_calendar': self.festival_calendar
        }
        
        return export_data
    
    def clean_text(self, text: str) -> str:
        """Clean and format text"""
        if not text:
            return ""
        return str(text).strip()
    
    def clean_district(self, district: str) -> str:
        """Clean district name"""
        if not district:
            return ""
        # Remove 'District' suffix if present
        cleaned = str(district).replace(' District', '').strip()
        return cleaned
    
    def get_tamil_name(self, english_name: str) -> str:
        """Generate Tamil name placeholder"""
        return f"{english_name} கோயில்"
    
    def extract_deity_type(self, temple: Dict) -> str:
        """Determine deity type from temple data"""
        name = (temple.get('name') or '').lower()
        main_deity = (temple.get('main_deity') or '').lower()
        
        # Check patterns
        if any(p in name or p in main_deity for p in ['eswara', 'ishwara', 'nataraja', 'shiva', 'siva']):
            return 'Shiva'
        elif any(p in name or p in main_deity for p in ['vishnu', 'perumal', 'ranganatha', 'krishna']):
            return 'Vishnu'
        elif any(p in name or p in main_deity for p in ['murugan', 'subrahmanya', 'kartikeya']):
            return 'Murugan'
        elif any(p in name or p in main_deity for p in ['amman', 'devi', 'lakshmi', 'durga']):
            return 'Devi'
        
        return 'Other'
    
    def calculate_completeness(self, temple: Dict) -> int:
        """Calculate data completeness percentage"""
        fields = ['name', 'district', 'address', 'pincode', 'deity_type', 
                 'main_deity', 'goddess', 'timings', 'festivals', 
                 'holy_water', 'sacred_tree', 'latitude', 'longitude']
        
        filled = sum(1 for field in fields if temple.get(field))
        return int((filled / len(fields)) * 100)
    
    def get_top_deity(self, temples: List[Dict]) -> str:
        """Get most common deity type in temple list"""
        deity_counts = {}
        for temple in temples:
            deity = temple.get('deity_type', 'Other')
            deity_counts[deity] = deity_counts.get(deity, 0) + 1
        
        if deity_counts:
            return max(deity_counts, key=deity_counts.get)
        return 'Unknown'
    
    def print_summary(self):
        """Print export summary"""
        print("\n" + "="*60)
        print("📊 ENHANCED EXPORT SUMMARY")
        print("="*60)
        print(f"✅ Total temples exported: {self.stats['total_exported']}")
        print(f"📍 Temples with coordinates: {self.stats['with_coordinates']}")
        print(f"📮 Temples with pincode: {self.stats['with_pincode']}")
        print(f"🎉 Temples with festivals: {self.stats['with_festivals']}")
        print(f"🏛️ Districts covered: {len(self.stats['districts'])}")
        print(f"📬 Unique pincodes: {len(self.stats['pincodes'])}")

def main():
    print("🚀 Starting Enhanced Data Export with Coordinates...")
    
    exporter = EnhancedDataExporter()
    
    try:
        # Export the data
        export_data = exporter.export_all_temples()
        
        # Save to demo-ui data directory
        output_path = '../demo-ui/data/temples_with_location.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Print summary
        exporter.print_summary()
        
        print(f"\n💾 Enhanced dataset exported to: {output_path}")
        print("✅ Ready for location-based features!")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        raise
    
    finally:
        exporter.conn.close()

if __name__ == "__main__":
    main()