#!/usr/bin/env python3
"""
Improved Temple Matching Algorithm
===================================
Better matching logic since ALL temples exist in HRCE database
"""

import json
import sqlite3
import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple

class ImprovedTempleMapper:
    """Enhanced matching that accounts for common variations"""
    
    def __init__(self):
        self.conn = sqlite3.connect('../database/temples.db')
        self.conn.row_factory = sqlite3.Row
        
        # Common name variations in Tamil temple names
        self.name_variations = {
            'eswarar': ['easwaran', 'eswaran', 'eshwar', 'ishwar', 'sivan', 'shiva'],
            'perumal': ['vishnu', 'narayanan', 'narayana', 'venkatesa', 'krishna'],
            'amman': ['ambal', 'devi', 'shakti', 'mariamman', 'durga'],
            'murugan': ['subramanya', 'subramanian', 'karthikeya', 'kumaran', 'dandayudhapani'],
            'vinayagar': ['ganesh', 'ganesha', 'ganapathi', 'pillaiyar'],
            'ayyanar': ['sastha', 'sasta', 'ayyappan'],
        }
        
        # Common prefix/suffix variations
        self.prefixes = ['arulmigu', 'sri', 'shri', 'shree', 'thiru']
        self.suffixes = ['temple', 'kovil', 'koil', 'swamy', 'swami', 'samy', 'devasthanam', 'alayam']
        
    def normalize_name_advanced(self, name: str) -> str:
        """Advanced normalization handling Tamil transliterations"""
        if not name:
            return ""
        
        name = str(name).lower()
        
        # Remove common prefixes
        for prefix in self.prefixes:
            name = re.sub(f'^{prefix}\\s+', '', name)
        
        # Remove common suffixes
        for suffix in self.suffixes:
            name = re.sub(f'\\s+{suffix}$', '', name)
        
        # Normalize common variations
        name = name.replace('oo', 'u')  # Moorthy -> Murthy
        name = name.replace('aa', 'a')  # Raamanaathan -> Ramanathan
        name = name.replace('ee', 'i')  # Meenakshi -> Minakshi
        name = name.replace('th', 't')  # Nathar -> Natar
        name = name.replace('zh', 'l')  # Pazham -> Palam
        name = name.replace('sh', 's')  # Shiva -> Siva
        
        # Remove special characters
        name = re.sub(r'[^\w\s]', '', name)
        name = ' '.join(name.split())
        
        return name.strip()
    
    def get_deity_type(self, name: str, deity: str = '') -> str:
        """Determine deity type from temple name or deity field"""
        combined = f"{name} {deity}".lower()
        
        # Check for deity types
        if any(term in combined for term in ['sivan', 'swara', 'linga', 'natha', 'easwar', 'shiva']):
            return 'shiva'
        elif any(term in combined for term in ['perumal', 'vishnu', 'rama', 'krishna', 'narayana', 'venkat']):
            return 'vishnu'
        elif any(term in combined for term in ['amman', 'ambal', 'devi', 'mari', 'durga', 'kali']):
            return 'amman'
        elif any(term in combined for term in ['murugan', 'subra', 'karth', 'kumara', 'dandayu']):
            return 'murugan'
        elif any(term in combined for term in ['vinayag', 'ganes', 'ganapat', 'pillai']):
            return 'ganesha'
        else:
            return 'unknown'
    
    def find_matches_improved(self, scraped_temple: Dict) -> List[Dict]:
        """Improved matching with multiple strategies"""
        
        fmt_name = scraped_temple.get('name', '')
        location = scraped_temple.get('location', {})
        
        if isinstance(location, dict):
            district = location.get('district', '')
            city = location.get('city', '')
            pincode = location.get('pincode', '')
        else:
            district = ''
            city = ''
            pincode = ''
        
        deities = scraped_temple.get('deities', {})
        if isinstance(deities, dict):
            main_deity = deities.get('main_deity', '')
        else:
            main_deity = ''
        
        # Determine deity type
        deity_type = self.get_deity_type(fmt_name, main_deity)
        
        # Normalize names for comparison
        fmt_name_norm = self.normalize_name_advanced(fmt_name)
        
        matches = []
        
        # Strategy 1: Exact district + name similarity
        if district:
            query = """
            SELECT * FROM temples 
            WHERE district LIKE ? 
            ORDER BY name
            """
            cursor = self.conn.execute(query, (f'%{district}%',))
            
            for row in cursor:
                db_temple = dict(row)
                db_name_norm = self.normalize_name_advanced(db_temple['name'])
                
                # Calculate similarity
                name_sim = SequenceMatcher(None, fmt_name_norm, db_name_norm).ratio() * 100
                
                # Check deity type match
                db_deity_type = self.get_deity_type(db_temple['name'], db_temple.get('main_deity', ''))
                deity_match = (deity_type == db_deity_type) or deity_type == 'unknown' or db_deity_type == 'unknown'
                
                # Check location match
                location_match = False
                if city and db_temple.get('location'):
                    if city.lower() in db_temple['location'].lower():
                        location_match = True
                if city and db_temple.get('address'):
                    if city.lower() in db_temple['address'].lower():
                        location_match = True
                
                # Calculate final score
                score = name_sim * 0.5
                if deity_match:
                    score += 30
                if location_match:
                    score += 20
                
                if score > 40:  # Lower threshold to catch more matches
                    matches.append({
                        'temple_id': db_temple['temple_id'],
                        'name': db_temple['name'],
                        'district': db_temple['district'],
                        'location': db_temple.get('location', ''),
                        'address': db_temple.get('address', ''),
                        'main_deity': db_temple.get('main_deity', ''),
                        'score': score,
                        'name_similarity': name_sim,
                        'deity_match': deity_match,
                        'location_match': location_match
                    })
        
        # Strategy 2: If no good matches, try pincode
        if not matches and pincode:
            query = "SELECT * FROM temples WHERE pincode = ?"
            cursor = self.conn.execute(query, (pincode,))
            
            for row in cursor:
                db_temple = dict(row)
                db_name_norm = self.normalize_name_advanced(db_temple['name'])
                name_sim = SequenceMatcher(None, fmt_name_norm, db_name_norm).ratio() * 100
                
                if name_sim > 30:  # Lower threshold for pincode matches
                    matches.append({
                        'temple_id': db_temple['temple_id'],
                        'name': db_temple['name'],
                        'district': db_temple['district'],
                        'location': db_temple.get('location', ''),
                        'address': db_temple.get('address', ''),
                        'main_deity': db_temple.get('main_deity', ''),
                        'score': name_sim + 30,  # Bonus for pincode match
                        'name_similarity': name_sim,
                        'pincode_match': True
                    })
        
        # Strategy 3: Fuzzy search on name parts
        if not matches:
            # Extract key words from temple name
            key_words = [w for w in fmt_name_norm.split() if len(w) > 3]
            
            for word in key_words[:2]:  # Use first 2 significant words
                query = "SELECT * FROM temples WHERE name LIKE ? LIMIT 20"
                cursor = self.conn.execute(query, (f'%{word}%',))
                
                for row in cursor:
                    db_temple = dict(row)
                    db_name_norm = self.normalize_name_advanced(db_temple['name'])
                    
                    # Check if districts are same or neighboring
                    district_match = False
                    if district and db_temple.get('district'):
                        if district.lower() in db_temple['district'].lower():
                            district_match = True
                    
                    name_sim = SequenceMatcher(None, fmt_name_norm, db_name_norm).ratio() * 100
                    
                    if name_sim > 40 and district_match:
                        matches.append({
                            'temple_id': db_temple['temple_id'],
                            'name': db_temple['name'],
                            'district': db_temple['district'],
                            'location': db_temple.get('location', ''),
                            'address': db_temple.get('address', ''),
                            'main_deity': db_temple.get('main_deity', ''),
                            'score': name_sim,
                            'name_similarity': name_sim,
                            'fuzzy_match': True
                        })
        
        # Sort by score and return top 5
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:5]
    
    def process_all_temples(self):
        """Process with improved matching"""
        
        # Load scraped data
        with open('../findmytemple_master_scraped_data.json', 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
        
        temples = scraped_data['temples_scraped']
        
        results = {
            'high_confidence': [],  # >70%
            'medium_confidence': [],  # 50-70%
            'low_confidence': [],  # 30-50%
            'no_match': []  # <30%
        }
        
        print(f"Processing {len(temples)} temples with improved matching...")
        print("=" * 60)
        
        for i, temple in enumerate(temples, 1):
            matches = self.find_matches_improved(temple)
            
            if matches and matches[0]['score'] > 70:
                results['high_confidence'].append({
                    'findmytemple': temple,
                    'matches': matches
                })
            elif matches and matches[0]['score'] > 50:
                results['medium_confidence'].append({
                    'findmytemple': temple,
                    'matches': matches
                })
            elif matches and matches[0]['score'] > 30:
                results['low_confidence'].append({
                    'findmytemple': temple,
                    'matches': matches
                })
            else:
                results['no_match'].append({
                    'findmytemple': temple,
                    'matches': matches
                })
            
            if i % 50 == 0:
                print(f"Processed {i}/{len(temples)}...")
        
        # Save improved results
        with open('improved_matching_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "=" * 60)
        print("IMPROVED MATCHING RESULTS")
        print("=" * 60)
        print(f"High confidence (>70%): {len(results['high_confidence'])}")
        print(f"Medium confidence (50-70%): {len(results['medium_confidence'])}")
        print(f"Low confidence (30-50%): {len(results['low_confidence'])}")
        print(f"No match (<30%): {len(results['no_match'])}")
        
        # Show sample high confidence matches
        print("\nSample High Confidence Matches:")
        for item in results['high_confidence'][:5]:
            fmt = item['findmytemple']
            match = item['matches'][0]
            print(f"\n{fmt['name']} ({fmt.get('location', {}).get('district', '')})")
            print(f"  → {match['name']} ({match['district']})")
            print(f"  Score: {match['score']:.1f}%")
        
        return results

def main():
    mapper = ImprovedTempleMapper()
    results = mapper.process_all_temples()
    
    print("\n✅ Improved matching complete!")
    print("📄 Results saved to: improved_matching_results.json")
    
    # Calculate coverage for MVP
    total = 284
    matched = len(results['high_confidence']) + len(results['medium_confidence'])
    coverage = (matched / total) * 100
    
    print(f"\n🎯 MVP Coverage: {matched}/{total} temples ({coverage:.1f}%)")
    print(f"   This should be enough for MVP launch!")

if __name__ == "__main__":
    main()