#!/usr/bin/env python3
"""
Temple Matching Script
======================
Matches FindMyTemple scraped data with existing database temples
using multiple matching strategies and confidence scoring.
"""

import json
import sqlite3
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from datetime import datetime


class TempleMapper:
    """Maps FindMyTemple temples to database temples"""
    
    def __init__(self, db_path: str = "database/temples.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.mappings = {}
        self.statistics = {
            'total_scraped': 0,
            'exact_matches': 0,
            'strong_matches': 0,
            'good_matches': 0,
            'possible_matches': 0,
            'weak_matches': 0,
            'no_matches': 0
        }
        
    def clean_name(self, name) -> str:
        """Normalize temple name for matching"""
        if not name:
            return ""
        
        # Handle list input - take first item
        if isinstance(name, list):
            name = name[0] if name else ""
        
        # Convert to string
        name = str(name)
        
        # Remove common prefixes
        name = re.sub(r'^(Arulmigu\s+|Sri\s+|Shri\s+|Shree\s+)', '', name, flags=re.I)
        # Remove temple/kovil suffixes
        name = re.sub(r'\s+(Temple|Kovil|Koil|Swamy|Swami|Samy)$', '', name, flags=re.I)
        # Normalize whitespace
        name = ' '.join(name.split())
        
        return name.strip().lower()
    
    def normalize_district(self, district: str) -> str:
        """Normalize district names"""
        if not district:
            return ""
        
        # Remove "District" suffix
        district = re.sub(r'\s+District$', '', district, flags=re.I)
        
        # Handle known variations
        district_map = {
            'tanjore': 'thanjavur',
            'tirunelveli': 'tirunelveli',
            'nellai': 'tirunelveli',
            'trichy': 'thiruchirappalli',
            'tiruchirappalli': 'thiruchirappalli',
            'madurai': 'madurai',
            'coimbatore': 'coimbatore',
            'kovai': 'coimbatore'
        }
        
        clean = district.lower().strip()
        return district_map.get(clean, clean)
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two temple names"""
        clean1 = self.clean_name(name1)
        clean2 = self.clean_name(name2)
        
        if not clean1 or not clean2:
            return 0.0
        
        # Direct comparison
        if clean1 == clean2:
            return 100.0
        
        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, clean1, clean2).ratio() * 100
    
    def calculate_location_similarity(self, scraped: Dict, db_temple: Dict) -> float:
        """Calculate location similarity"""
        score = 0.0
        
        # Handle location as string or dict
        location = scraped.get('location', {})
        if isinstance(location, str):
            scraped_district = ''
            scraped_city = ''
            scraped_lat = None
            scraped_lon = None
        else:
            # District match
            scraped_district = self.normalize_district(location.get('district', ''))
            scraped_city = location.get('city', '').lower()
            scraped_lat = location.get('coordinates', {}).get('latitude')
            scraped_lon = location.get('coordinates', {}).get('longitude')
        
        db_district = self.normalize_district(db_temple.get('district', ''))
        
        if scraped_district and db_district:
            if scraped_district == db_district:
                score += 50
        
        # City match
        db_location = db_temple.get('location', '').lower() if db_temple.get('location') else ''
        db_address = db_temple.get('address', '').lower() if db_temple.get('address') else ''
        
        if scraped_city:
            if scraped_city in db_location or scraped_city in db_address:
                score += 30
        
        # Coordinate match (if available)
        db_lat = db_temple.get('latitude')
        db_lon = db_temple.get('longitude')
        
        if all([scraped_lat, scraped_lon, db_lat, db_lon]):
            # Check if coordinates are within ~100m (0.001 degrees)
            if abs(float(scraped_lat) - float(db_lat)) < 0.001 and \
               abs(float(scraped_lon) - float(db_lon)) < 0.001:
                score += 20
        
        return score
    
    def calculate_deity_similarity(self, scraped: Dict, db_temple: Dict) -> float:
        """Calculate deity similarity"""
        score = 0.0
        
        # Handle different deity data structures
        deities = scraped.get('deities', {})
        if isinstance(deities, list):
            # Some temples have deities as a list
            scraped_deity = ''
            scraped_goddess = ''
        else:
            # Main deity match
            scraped_deity = self.clean_name(deities.get('main_deity', ''))
            scraped_goddess = self.clean_name(deities.get('goddess', ''))
        
        db_deity = self.clean_name(db_temple.get('main_deity', ''))
        
        if scraped_deity and db_deity:
            deity_sim = self.calculate_name_similarity(scraped_deity, db_deity)
            if deity_sim > 80:
                score += 50
            elif deity_sim > 60:
                score += 30
        
        return score
    
    def find_best_match(self, scraped_temple: Dict) -> Tuple[Optional[str], float, str]:
        """Find best matching temple in database"""
        
        scraped_name = scraped_temple.get('name', '')
        location = scraped_temple.get('location', {})
        
        # Handle location as string or dict
        if isinstance(location, str):
            scraped_district = ''
        else:
            scraped_district = self.normalize_district(location.get('district', ''))
        
        # Query potential matches from database
        query = """
        SELECT temple_id, name, district, location, address, 
               latitude, longitude, main_deity
        FROM temples
        WHERE district LIKE ?
        """
        
        cursor = self.conn.execute(query, (f'%{scraped_district}%',))
        potential_matches = []
        
        for row in cursor:
            db_temple = dict(row)
            
            # Calculate match score
            name_score = self.calculate_name_similarity(scraped_name, db_temple['name'])
            location_score = self.calculate_location_similarity(scraped_temple, db_temple)
            deity_score = self.calculate_deity_similarity(scraped_temple, db_temple)
            
            # Weighted total score
            total_score = (name_score * 0.5) + (location_score * 0.3) + (deity_score * 0.2)
            
            potential_matches.append({
                'temple_id': db_temple['temple_id'],
                'name': db_temple['name'],
                'score': total_score,
                'name_score': name_score,
                'location_score': location_score,
                'deity_score': deity_score
            })
        
        # Sort by score and get best match
        potential_matches.sort(key=lambda x: x['score'], reverse=True)
        
        if not potential_matches:
            return None, 0, 'no_match'
        
        best_match = potential_matches[0]
        score = best_match['score']
        
        # Determine match quality
        if score >= 90:
            method = 'exact_match' if best_match['name_score'] >= 95 else 'strong_match'
        elif score >= 80:
            method = 'good_match'
        elif score >= 70:
            method = 'possible_match'
        elif score >= 50:
            method = 'weak_match'
        else:
            return None, score, 'no_match'
        
        return best_match['temple_id'], score, method
    
    def process_all_temples(self):
        """Process all FindMyTemple temples"""
        
        # Load scraped data
        with open('findmytemple_master_scraped_data.json', 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
        
        temples = scraped_data['temples_scraped']
        self.statistics['total_scraped'] = len(temples)
        
        print(f"Processing {len(temples)} temples...")
        print("=" * 60)
        
        for i, temple in enumerate(temples, 1):
            temple_id = temple['temple_id']
            temple_name = temple.get('name', 'Unknown')
            
            # Find best match
            db_id, confidence, method = self.find_best_match(temple)
            
            # Store mapping
            location = temple.get('location', {})
            if isinstance(location, str):
                district = ''
                city = ''
            else:
                district = location.get('district', '')
                city = location.get('city', '')
            
            self.mappings[temple_id] = {
                'findmytemple_id': temple_id,
                'findmytemple_name': temple_name,
                'db_id': db_id,
                'confidence': round(confidence, 2),
                'match_method': method,
                'district': district,
                'city': city
            }
            
            # Update statistics
            if method == 'exact_match':
                self.statistics['exact_matches'] += 1
            elif method == 'strong_match':
                self.statistics['strong_matches'] += 1
            elif method == 'good_match':
                self.statistics['good_matches'] += 1
            elif method == 'possible_match':
                self.statistics['possible_matches'] += 1
            elif method == 'weak_match':
                self.statistics['weak_matches'] += 1
            else:
                self.statistics['no_matches'] += 1
            
            # Progress indicator
            if i % 20 == 0:
                print(f"Processed {i}/{len(temples)} temples...")
        
        # Get DB temple name for matched temples
        for temple_id, mapping in self.mappings.items():
            if mapping['db_id']:
                cursor = self.conn.execute(
                    "SELECT name FROM temples WHERE temple_id = ?",
                    (mapping['db_id'],)
                )
                result = cursor.fetchone()
                if result:
                    mapping['db_name'] = result[0]
                else:
                    mapping['db_name'] = None
    
    def save_results(self):
        """Save mapping results to JSON"""
        
        output = {
            'metadata': {
                'generated_date': datetime.now().isoformat(),
                'source_file': 'findmytemple_master_scraped_data.json',
                'database': self.db_path,
                'total_processed': self.statistics['total_scraped']
            },
            'statistics': self.statistics,
            'match_distribution': {
                'excellent (90-100%)': self.statistics['exact_matches'] + self.statistics['strong_matches'],
                'good (80-89%)': self.statistics['good_matches'],
                'possible (70-79%)': self.statistics['possible_matches'],
                'weak (50-69%)': self.statistics['weak_matches'],
                'no_match (0-49%)': self.statistics['no_matches']
            },
            'mappings': self.mappings
        }
        
        with open('temple_id_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Mapping saved to: temple_id_mapping.json")
    
    def generate_validation_report(self):
        """Generate human-readable validation report"""
        
        report_lines = [
            "# Temple Matching Validation Report",
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## Summary Statistics\n",
            f"- **Total Temples Processed**: {self.statistics['total_scraped']}",
            f"- **Exact Matches**: {self.statistics['exact_matches']}",
            f"- **Strong Matches (90%+)**: {self.statistics['strong_matches']}",
            f"- **Good Matches (80-89%)**: {self.statistics['good_matches']}",
            f"- **Possible Matches (70-79%)**: {self.statistics['possible_matches']}",
            f"- **Weak Matches (50-69%)**: {self.statistics['weak_matches']}",
            f"- **No Matches**: {self.statistics['no_matches']}",
            "\n## Match Quality Distribution\n"
        ]
        
        # Calculate percentages
        total = self.statistics['total_scraped']
        if total > 0:
            report_lines.append(f"- Excellent (90-100%): {(self.statistics['exact_matches'] + self.statistics['strong_matches'])/total*100:.1f}%")
            report_lines.append(f"- Good (80-89%): {self.statistics['good_matches']/total*100:.1f}%")
            report_lines.append(f"- Possible (70-79%): {self.statistics['possible_matches']/total*100:.1f}%")
            report_lines.append(f"- Weak (50-69%): {self.statistics['weak_matches']/total*100:.1f}%")
            report_lines.append(f"- No Match: {self.statistics['no_matches']/total*100:.1f}%")
        
        # Sample matches from each category
        report_lines.append("\n## Sample Matches by Category\n")
        
        categories = {
            'exact_match': "### Exact Matches (Samples)",
            'strong_match': "### Strong Matches (Samples)",
            'good_match': "### Good Matches (Samples)",
            'possible_match': "### Possible Matches (Samples)",
            'no_match': "### No Matches (Samples)"
        }
        
        for method, title in categories.items():
            samples = [m for m in self.mappings.values() if m['match_method'] == method][:5]
            if samples:
                report_lines.append(f"\n{title}\n")
                for sample in samples:
                    report_lines.append(f"- **{sample['findmytemple_name']}** ({sample['findmytemple_id']})")
                    if sample['db_id']:
                        report_lines.append(f"  - Matched to: {sample.get('db_name', 'N/A')} ({sample['db_id']})")
                        report_lines.append(f"  - Confidence: {sample['confidence']}%")
                    else:
                        report_lines.append(f"  - No match found")
                    report_lines.append(f"  - District: {sample['district']}, City: {sample['city']}")
        
        # Write report
        with open('matching_validation_report.md', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print("✅ Validation report saved to: matching_validation_report.md")
    
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Main execution"""
    print("🔍 Temple Matching Process Starting...")
    print("=" * 60)
    
    mapper = TempleMapper()
    
    try:
        # Process all temples
        mapper.process_all_temples()
        
        # Save results
        mapper.save_results()
        
        # Generate report
        mapper.generate_validation_report()
        
        # Print summary
        print("\n📊 Matching Summary:")
        print(f"   Total Processed: {mapper.statistics['total_scraped']}")
        print(f"   Matched: {mapper.statistics['total_scraped'] - mapper.statistics['no_matches']}")
        print(f"   Unmatched: {mapper.statistics['no_matches']}")
        
    finally:
        mapper.close()
    
    print("\n✅ Temple matching complete!")


if __name__ == "__main__":
    main()