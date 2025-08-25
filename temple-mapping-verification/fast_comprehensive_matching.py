#!/usr/bin/env python3
"""
Fast Comprehensive Matching with Temple Importance Analysis
============================================================
"""

import json
import sqlite3
import re
from difflib import SequenceMatcher
from typing import Dict, List

class FastComprehensiveMapper:
    def __init__(self):
        self.conn = sqlite3.connect('../database/temples.db')
        self.conn.row_factory = sqlite3.Row
        
        # Load unmatched temples
        with open('location_fix_results.json', 'r') as f:
            self.data = json.load(f)
        self.unmatched = self.data['still_unmatched']
        
        # Major temple indicators
        self.major_temple_keywords = [
            'brihadiswara', 'meenakshi', 'nataraja', 'ekambareswarar',
            'ramanathaswamy', 'arunachaleswarar', 'kapaleeshwarar',
            'jambukeswarar', 'parthasarathy', 'ranganatha',
            'murugan', 'palani', 'thiruchendur', 'swamimalai',
            'vadapalani', 'marudhamalai', 'alagarkoil', 'azhagarkoil',
            'navagraha', 'surya', 'chandra', 'angaraka', 'budha',
            'guru', 'sukra', 'sani', 'rahu', 'ketu'
        ]
        
        # City mapping
        self.city_to_district = {
            'kumbakonam': 'thanjavur',
            'kanjanur': 'thanjavur',
            'thiruverumbur': 'tiruchirappalli',
            'uyyakondan thirumalai': 'tiruchirappalli',
            'thottiyam': 'tiruchirappalli',
            'perugamani': 'tiruchirappalli',
            'thirupugalur': 'nagapattinam',
        }
    
    def is_major_temple(self, temple_name: str, deity: str = '') -> Dict:
        """Determine if this is a major/important temple"""
        
        combined = f"{temple_name} {deity}".lower()
        
        importance = {
            'is_major': False,
            'category': 'regular',
            'reason': []
        }
        
        # Check for major temple keywords
        for keyword in self.major_temple_keywords:
            if keyword in combined:
                importance['is_major'] = True
                importance['reason'].append(f"Contains '{keyword}' - known major temple")
                
                # Categorize
                if keyword in ['brihadiswara', 'meenakshi', 'nataraja', 'ekambareswarar']:
                    importance['category'] = 'unesco_heritage'
                elif keyword in ['murugan', 'palani', 'thiruchendur']:
                    importance['category'] = 'six_abodes_murugan'
                elif keyword in ['navagraha', 'surya', 'chandra', 'sani']:
                    importance['category'] = 'navagraha'
                else:
                    importance['category'] = 'major_pilgrimage'
                break
        
        # Check for Divya Desam (108 Vishnu temples)
        if 'perumal' in combined or 'vishnu' in combined or 'narayana' in combined:
            if any(term in combined for term in ['srirangam', 'tirupati', 'kanchipuram']):
                importance['is_major'] = True
                importance['category'] = 'divya_desam'
                importance['reason'].append("Divya Desam - 108 sacred Vishnu temples")
        
        # Check for Pancha Bhoota temples
        if any(term in combined for term in ['ekambareswarar', 'jambukeswarar', 'arunachaleswarar', 'nataraja', 'kalahasti']):
            importance['is_major'] = True
            importance['category'] = 'pancha_bhoota'
            importance['reason'].append("Pancha Bhoota Stalam - Five elements temple")
        
        # Check temple age/historical importance
        if any(term in combined for term in ['chola', 'pallava', 'pandya', '1000', 'ancient']):
            importance['is_major'] = True
            importance['category'] = 'historical'
            importance['reason'].append("Historical/Ancient temple")
        
        return importance
    
    def normalize(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        text = text.lower()
        for term in ['arulmigu', 'sri', 'shri', 'temple', 'kovil', 'swamy']:
            text = text.replace(term, '')
        return ' '.join(text.split()).strip()
    
    def quick_match_all(self):
        """Quick matching with all strategies"""
        
        results = []
        
        print("🚀 Fast Comprehensive Matching with Temple Importance Analysis")
        print("=" * 70)
        
        for i, temple in enumerate(self.unmatched, 1):
            temple_name = temple.get('name', '')
            location = temple.get('location', {})
            deities = temple.get('deities', {})
            
            # Extract deity
            if isinstance(deities, dict):
                main_deity = deities.get('main_deity', '')
            else:
                main_deity = ''
            
            # Check temple importance
            importance = self.is_major_temple(temple_name, main_deity)
            
            # Try to find matches
            best_match = None
            best_score = 0
            match_reason = []
            
            # Strategy 1: Search by core name
            core_name = self.normalize(temple_name)
            query = "SELECT * FROM temples WHERE name LIKE ? LIMIT 10"
            
            for word in core_name.split()[:2]:
                if len(word) > 4:
                    cursor = self.conn.execute(query, (f'%{word}%',))
                    for row in cursor:
                        db_temple = dict(row)
                        score = SequenceMatcher(None, core_name, self.normalize(db_temple['name'])).ratio() * 100
                        
                        if score > best_score:
                            best_score = score
                            best_match = db_temple
                            match_reason = [f"Name similarity: {score:.1f}%"]
            
            # Strategy 2: Search by deity if no good name match
            if best_score < 60 and main_deity:
                deity_core = self.normalize(main_deity)
                cursor = self.conn.execute(
                    "SELECT * FROM temples WHERE main_deity LIKE ? LIMIT 5",
                    (f'%{deity_core}%',)
                )
                for row in cursor:
                    db_temple = dict(row)
                    name_score = SequenceMatcher(None, core_name, self.normalize(db_temple['name'])).ratio() * 100
                    deity_score = SequenceMatcher(None, deity_core, self.normalize(db_temple.get('main_deity', ''))).ratio() * 100
                    combined_score = (name_score * 0.6) + (deity_score * 0.4)
                    
                    if combined_score > best_score:
                        best_score = combined_score
                        best_match = db_temple
                        match_reason = [
                            f"Name: {name_score:.1f}%",
                            f"Deity: {deity_score:.1f}%"
                        ]
            
            # Prepare result
            result = {
                'findmytemple': {
                    'id': temple.get('temple_id', ''),
                    'name': temple_name,
                    'location': location,
                    'deity': main_deity
                },
                'importance': importance,
                'match': None,
                'confidence': 'no_match',
                'reasoning': []
            }
            
            if best_match and best_score > 50:
                result['match'] = {
                    'temple_id': best_match['temple_id'],
                    'name': best_match['name'],
                    'district': best_match['district'],
                    'score': best_score
                }
                
                # Determine confidence
                if best_score > 80:
                    result['confidence'] = 'high'
                elif best_score > 65:
                    result['confidence'] = 'medium'
                else:
                    result['confidence'] = 'low'
                
                result['reasoning'] = match_reason
                
                # Print result
                status = "✅" if result['confidence'] == 'high' else "⚠️" if result['confidence'] == 'medium' else "❓"
                major = "⭐ MAJOR" if importance['is_major'] else ""
                
                print(f"{status} {temple_name[:35]:<35} -> {best_match['name'][:35]:<35} ({best_score:.1f}%) {major}")
                if importance['is_major']:
                    print(f"   Category: {importance['category']} - {importance['reason'][0]}")
            else:
                print(f"❌ {temple_name[:35]:<35} -> No match found")
                if importance['is_major']:
                    print(f"   ⚠️ IMPORTANT: This is a {importance['category']} temple!")
            
            results.append(result)
        
        return results

def main():
    mapper = FastComprehensiveMapper()
    results = mapper.quick_match_all()
    
    # Analyze results
    total = len(results)
    high_conf = sum(1 for r in results if r['confidence'] == 'high')
    medium_conf = sum(1 for r in results if r['confidence'] == 'medium')
    low_conf = sum(1 for r in results if r['confidence'] == 'low')
    no_match = sum(1 for r in results if r['confidence'] == 'no_match')
    
    major_temples = sum(1 for r in results if r['importance']['is_major'])
    major_matched = sum(1 for r in results if r['importance']['is_major'] and r['match'])
    
    # Save results
    with open('final_matching_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("📊 FINAL MATCHING RESULTS")
    print("=" * 70)
    print(f"Total unmatched temples processed: {total}")
    print(f"  High confidence: {high_conf}")
    print(f"  Medium confidence: {medium_conf}")
    print(f"  Low confidence: {low_conf}")
    print(f"  No match: {no_match}")
    print(f"\n⭐ Major temples: {major_temples}")
    print(f"  Major temples matched: {major_matched}")
    print(f"  Major temples unmatched: {major_temples - major_matched}")
    
    # Previous totals
    previously_matched = 168
    new_good_matches = high_conf + medium_conf
    total_matched = previously_matched + new_good_matches
    
    print(f"\n🎯 TOTAL COVERAGE:")
    print(f"  Previously matched: {previously_matched}")
    print(f"  New matches (high+medium): {new_good_matches}")
    print(f"  TOTAL: {total_matched}/284 ({total_matched/284*100:.1f}%)")
    
    mapper.conn.close()

if __name__ == "__main__":
    main()