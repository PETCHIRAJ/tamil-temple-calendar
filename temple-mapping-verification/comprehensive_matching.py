#!/usr/bin/env python3
"""
Comprehensive Temple Matching System
=====================================
Implements all 7 strategies to match ALL 284 temples
"""

import json
import sqlite3
import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional
import unicodedata

class ComprehensiveTempleMapper:
    """Implement all matching strategies systematically"""
    
    def __init__(self):
        self.conn = sqlite3.connect('../database/temples.db')
        self.conn.row_factory = sqlite3.Row
        
        # Load unmatched temples
        with open('location_fix_results.json', 'r') as f:
            self.data = json.load(f)
        
        self.unmatched = self.data['still_unmatched']
        
        # City to District mapping for Tamil Nadu
        self.city_to_district = {
            # Thanjavur District
            'kumbakonam': 'thanjavur',
            'thiruvidaimarudur': 'thanjavur',
            'papanasam': 'thanjavur',
            'thiruvaiyaru': 'thanjavur',
            'orathanadu': 'thanjavur',
            'pattukkottai': 'thanjavur',
            'peravurani': 'thanjavur',
            'kanjanur': 'thanjavur',
            'aduthurai': 'thanjavur',
            
            # Tiruchirappalli District
            'thiruverumbur': 'tiruchirappalli',
            'srirangam': 'tiruchirappalli',
            'lalgudi': 'tiruchirappalli',
            'manachanallur': 'tiruchirappalli',
            'musiri': 'tiruchirappalli',
            'thuraiyur': 'tiruchirappalli',
            'manapparai': 'tiruchirappalli',
            'uyyakondan thirumalai': 'tiruchirappalli',
            'thottiyam': 'tiruchirappalli',
            'perugamani': 'tiruchirappalli',
            'mandurai': 'tiruchirappalli',  # Not Madurai, but a place in Trichy
            
            # Nagapattinam District
            'nagapattinam': 'nagapattinam',
            'thirukkuvalai': 'nagapattinam',
            'keezhvelur': 'nagapattinam',
            'vedaranyam': 'nagapattinam',
            'mayiladuthurai': 'nagapattinam',  # Now separate district
            'sirkazhi': 'nagapattinam',
            'thirupugalur': 'nagapattinam',
            
            # Chennai District
            'mylapore': 'chennai',
            'triplicane': 'chennai',
            'george town': 'chennai',
            
            # Kanchipuram District
            'kanchipuram': 'kanchipuram',
            'sriperumbudur': 'kanchipuram',
            'chengalpattu': 'kanchipuram',
            
            # Add more as needed
        }
        
        # Famous temples lookup (temple_id to be verified)
        self.famous_temples = {
            'brihadiswara temple': 'Arulmigu Peruvudaiyar Temple',  # Thanjavur Big Temple
            'ekambareswarar temple': 'Arulmigu Ekambaranathar Temple',  # Kanchipuram
            'meenakshi amman temple': 'Arulmigu Meenakshi Sundareshwarar Temple',  # Madurai
            'ramanathaswamy temple': 'Arulmigu Ramanathaswamy Temple',  # Rameswaram
            'nataraja temple': 'Arulmigu Natarajar Temple',  # Chidambaram
            'thillai nataraja temple': 'Arulmigu Natarajar Temple',  # Chidambaram
            'arunachaleswarar temple': 'Arulmigu Arunachaleswarar Temple',  # Tiruvannamalai
            'jambukeswarar temple': 'Arulmigu Jambukeswarar Temple',  # Thiruvanaikaval
            'kapaleeshwarar temple': 'Arulmigu Kapaleeswarar Temple',  # Mylapore
        }
        
    def normalize_for_comparison(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        
        text = text.lower()
        
        # Remove common prefixes/suffixes
        remove_terms = [
            'arulmigu', 'sri', 'shri', 'shree', 'thiru', 'temple', 
            'kovil', 'koil', 'swamy', 'swami', 'samy', 'devasthanam'
        ]
        
        for term in remove_terms:
            text = re.sub(rf'\b{term}\b', '', text)
        
        # Normalize spaces
        text = ' '.join(text.split())
        return text.strip()
    
    def phonetic_normalize(self, text: str) -> str:
        """Phonetic normalization for Tamil-English variations"""
        if not text:
            return ""
        
        text = text.lower()
        
        # Common phonetic variations
        replacements = [
            ('aa', 'a'), ('ee', 'i'), ('oo', 'u'),
            ('th', 't'), ('dh', 'd'), ('bh', 'b'),
            ('sh', 's'), ('zh', 'l'), ('ch', 'c'),
            ('ksh', 'ks'), ('gn', 'n'), ('nj', 'n'),
            ('eswar', 'iswar'), ('eeswar', 'iswar'),
            ('eshwar', 'iswar'), ('easwar', 'iswar'),
            ('ambal', 'amman'), ('amma', 'amman'),
            ('perumal', 'perumal'), ('peruman', 'perumal'),
            ('vinayag', 'ganesh'), ('pillaiyar', 'ganesh'),
        ]
        
        for old, new in replacements:
            text = text.replace(old, new)
        
        return text
    
    # STRATEGY 1: Deity-Based Matching
    def match_by_deity(self, temple: Dict) -> List[Dict]:
        """Match temples by deity name"""
        
        deities = temple.get('deities', {})
        if isinstance(deities, dict):
            main_deity = deities.get('main_deity', '')
        else:
            main_deity = ''
        
        if not main_deity:
            return []
        
        # Extract core deity name
        deity_core = self.normalize_for_comparison(main_deity)
        deity_phonetic = self.phonetic_normalize(deity_core)
        
        matches = []
        
        # Search in main_deity field
        query = "SELECT * FROM temples WHERE main_deity IS NOT NULL"
        cursor = self.conn.execute(query)
        
        for row in cursor:
            db_temple = dict(row)
            db_deity = db_temple.get('main_deity', '')
            
            if not db_deity:
                continue
            
            db_deity_core = self.normalize_for_comparison(db_deity)
            db_deity_phonetic = self.phonetic_normalize(db_deity_core)
            
            # Calculate similarity
            direct_sim = SequenceMatcher(None, deity_core, db_deity_core).ratio() * 100
            phonetic_sim = SequenceMatcher(None, deity_phonetic, db_deity_phonetic).ratio() * 100
            
            max_sim = max(direct_sim, phonetic_sim)
            
            if max_sim > 60:  # Good deity match
                matches.append({
                    'temple_id': db_temple['temple_id'],
                    'name': db_temple['name'],
                    'district': db_temple['district'],
                    'main_deity': db_deity,
                    'score': max_sim,
                    'strategy': 'deity_match',
                    'confidence': 'high' if max_sim > 80 else 'medium'
                })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:3]
    
    # STRATEGY 2: City-to-District Mapping
    def match_with_city_mapping(self, temple: Dict) -> List[Dict]:
        """Fix city/district confusion and retry matching"""
        
        location = temple.get('location', {})
        if not isinstance(location, dict):
            return []
        
        city = location.get('city', '').lower()
        original_district = location.get('district', '').lower()
        
        # Check if city should be mapped to a district
        correct_district = self.city_to_district.get(city, '')
        
        if not correct_district and original_district:
            # Check if the district name is actually a city
            correct_district = self.city_to_district.get(original_district, original_district)
        
        if not correct_district:
            return []
        
        # Now search with correct district
        temple_name = temple.get('name', '')
        name_core = self.normalize_for_comparison(temple_name)
        
        matches = []
        
        query = "SELECT * FROM temples WHERE district LIKE ?"
        cursor = self.conn.execute(query, (f'%{correct_district}%',))
        
        for row in cursor:
            db_temple = dict(row)
            db_name = self.normalize_for_comparison(db_temple['name'])
            
            similarity = SequenceMatcher(None, name_core, db_name).ratio() * 100
            
            if similarity > 50:
                matches.append({
                    'temple_id': db_temple['temple_id'],
                    'name': db_temple['name'],
                    'district': db_temple['district'],
                    'location': db_temple.get('location', ''),
                    'score': similarity,
                    'strategy': 'city_mapping',
                    'confidence': 'high' if similarity > 70 else 'medium',
                    'corrected_district': correct_district
                })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:3]
    
    # STRATEGY 3: Famous Temple Lookup
    def match_famous_temples(self, temple: Dict) -> List[Dict]:
        """Match famous temples by known names"""
        
        temple_name = temple.get('name', '').lower()
        
        for famous_name, hrce_name in self.famous_temples.items():
            if famous_name in temple_name:
                # Search for the HRCE name
                query = "SELECT * FROM temples WHERE name LIKE ?"
                cursor = self.conn.execute(query, (f'%{hrce_name}%',))
                
                matches = []
                for row in cursor:
                    db_temple = dict(row)
                    matches.append({
                        'temple_id': db_temple['temple_id'],
                        'name': db_temple['name'],
                        'district': db_temple['district'],
                        'score': 95,  # High confidence for famous temples
                        'strategy': 'famous_temple',
                        'confidence': 'high',
                        'matched_as': famous_name
                    })
                
                return matches[:1]  # Return first match only
        
        return []
    
    # STRATEGY 4: Phonetic Matching
    def match_by_phonetics(self, temple: Dict) -> List[Dict]:
        """Match using phonetic similarity"""
        
        temple_name = temple.get('name', '')
        name_phonetic = self.phonetic_normalize(temple_name)
        
        if not name_phonetic:
            return []
        
        matches = []
        
        # Get all temples and compare phonetically
        query = "SELECT temple_id, name, district FROM temples"
        cursor = self.conn.execute(query)
        
        for row in cursor:
            db_temple = dict(row)
            db_phonetic = self.phonetic_normalize(db_temple['name'])
            
            similarity = SequenceMatcher(None, name_phonetic, db_phonetic).ratio() * 100
            
            if similarity > 65:  # Good phonetic match
                matches.append({
                    'temple_id': db_temple['temple_id'],
                    'name': db_temple['name'],
                    'district': db_temple['district'],
                    'score': similarity,
                    'strategy': 'phonetic',
                    'confidence': 'medium' if similarity > 75 else 'low'
                })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:3]
    
    # STRATEGY 5: Multi-Field Search
    def match_multi_field(self, temple: Dict) -> List[Dict]:
        """Search across multiple database fields"""
        
        temple_name = temple.get('name', '')
        
        # Extract key words
        words = [w for w in temple_name.split() if len(w) > 4]
        
        if not words:
            return []
        
        matches = []
        
        for word in words[:2]:  # Use first 2 significant words
            # Search in multiple fields
            query = """
            SELECT temple_id, name, district, tamil_name, raw_data 
            FROM temples 
            WHERE name LIKE ? 
               OR tamil_name LIKE ? 
               OR raw_data LIKE ?
            LIMIT 10
            """
            
            search_term = f'%{word}%'
            cursor = self.conn.execute(query, (search_term, search_term, search_term))
            
            for row in cursor:
                db_temple = dict(row)
                
                # Calculate match quality
                name_sim = SequenceMatcher(None, 
                    self.normalize_for_comparison(temple_name),
                    self.normalize_for_comparison(db_temple['name'])
                ).ratio() * 100
                
                if name_sim > 40:
                    matches.append({
                        'temple_id': db_temple['temple_id'],
                        'name': db_temple['name'],
                        'district': db_temple['district'],
                        'score': name_sim,
                        'strategy': 'multi_field',
                        'confidence': 'low',
                        'matched_in': 'name/tamil_name/raw_data'
                    })
        
        # Remove duplicates
        seen = set()
        unique_matches = []
        for m in matches:
            if m['temple_id'] not in seen:
                seen.add(m['temple_id'])
                unique_matches.append(m)
        
        unique_matches.sort(key=lambda x: x['score'], reverse=True)
        return unique_matches[:3]
    
    # STRATEGY 6: Generate Top Candidates
    def generate_candidates(self, temple: Dict) -> List[Dict]:
        """Generate top 3 candidates for manual review"""
        
        all_matches = []
        
        # Try all strategies
        strategies = [
            self.match_by_deity(temple),
            self.match_with_city_mapping(temple),
            self.match_famous_temples(temple),
            self.match_by_phonetics(temple),
            self.match_multi_field(temple)
        ]
        
        # Collect all unique matches
        seen = set()
        for strategy_matches in strategies:
            for match in strategy_matches:
                if match['temple_id'] not in seen:
                    seen.add(match['temple_id'])
                    all_matches.append(match)
        
        # Sort by score
        all_matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 3 unique candidates
        return all_matches[:3]
    
    def process_all_unmatched(self):
        """Process all unmatched temples with all strategies"""
        
        results = {
            'high_confidence': [],
            'medium_confidence': [],
            'low_confidence': [],
            'candidates_for_review': [],
            'no_match': []
        }
        
        print("🚀 Comprehensive Matching System")
        print("=" * 60)
        print(f"Processing {len(self.unmatched)} unmatched temples...\n")
        
        for i, temple in enumerate(self.unmatched, 1):
            temple_name = temple.get('name', '')
            
            # Get best matches from all strategies
            candidates = self.generate_candidates(temple)
            
            if candidates:
                best_match = candidates[0]
                
                if best_match['confidence'] == 'high' and best_match['score'] > 70:
                    results['high_confidence'].append({
                        'findmytemple': temple,
                        'match': best_match,
                        'alternatives': candidates[1:3]
                    })
                    print(f"✅ HIGH: {temple_name[:35]:<35} -> {best_match['name'][:35]:<35} "
                          f"({best_match['score']:.1f}% via {best_match['strategy']})")
                
                elif best_match['confidence'] == 'medium' and best_match['score'] > 60:
                    results['medium_confidence'].append({
                        'findmytemple': temple,
                        'match': best_match,
                        'alternatives': candidates[1:3]
                    })
                    print(f"⚠️  MED: {temple_name[:35]:<35} -> {best_match['name'][:35]:<35} "
                          f"({best_match['score']:.1f}% via {best_match['strategy']})")
                
                elif best_match['score'] > 40:
                    results['low_confidence'].append({
                        'findmytemple': temple,
                        'match': best_match,
                        'alternatives': candidates[1:3]
                    })
                    print(f"❓ LOW: {temple_name[:35]:<35} -> {best_match['name'][:35]:<35} "
                          f"({best_match['score']:.1f}% via {best_match['strategy']})")
                
                else:
                    results['candidates_for_review'].append({
                        'findmytemple': temple,
                        'candidates': candidates
                    })
                    print(f"👀 REV: {temple_name[:35]:<35} -> {len(candidates)} candidates for review")
            else:
                results['no_match'].append(temple)
                print(f"❌ NONE: {temple_name[:35]:<35} -> No matches found")
            
            if i % 20 == 0:
                print(f"\n[Progress: {i}/{len(self.unmatched)}]\n")
        
        # Save comprehensive results
        with open('comprehensive_matching_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
    
    def create_review_interface_data(self, results):
        """Create data for manual review interface"""
        
        review_data = []
        
        # Add low confidence matches for review
        for item in results['low_confidence']:
            review_data.append({
                'findmytemple': item['findmytemple'],
                'suggested_match': item['match'],
                'alternatives': item['alternatives'],
                'review_reason': 'low_confidence'
            })
        
        # Add candidates that need review
        for item in results['candidates_for_review']:
            review_data.append({
                'findmytemple': item['findmytemple'],
                'suggested_match': item['candidates'][0] if item['candidates'] else None,
                'alternatives': item['candidates'][1:3] if len(item['candidates']) > 1 else [],
                'review_reason': 'multiple_candidates'
            })
        
        # Add no matches
        for temple in results['no_match']:
            review_data.append({
                'findmytemple': temple,
                'suggested_match': None,
                'alternatives': [],
                'review_reason': 'no_match'
            })
        
        with open('manual_review_interface_data.json', 'w', encoding='utf-8') as f:
            json.dump(review_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 Created manual_review_interface_data.json with {len(review_data)} temples for review")

def main():
    mapper = ComprehensiveTempleMapper()
    results = mapper.process_all_unmatched()
    
    # Calculate statistics
    high = len(results['high_confidence'])
    medium = len(results['medium_confidence'])
    low = len(results['low_confidence'])
    review = len(results['candidates_for_review'])
    no_match = len(results['no_match'])
    
    # Previous matches
    previously_matched = 168
    
    # New matches (high + medium confidence)
    new_good_matches = high + medium
    total_matched = previously_matched + new_good_matches
    
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE MATCHING RESULTS")
    print("=" * 60)
    print(f"Previously matched: {previously_matched}")
    print(f"New HIGH confidence: {high}")
    print(f"New MEDIUM confidence: {medium}")
    print(f"Low confidence (need review): {low}")
    print(f"Multiple candidates (need review): {review}")
    print(f"No matches found: {no_match}")
    print("-" * 60)
    print(f"TOTAL GOOD MATCHES: {total_matched}/284 ({total_matched/284*100:.1f}%)")
    print(f"Need manual review: {low + review + no_match}")
    
    # Create review interface data
    if low + review + no_match > 0:
        mapper.create_review_interface_data(results)
        print("\n✅ Ready for manual review phase!")
    
    if total_matched >= 250:
        print("\n🎉 EXCELLENT! Over 88% matched automatically!")
    elif total_matched >= 200:
        print("\n✅ GOOD! Over 70% matched - ready for MVP!")
    
    mapper.conn.close()

if __name__ == "__main__":
    main()