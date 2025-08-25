#!/usr/bin/env python3
"""
Aggressive Temple Matching
===========================
Find ALL 284 temples in HRCE database using multiple strategies
"""

import json
import sqlite3
import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional

class AggressiveTempleMapper:
    """Use every possible strategy to find matches"""
    
    def __init__(self):
        self.conn = sqlite3.connect('../database/temples.db')
        self.conn.row_factory = sqlite3.Row
        
        # Load unmatched temples
        with open('location_fix_results.json', 'r') as f:
            self.data = json.load(f)
        
        self.unmatched = self.data['still_unmatched']
        
    def aggressive_normalize(self, text: str) -> str:
        """Extremely aggressive normalization"""
        if not text:
            return ""
        
        text = text.lower()
        
        # Remove ALL common words
        remove_words = [
            'arulmigu', 'sri', 'shri', 'shree', 'thiru', 'temple', 'kovil', 
            'koil', 'swamy', 'swami', 'samy', 'devasthanam', 'alayam',
            'the', 'and', 'of', 'in', 'at', 'tiru', 'amman', 'perumal'
        ]
        
        for word in remove_words:
            text = text.replace(word, ' ')
        
        # Normalize variations
        text = re.sub(r'[^a-z0-9\s]', '', text)  # Remove all special chars
        text = text.replace('aa', 'a')
        text = text.replace('ee', 'i')
        text = text.replace('oo', 'u')
        text = text.replace('th', 't')
        text = text.replace('sh', 's')
        text = text.replace('zh', 'l')
        text = text.replace('ksh', 'ks')
        text = text.replace('gn', 'n')
        
        # Remove duplicate letters
        text = re.sub(r'(.)\1+', r'\1', text)
        
        # Get core words only
        words = [w for w in text.split() if len(w) > 2]
        return ' '.join(words[:3])  # Use first 3 core words
    
    def find_by_core_name(self, temple_name: str) -> List[Dict]:
        """Match by core name components"""
        
        core_name = self.aggressive_normalize(temple_name)
        if not core_name:
            return []
        
        matches = []
        
        # Get all temples and compare
        cursor = self.conn.execute("SELECT * FROM temples")
        
        for row in cursor:
            db_temple = dict(row)
            db_core = self.aggressive_normalize(db_temple['name'])
            
            if not db_core:
                continue
            
            # Check if any core word matches
            fmt_words = set(core_name.split())
            db_words = set(db_core.split())
            
            common_words = fmt_words & db_words
            
            if len(common_words) >= 1:  # At least 1 core word match
                # Calculate match score
                word_match_ratio = len(common_words) / max(len(fmt_words), len(db_words))
                similarity = SequenceMatcher(None, core_name, db_core).ratio()
                
                score = (word_match_ratio * 50) + (similarity * 50)
                
                if score > 30:  # Very low threshold
                    matches.append({
                        'temple_id': db_temple['temple_id'],
                        'name': db_temple['name'],
                        'district': db_temple['district'],
                        'score': score,
                        'core_match': f"{core_name} ~ {db_core}",
                        'common_words': list(common_words)
                    })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:5]
    
    def find_by_deity_and_location(self, temple: Dict) -> List[Dict]:
        """Match by deity name and approximate location"""
        
        deities = temple.get('deities', {})
        if isinstance(deities, dict):
            main_deity = deities.get('main_deity', '')
        else:
            main_deity = ''
        
        if not main_deity:
            return []
        
        # Extract deity core name
        deity_core = self.aggressive_normalize(main_deity)
        
        matches = []
        
        # Search for temples with similar deity
        query = "SELECT * FROM temples WHERE main_deity IS NOT NULL"
        cursor = self.conn.execute(query)
        
        for row in cursor:
            db_temple = dict(row)
            db_deity = db_temple.get('main_deity', '')
            
            if not db_deity:
                continue
            
            db_deity_core = self.aggressive_normalize(db_deity)
            
            # Check deity similarity
            if deity_core and db_deity_core:
                deity_sim = SequenceMatcher(None, deity_core, db_deity_core).ratio() * 100
                
                if deity_sim > 50:  # Deity matches
                    # Also check name similarity
                    name_sim = SequenceMatcher(None, 
                        self.aggressive_normalize(temple['name']),
                        self.aggressive_normalize(db_temple['name'])
                    ).ratio() * 100
                    
                    score = (deity_sim * 0.4) + (name_sim * 0.6)
                    
                    if score > 40:
                        matches.append({
                            'temple_id': db_temple['temple_id'],
                            'name': db_temple['name'],
                            'district': db_temple['district'],
                            'main_deity': db_temple.get('main_deity', ''),
                            'score': score,
                            'deity_match': f"{main_deity} ~ {db_deity}"
                        })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:5]
    
    def find_by_unique_words(self, temple_name: str) -> List[Dict]:
        """Find by unique/rare words in temple name"""
        
        # Extract potentially unique words (not common temple words)
        common_words = {'sri', 'temple', 'kovil', 'swamy', 'perumal', 'amman', 'murugan'}
        
        words = temple_name.lower().split()
        unique_words = [w for w in words if len(w) > 4 and w not in common_words]
        
        if not unique_words:
            return []
        
        matches = []
        
        for word in unique_words:
            # Search for this unique word
            query = "SELECT * FROM temples WHERE name LIKE ? LIMIT 20"
            cursor = self.conn.execute(query, (f'%{word}%',))
            
            for row in cursor:
                db_temple = dict(row)
                
                # Calculate similarity
                name_sim = SequenceMatcher(None,
                    temple_name.lower(),
                    db_temple['name'].lower()
                ).ratio() * 100
                
                if name_sim > 35:  # Very low threshold
                    matches.append({
                        'temple_id': db_temple['temple_id'],
                        'name': db_temple['name'],
                        'district': db_temple['district'],
                        'score': name_sim,
                        'matched_word': word
                    })
        
        # Remove duplicates and sort
        seen = set()
        unique_matches = []
        for m in matches:
            if m['temple_id'] not in seen:
                seen.add(m['temple_id'])
                unique_matches.append(m)
        
        unique_matches.sort(key=lambda x: x['score'], reverse=True)
        return unique_matches[:5]
    
    def find_by_partial_match(self, temple_name: str) -> List[Dict]:
        """Find by matching first few characters of main word"""
        
        # Get the main distinguishing word
        words = temple_name.replace('Temple', '').replace('Kovil', '').split()
        main_words = [w for w in words if len(w) > 5]  # Longer words are more unique
        
        if not main_words:
            main_words = [w for w in words if len(w) > 3]
        
        if not main_words:
            return []
        
        matches = []
        
        for word in main_words[:2]:  # Use first 2 main words
            prefix = word[:4].lower()  # First 4 characters
            
            query = "SELECT * FROM temples WHERE LOWER(name) LIKE ?"
            cursor = self.conn.execute(query, (f'%{prefix}%',))
            
            for row in cursor:
                db_temple = dict(row)
                
                # Check if prefix appears in a similar position
                db_name_lower = db_temple['name'].lower()
                if prefix in db_name_lower:
                    # Calculate positional similarity
                    fmt_pos = temple_name.lower().find(prefix)
                    db_pos = db_name_lower.find(prefix)
                    
                    pos_diff = abs(fmt_pos - db_pos)
                    pos_score = max(0, 100 - pos_diff * 5)  # Penalty for position difference
                    
                    # Overall name similarity
                    name_sim = SequenceMatcher(None,
                        self.aggressive_normalize(temple_name),
                        self.aggressive_normalize(db_temple['name'])
                    ).ratio() * 100
                    
                    score = (pos_score * 0.3) + (name_sim * 0.7)
                    
                    if score > 30:
                        matches.append({
                            'temple_id': db_temple['temple_id'],
                            'name': db_temple['name'],
                            'district': db_temple['district'],
                            'score': score,
                            'prefix_match': prefix
                        })
        
        # Remove duplicates
        seen = set()
        unique_matches = []
        for m in matches:
            if m['temple_id'] not in seen:
                seen.add(m['temple_id'])
                unique_matches.append(m)
        
        unique_matches.sort(key=lambda x: x['score'], reverse=True)
        return unique_matches[:5]
    
    def process_remaining_temples(self):
        """Try every strategy to match remaining temples"""
        
        final_matches = []
        still_no_match = []
        
        print("🔥 Aggressive Matching for Remaining Temples")
        print("=" * 60)
        
        for temple in self.unmatched:
            temple_name = temple['name']
            matched = False
            
            # Try all strategies
            strategies = [
                ('core_name', self.find_by_core_name(temple_name)),
                ('deity_location', self.find_by_deity_and_location(temple)),
                ('unique_words', self.find_by_unique_words(temple_name)),
                ('partial_match', self.find_by_partial_match(temple_name))
            ]
            
            # Collect all matches
            all_matches = {}
            for strategy_name, matches in strategies:
                for match in matches:
                    tid = match['temple_id']
                    if tid not in all_matches or match['score'] > all_matches[tid]['score']:
                        all_matches[tid] = {
                            **match,
                            'strategy': strategy_name
                        }
            
            # Get best match
            if all_matches:
                best_match = max(all_matches.values(), key=lambda x: x['score'])
                
                if best_match['score'] > 35:  # Very low threshold
                    final_matches.append({
                        'findmytemple': temple,
                        'match': best_match
                    })
                    matched = True
                    
                    print(f"✅ {temple_name[:35]:<35} -> {best_match['name'][:35]:<35} "
                          f"({best_match['score']:.1f}% via {best_match['strategy']})")
            
            if not matched:
                still_no_match.append(temple)
                print(f"❌ {temple_name[:35]:<35} -> No match found")
        
        # Save results
        results = {
            'aggressive_matches': final_matches,
            'still_unmatched': still_no_match,
            'summary': {
                'matched': len(final_matches),
                'unmatched': len(still_no_match)
            }
        }
        
        with open('aggressive_matching_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
    
    def create_manual_review_file(self, unmatched):
        """Create a file for manual matching of remaining temples"""
        
        review_data = []
        
        for temple in unmatched:
            # Get top 10 potential matches regardless of score
            all_candidates = []
            
            # Search by any part of name
            words = temple['name'].split()
            for word in words:
                if len(word) > 3:
                    query = "SELECT * FROM temples WHERE name LIKE ? LIMIT 5"
                    cursor = self.conn.execute(query, (f'%{word}%',))
                    for row in cursor:
                        db_temple = dict(row)
                        all_candidates.append({
                            'temple_id': db_temple['temple_id'],
                            'name': db_temple['name'],
                            'district': db_temple['district'],
                            'location': db_temple.get('location', '')
                        })
            
            # Remove duplicates
            seen = set()
            candidates = []
            for c in all_candidates:
                if c['temple_id'] not in seen:
                    seen.add(c['temple_id'])
                    candidates.append(c)
            
            review_data.append({
                'findmytemple': temple,
                'potential_matches': candidates[:10]
            })
        
        with open('manual_review_needed.json', 'w', encoding='utf-8') as f:
            json.dump(review_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 Created manual_review_needed.json with {len(review_data)} temples")
        print("   These need human verification to find correct matches")

def main():
    mapper = AggressiveTempleMapper()
    results = mapper.process_remaining_temples()
    
    # Calculate final statistics
    previously_matched = 168
    new_matches = results['summary']['matched']
    total_matched = previously_matched + new_matches
    still_unmatched = results['summary']['unmatched']
    
    print("\n" + "=" * 60)
    print("📊 FINAL MATCHING RESULTS")
    print("=" * 60)
    print(f"Previously matched: {previously_matched}")
    print(f"New aggressive matches: {new_matches}")
    print(f"TOTAL MATCHED: {total_matched}/284 ({total_matched/284*100:.1f}%)")
    print(f"Still unmatched: {still_unmatched}")
    
    if still_unmatched > 0:
        print(f"\n⚠️ Creating manual review file for {still_unmatched} temples...")
        mapper.create_manual_review_file(results['still_unmatched'])
    
    if total_matched >= 250:
        print("\n🎉 EXCELLENT! Over 88% matched - definitely ready for MVP!")
    elif total_matched >= 200:
        print("\n✅ GOOD! Over 70% matched - solid for MVP launch!")
    
    mapper.conn.close()

if __name__ == "__main__":
    main()