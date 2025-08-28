#!/usr/bin/env python3
"""
Enhanced Demo Data Exporter
============================
Export rich temple dataset from SQLite database for demo-ui integration
Transforms 193 FindMyTemple integrated temples into demo-compatible JSON
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any
import re

class DemoDataExporter:
    def __init__(self):
        self.db_path = '../database/temples.db'
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Stats for summary
        self.stats = {
            'total_exported': 0,
            'with_findmytemple': 0,
            'deity_distribution': {},
            'district_distribution': {},
            'completeness_levels': {'high': 0, 'medium': 0, 'low': 0}
        }
    
    def calculate_completeness_score(self, temple: Dict) -> int:
        """Calculate data completeness percentage for a temple"""
        
        # Core fields (mandatory)
        core_fields = ['name', 'district', 'address']
        core_score = sum(1 for field in core_fields if temple.get(field))
        
        # Enhanced fields (from FindMyTemple integration)
        enhanced_fields = ['goddess', 'holy_water', 'sacred_tree', 'special_rituals', 
                          'temple_tank', 'inscriptions']
        enhanced_score = sum(1 for field in enhanced_fields if temple.get(field))
        
        # Bonus fields
        bonus_fields = ['main_deity', 'deity_type']
        bonus_score = sum(1 for field in bonus_fields if temple.get(field))
        
        # Calculate weighted percentage
        total_possible = len(core_fields) * 3 + len(enhanced_fields) * 2 + len(bonus_fields)
        actual_score = core_score * 3 + enhanced_score * 2 + bonus_score
        
        return min(100, int((actual_score / total_possible) * 100))
    
    def extract_deity_type(self, temple: Dict) -> str:
        """Determine deity type from available data"""
        
        name = (temple.get('name') or '').lower()
        main_deity = (temple.get('main_deity') or '').lower()
        
        # Check for Shiva indicators
        shiva_patterns = ['eswara', 'ishwara', 'nataraja', 'shiva', 'siva', 'linga']
        if any(pattern in name or pattern in main_deity for pattern in shiva_patterns):
            return 'Shiva'
        
        # Check for Vishnu indicators  
        vishnu_patterns = ['vishnu', 'perumal', 'ranganatha', 'venkateshwara', 'rama', 'krishna']
        if any(pattern in name or pattern in main_deity for pattern in vishnu_patterns):
            return 'Vishnu'
        
        # Check for Murugan indicators
        murugan_patterns = ['murugan', 'subrahmanya', 'kartikeya', 'palani', 'dhandayutha']
        if any(pattern in name or pattern in main_deity for pattern in murugan_patterns):
            return 'Murugan'
        
        # Check for Devi/Amman indicators
        devi_patterns = ['amman', 'devi', 'lakshmi', 'saraswati', 'durga', 'kali', 'meenakshi']
        if any(pattern in name or pattern in main_deity for pattern in devi_patterns):
            return 'Devi'
        
        return 'Other'
    
    def clean_text(self, text: str) -> str:
        """Clean and format text for UI display"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', str(text)).strip()
        
        # Handle JSON-like strings (common in our data)
        if cleaned.startswith('{') or cleaned.startswith('['):
            try:
                # Try to parse and extract meaningful content
                parsed = json.loads(cleaned)
                if isinstance(parsed, dict):
                    # Extract first meaningful value
                    for key, value in parsed.items():
                        if value and isinstance(value, str) and len(value.strip()) > 0:
                            return str(value).strip()
                elif isinstance(parsed, list) and parsed:
                    return str(parsed[0]).strip()
            except:
                pass
        
        return cleaned
    
    def process_festivals(self, festivals_data: str) -> List[str]:
        """Process festival data into clean list"""
        if not festivals_data:
            return []
        
        try:
            # Try to parse as JSON first
            if festivals_data.startswith('['):
                festivals = json.loads(festivals_data)
                if isinstance(festivals, list):
                    return [self.clean_text(f) for f in festivals if f][:5]  # Limit to 5 festivals
        except:
            pass
        
        # Fallback: split by common delimiters
        festivals = re.split(r'[,;|]', festivals_data)
        return [self.clean_text(f) for f in festivals if f.strip()][:5]
    
    def get_tamil_name(self, english_name: str) -> str:
        """Generate or improve Tamil name display"""
        
        # Common temple name translations
        translations = {
            'temple': 'கோயில்',
            'swamy': 'சுவாமி',
            'amman': 'அம்மன்',
            'perumal': 'பெருமாள்',
            'eswara': 'ஈஸ்வரர்',
            'nataraja': 'நடராஜர்'
        }
        
        # For now, return the name with temple suffix
        # In a real implementation, you'd have proper Tamil translations
        return f"{english_name} கோயில்"
    
    def export_enhanced_temples(self) -> Dict[str, Any]:
        """Export all temples with FindMyTemple integration"""
        
        print("🔄 Querying database for enhanced temple data...")
        
        # Query temples with FindMyTemple integration
        query = """
        SELECT temple_id, name, tamil_name, district, address, main_deity, deity_type,
               income_category, temple_type, goddess, holy_water, sacred_tree, 
               special_rituals, temple_tank, inscriptions, temple_age, raw_data
        FROM temples 
        WHERE raw_data LIKE '%findmytemple%'
        ORDER BY name
        """
        
        cursor = self.conn.execute(query)
        temples = []
        
        for row in cursor:
            row_dict = None
            try:
                # Convert row to dict for processing
                row_dict = dict(row)
                
                # Parse raw_data for additional fields
                raw_data = {}
                if row_dict['raw_data']:
                    try:
                        raw_data = json.loads(row_dict['raw_data'])
                    except:
                        pass
                
                # Extract FindMyTemple data
                fmt_data = raw_data.get('findmytemple', {})
                
                # Build enhanced temple record
                temple = {
                    'temple_id': row_dict['temple_id'],
                    'name': self.clean_text(row_dict['name']),
                    'tamil_name': row_dict['tamil_name'] or self.get_tamil_name(row_dict['name']),
                    'district': self.clean_text(row_dict['district']),
                    'location': self.clean_text(row_dict['address']),
                    'city': self.extract_city(row_dict['address']),
                    'deity_type': row_dict['deity_type'] or self.extract_deity_type(row_dict),
                    'main_deity': self.clean_text(row_dict['main_deity']),
                    'goddess': self.clean_text(row_dict['goddess']),
                }
                
                # Add enhanced fields from FindMyTemple
                if fmt_data:
                    self.stats['with_findmytemple'] += 1
                    
                    # Timings
                    timings = fmt_data.get('timings', {})
                    if isinstance(timings, dict):
                        temple['timings'] = timings.get('general', 'Contact temple for timings')
                    elif isinstance(timings, str):
                        temple['timings'] = self.clean_text(timings)
                    else:
                        temple['timings'] = 'Contact temple for timings'
                    
                    # Contact info
                    contact = fmt_data.get('contact', {})
                    if isinstance(contact, dict):
                        temple['phone'] = contact.get('phone', '')
                        temple['email'] = contact.get('email', '')
                        temple['website'] = contact.get('website', '')
                    
                    # Festivals
                    festivals = fmt_data.get('festivals', [])
                    if isinstance(festivals, list):
                        temple['festivals'] = [str(f) for f in festivals[:5]]
                    else:
                        temple['festivals'] = self.process_festivals(str(festivals))
                    
                    # Location data
                    location_data = fmt_data.get('location', {})
                    if isinstance(location_data, dict):
                        temple['latitude'] = location_data.get('coordinates', {}).get('lat', 0.0)
                        temple['longitude'] = location_data.get('coordinates', {}).get('lng', 0.0)
                    
                else:
                    # Default values for temples without FindMyTemple data
                    temple['timings'] = 'Contact temple for timings'
                    temple['phone'] = ''
                    temple['festivals'] = []
                    temple['latitude'] = 0.0
                    temple['longitude'] = 0.0
                
                # Enhanced spiritual elements
                temple['holy_water'] = self.clean_text(row_dict['holy_water'])
                temple['sacred_tree'] = self.clean_text(row_dict['sacred_tree'])
                temple['special_features'] = self.process_festivals(row_dict['special_rituals'])
                temple['temple_tank'] = self.clean_text(row_dict['temple_tank'])
                temple['inscriptions'] = self.clean_text(row_dict['inscriptions'])
                temple['historical_period'] = self.clean_text(row_dict['temple_age'])
                
                # Calculate completeness
                temple['data_completeness'] = self.calculate_completeness_score(temple)
                
                # Categorize completeness
                if temple['data_completeness'] >= 80:
                    self.stats['completeness_levels']['high'] += 1
                elif temple['data_completeness'] >= 60:
                    self.stats['completeness_levels']['medium'] += 1
                else:
                    self.stats['completeness_levels']['low'] += 1
                
                # Update stats
                deity_type = temple['deity_type']
                self.stats['deity_distribution'][deity_type] = self.stats['deity_distribution'].get(deity_type, 0) + 1
                
                district = temple['district']
                self.stats['district_distribution'][district] = self.stats['district_distribution'].get(district, 0) + 1
                
                temples.append(temple)
                self.stats['total_exported'] += 1
                
            except Exception as e:
                temple_name = row_dict.get('name', 'Unknown') if row_dict else 'Unknown'
                print(f"⚠️ Error processing temple {temple_name}: {e}")
                continue
        
        # Build complete export structure
        export_data = {
            'metadata': {
                'source': 'Enhanced HRCE + FindMyTemple Integration',
                'export_date': datetime.now().isoformat(),
                'total_temples': len(temples),
                'data_quality': 'High - Comprehensive integration with 193 temples',
                'update_source': 'SQLite database with FindMyTemple matches',
                'completeness_distribution': self.stats['completeness_levels'],
                'deity_distribution': dict(sorted(self.stats['deity_distribution'].items())),
                'district_count': len(self.stats['district_distribution'])
            },
            'featured_temples': self.select_featured_temples(temples),
            'temples': temples
        }
        
        return export_data
    
    def extract_city(self, address: str) -> str:
        """Extract city name from address"""
        if not address:
            return ""
        
        # Simple extraction - take the part before comma or use last word
        parts = address.split(',')
        if len(parts) > 1:
            return parts[0].strip()
        
        words = address.split()
        return words[-1] if words else ""
    
    def select_featured_temples(self, temples: List[Dict]) -> List[Dict]:
        """Select featured temples based on data quality and significance"""
        
        # Sort by completeness and variety
        featured = []
        
        # Get highest quality temples from each deity type
        deity_types = ['Shiva', 'Vishnu', 'Murugan', 'Devi']
        for deity_type in deity_types:
            deity_temples = [t for t in temples if t['deity_type'] == deity_type]
            if deity_temples:
                # Sort by completeness and take top 2
                deity_temples.sort(key=lambda x: x['data_completeness'], reverse=True)
                featured.extend(deity_temples[:2])
        
        # Add some high-quality temples regardless of type
        all_sorted = sorted(temples, key=lambda x: x['data_completeness'], reverse=True)
        for temple in all_sorted[:12]:  # Top 12 overall
            if temple not in featured:
                featured.append(temple)
            if len(featured) >= 16:  # Limit featured temples
                break
        
        return featured[:16]
    
    def print_export_summary(self, export_data: Dict):
        """Print summary of export results"""
        
        print("\n" + "="*60)
        print("🎯 ENHANCED DEMO DATA EXPORT SUMMARY")
        print("="*60)
        
        metadata = export_data['metadata']
        print(f"✅ Total temples exported: {metadata['total_temples']}")
        print(f"✅ With FindMyTemple data: {self.stats['with_findmytemple']}")
        print(f"✅ Featured temples: {len(export_data['featured_temples'])}")
        print(f"✅ Districts covered: {metadata['district_count']}")
        
        print(f"\n📊 Data Completeness:")
        for level, count in metadata['completeness_distribution'].items():
            percentage = (count / metadata['total_temples']) * 100
            print(f"   {level.title()}: {count} temples ({percentage:.1f}%)")
        
        print(f"\n🏛️ Deity Distribution:")
        for deity, count in metadata['deity_distribution'].items():
            percentage = (count / metadata['total_temples']) * 100
            print(f"   {deity}: {count} temples ({percentage:.1f}%)")
        
        print(f"\n📍 Top Districts:")
        sorted_districts = sorted(self.stats['district_distribution'].items(), 
                                key=lambda x: x[1], reverse=True)
        for district, count in sorted_districts[:8]:
            print(f"   {district}: {count} temples")

def main():
    print("🚀 Starting Enhanced Demo Data Export...")
    
    exporter = DemoDataExporter()
    
    try:
        # Export the data
        export_data = exporter.export_enhanced_temples()
        
        # Save to demo-ui data directory
        output_path = '../demo-ui/data/enhanced_temple_data.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Print summary
        exporter.print_export_summary(export_data)
        
        print(f"\n💾 Enhanced dataset exported to: {output_path}")
        print("🎉 Ready for demo-ui integration!")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        raise
    
    finally:
        exporter.conn.close()

if __name__ == "__main__":
    main()