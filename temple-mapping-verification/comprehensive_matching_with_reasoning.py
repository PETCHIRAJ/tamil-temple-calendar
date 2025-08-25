#!/usr/bin/env python3
"""
Comprehensive Temple Matching with Detailed Reasoning
======================================================
Provides clear explanations for why each match was selected
"""

import json
import sqlite3
import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional

class ReasonedTempleMapper:
    """Temple matching with detailed reasoning for verification"""
    
    def __init__(self):
        self.conn = sqlite3.connect('../database/temples.db')
        self.conn.row_factory = sqlite3.Row
        
        # Load unmatched temples
        with open('location_fix_results.json', 'r') as f:
            self.data = json.load(f)
        
        self.unmatched = self.data['still_unmatched']
        
        # City to District mapping
        self.city_to_district = {
            'kumbakonam': 'thanjavur',
            'thiruvidaimarudur': 'thanjavur',
            'kanjanur': 'thanjavur',
            'aduthurai': 'thanjavur',
            'thiruverumbur': 'tiruchirappalli',
            'srirangam': 'tiruchirappalli',
            'uyyakondan thirumalai': 'tiruchirappalli',
            'thottiyam': 'tiruchirappalli',
            'perugamani': 'tiruchirappalli',
            'mandurai': 'tiruchirappalli',
            'thirupugalur': 'nagapattinam',
            'mylapore': 'chennai',
            'kanchipuram': 'kanchipuram',
        }
        
        self.famous_temples = {
            'brihadiswara': 'Peruvudaiyar',
            'ekambareswarar': 'Ekambaranathar',
            'meenakshi': 'Meenakshi Sundareshwarar',
            'kapaleeshwarar': 'Kapaleeswarar',
            'nataraja': 'Natarajar',
        }
    
    def generate_match_reasoning(self, fmt_temple: Dict, db_temple: Dict, 
                                 match_type: str, score: float) -> Dict:
        """Generate detailed reasoning for why this match was selected"""
        
        reasoning = {
            'match_confidence': 'high' if score > 75 else 'medium' if score > 60 else 'low',
            'match_score': round(score, 1),
            'match_method': match_type,
            'evidence': [],
            'concerns': [],
            'recommendation': ''
        }
        
        # Extract data for comparison
        fmt_name = fmt_temple.get('name', '')
        fmt_location = fmt_temple.get('location', {})
        fmt_deity = fmt_temple.get('deities', {})
        
        db_name = db_temple.get('name', '')
        db_district = db_temple.get('district', '')
        db_deity = db_temple.get('main_deity', '')
        
        # Name comparison
        name_sim = SequenceMatcher(None, 
            self.normalize(fmt_name), 
            self.normalize(db_name)
        ).ratio() * 100
        
        if name_sim > 80:
            reasoning['evidence'].append(f"✅ Strong name match ({name_sim:.0f}% similar)")
        elif name_sim > 60:
            reasoning['evidence'].append(f"⚠️ Moderate name match ({name_sim:.0f}% similar)")
        else:
            reasoning['concerns'].append(f"❌ Weak name match ({name_sim:.0f}% similar)")
        
        # Location comparison
        if isinstance(fmt_location, dict):
            fmt_district = fmt_location.get('district', '')
            fmt_city = fmt_location.get('city', '')
            
            if fmt_district and db_district:
                if self.normalize(fmt_district) in self.normalize(db_district):
                    reasoning['evidence'].append(f"✅ District matches: {fmt_district} = {db_district}")
                else:
                    # Check city mapping
                    mapped_district = self.city_to_district.get(fmt_city.lower(), '')
                    if mapped_district and mapped_district in db_district.lower():
                        reasoning['evidence'].append(f"✅ City '{fmt_city}' is in {db_district} district")
                    else:
                        reasoning['concerns'].append(f"⚠️ District mismatch: {fmt_district} ≠ {db_district}")
        
        # Deity comparison
        if isinstance(fmt_deity, dict):
            fmt_main_deity = fmt_deity.get('main_deity', '')
            if fmt_main_deity and db_deity:
                deity_sim = SequenceMatcher(None,
                    self.normalize(fmt_main_deity),
                    self.normalize(db_deity)
                ).ratio() * 100
                
                if deity_sim > 70:
                    reasoning['evidence'].append(f"✅ Deity matches: {fmt_main_deity} ≈ {db_deity}")
                elif deity_sim > 50:
                    reasoning['evidence'].append(f"⚠️ Deity partially matches: {fmt_main_deity} ~ {db_deity}")
        
        # Match type specific reasoning
        if match_type == 'deity_match':
            reasoning['evidence'].append("🕉️ Matched primarily by deity name")
            reasoning['explanation'] = "The unique deity name strongly indicates this is the same temple"
        
        elif match_type == 'city_mapping':
            reasoning['evidence'].append("📍 Matched by correcting city/district confusion")
            reasoning['explanation'] = f"'{fmt_city}' is actually in {db_district} district"
        
        elif match_type == 'famous_temple':
            reasoning['evidence'].append("🏛️ Matched as a famous temple")
            reasoning['explanation'] = "This is a well-known temple with name variations"
        
        elif match_type == 'phonetic':
            reasoning['evidence'].append("🔤 Matched by phonetic similarity")
            reasoning['explanation'] = "Tamil-English transliteration variations detected"
        
        elif match_type == 'multi_field':
            reasoning['evidence'].append("🔍 Found in multiple database fields")
            reasoning['explanation'] = "Match found in tamil_name or raw_data fields"
        
        # Generate recommendation
        evidence_count = len(reasoning['evidence'])
        concern_count = len(reasoning['concerns'])
        
        if score > 80 and evidence_count > concern_count * 2:
            reasoning['recommendation'] = "✅ APPROVE - Strong match with multiple evidence"
        elif score > 70 and evidence_count > concern_count:
            reasoning['recommendation'] = "✅ APPROVE - Good match with sufficient evidence"
        elif score > 60:
            reasoning['recommendation'] = "⚠️ REVIEW - Moderate match, verify details"
        elif score > 50:
            reasoning['recommendation'] = "❓ UNCERTAIN - Weak match, careful review needed"
        else:
            reasoning['recommendation'] = "❌ REJECT - Poor match, likely different temple"
        
        return reasoning
    
    def normalize(self, text: str) -> str:
        """Basic normalization for comparison"""
        if not text:
            return ""
        text = text.lower()
        # Remove common prefixes/suffixes
        for term in ['arulmigu', 'sri', 'shri', 'temple', 'kovil', 'swamy']:
            text = text.replace(term, '')
        return ' '.join(text.split()).strip()
    
    def process_with_reasoning(self):
        """Process all unmatched temples and provide detailed reasoning"""
        
        # Load the comprehensive matching results
        try:
            with open('comprehensive_matching_results.json', 'r') as f:
                comp_results = json.load(f)
        except:
            print("❌ Please run comprehensive_matching.py first to generate matches")
            return None
        
        verification_data = {
            'high_confidence_matches': [],
            'medium_confidence_matches': [],
            'review_required': [],
            'summary': {
                'total_processed': 0,
                'high_confidence': 0,
                'medium_confidence': 0,
                'needs_review': 0
            }
        }
        
        print("📝 Generating Verification Report with Reasoning")
        print("=" * 60)
        
        # Process high confidence matches
        for item in comp_results.get('high_confidence', []):
            fmt_temple = item['findmytemple']
            match = item['match']
            
            # Get full DB temple details
            cursor = self.conn.execute(
                "SELECT * FROM temples WHERE temple_id = ?", 
                (match['temple_id'],)
            )
            db_temple = dict(cursor.fetchone()) if cursor else {}
            
            reasoning = self.generate_match_reasoning(
                fmt_temple, db_temple, 
                match.get('strategy', 'unknown'),
                match.get('score', 0)
            )
            
            verification_entry = {
                'findmytemple': {
                    'id': fmt_temple.get('temple_id', ''),
                    'name': fmt_temple.get('name', ''),
                    'location': fmt_temple.get('location', {}),
                    'deities': fmt_temple.get('deities', {})
                },
                'matched_to': {
                    'temple_id': match['temple_id'],
                    'name': match['name'],
                    'district': match['district'],
                    'main_deity': db_temple.get('main_deity', '')
                },
                'reasoning': reasoning,
                'alternatives': item.get('alternatives', [])
            }
            
            verification_data['high_confidence_matches'].append(verification_entry)
            
            # Print summary
            print(f"✅ {fmt_temple['name'][:40]:<40} -> {match['name'][:40]:<40}")
            print(f"   Reason: {reasoning['explanation']}")
            print(f"   Evidence: {', '.join(reasoning['evidence'][:2])}")
            print()
        
        # Process medium confidence matches
        for item in comp_results.get('medium_confidence', []):
            fmt_temple = item['findmytemple']
            match = item['match']
            
            cursor = self.conn.execute(
                "SELECT * FROM temples WHERE temple_id = ?", 
                (match['temple_id'],)
            )
            db_temple = dict(cursor.fetchone()) if cursor else {}
            
            reasoning = self.generate_match_reasoning(
                fmt_temple, db_temple,
                match.get('strategy', 'unknown'),
                match.get('score', 0)
            )
            
            verification_entry = {
                'findmytemple': {
                    'id': fmt_temple.get('temple_id', ''),
                    'name': fmt_temple.get('name', ''),
                    'location': fmt_temple.get('location', {}),
                    'deities': fmt_temple.get('deities', {})
                },
                'matched_to': {
                    'temple_id': match['temple_id'],
                    'name': match['name'],
                    'district': match['district'],
                    'main_deity': db_temple.get('main_deity', '')
                },
                'reasoning': reasoning,
                'alternatives': item.get('alternatives', [])
            }
            
            verification_data['medium_confidence_matches'].append(verification_entry)
            
            print(f"⚠️  {fmt_temple['name'][:40]:<40} -> {match['name'][:40]:<40}")
            print(f"   Reason: {reasoning['explanation']}")
            if reasoning['concerns']:
                print(f"   Concerns: {reasoning['concerns'][0]}")
            print()
        
        # Process items needing review
        for item in comp_results.get('low_confidence', []) + comp_results.get('candidates_for_review', []):
            if 'findmytemple' in item:
                fmt_temple = item['findmytemple']
                
                candidates = []
                if 'match' in item:
                    candidates = [item['match']] + item.get('alternatives', [])
                elif 'candidates' in item:
                    candidates = item['candidates']
                
                # Generate reasoning for each candidate
                candidates_with_reasoning = []
                for candidate in candidates[:3]:
                    cursor = self.conn.execute(
                        "SELECT * FROM temples WHERE temple_id = ?",
                        (candidate['temple_id'],)
                    )
                    db_temple = dict(cursor.fetchone()) if cursor else {}
                    
                    reasoning = self.generate_match_reasoning(
                        fmt_temple, db_temple,
                        candidate.get('strategy', 'unknown'),
                        candidate.get('score', 0)
                    )
                    
                    candidates_with_reasoning.append({
                        'temple': {
                            'temple_id': candidate['temple_id'],
                            'name': candidate['name'],
                            'district': candidate['district']
                        },
                        'reasoning': reasoning
                    })
                
                verification_data['review_required'].append({
                    'findmytemple': {
                        'id': fmt_temple.get('temple_id', ''),
                        'name': fmt_temple.get('name', ''),
                        'location': fmt_temple.get('location', {}),
                        'deities': fmt_temple.get('deities', {})
                    },
                    'candidates': candidates_with_reasoning
                })
        
        # Update summary
        verification_data['summary']['high_confidence'] = len(verification_data['high_confidence_matches'])
        verification_data['summary']['medium_confidence'] = len(verification_data['medium_confidence_matches'])
        verification_data['summary']['needs_review'] = len(verification_data['review_required'])
        verification_data['summary']['total_processed'] = sum([
            verification_data['summary']['high_confidence'],
            verification_data['summary']['medium_confidence'],
            verification_data['summary']['needs_review']
        ])
        
        # Save verification data
        with open('verification_with_reasoning.json', 'w', encoding='utf-8') as f:
            json.dump(verification_data, f, indent=2, ensure_ascii=False)
        
        # Create markdown report
        self.create_markdown_report(verification_data)
        
        return verification_data
    
    def create_markdown_report(self, data):
        """Create a readable markdown report for verification"""
        
        with open('verification_report.md', 'w', encoding='utf-8') as f:
            f.write("# Temple Matching Verification Report\n\n")
            f.write(f"Generated: {json.dumps(None, default=str)}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **High Confidence Matches**: {data['summary']['high_confidence']}\n")
            f.write(f"- **Medium Confidence Matches**: {data['summary']['medium_confidence']}\n")
            f.write(f"- **Needs Manual Review**: {data['summary']['needs_review']}\n")
            f.write(f"- **Total Processed**: {data['summary']['total_processed']}\n\n")
            
            f.write("## High Confidence Matches\n\n")
            f.write("These matches have strong evidence and can likely be auto-approved:\n\n")
            
            for i, item in enumerate(data['high_confidence_matches'][:10], 1):
                fmt = item['findmytemple']
                match = item['matched_to']
                reasoning = item['reasoning']
                
                f.write(f"### {i}. {fmt['name']}\n\n")
                f.write(f"**Matched to**: {match['name']} ({match['temple_id']})\n\n")
                f.write(f"**Score**: {reasoning['match_score']}% | ")
                f.write(f"**Method**: {reasoning['match_method']}\n\n")
                f.write(f"**Evidence**:\n")
                for evidence in reasoning['evidence']:
                    f.write(f"- {evidence}\n")
                f.write(f"\n**Recommendation**: {reasoning['recommendation']}\n\n")
                f.write("---\n\n")
            
            f.write("## Medium Confidence Matches\n\n")
            f.write("These matches need verification but are likely correct:\n\n")
            
            for i, item in enumerate(data['medium_confidence_matches'][:10], 1):
                fmt = item['findmytemple']
                match = item['matched_to']
                reasoning = item['reasoning']
                
                f.write(f"### {i}. {fmt['name']}\n\n")
                f.write(f"**Matched to**: {match['name']} ({match['temple_id']})\n\n")
                f.write(f"**Score**: {reasoning['match_score']}% | ")
                f.write(f"**Method**: {reasoning['match_method']}\n\n")
                
                if reasoning['evidence']:
                    f.write(f"**Evidence**:\n")
                    for evidence in reasoning['evidence']:
                        f.write(f"- {evidence}\n")
                
                if reasoning['concerns']:
                    f.write(f"\n**Concerns**:\n")
                    for concern in reasoning['concerns']:
                        f.write(f"- {concern}\n")
                
                f.write(f"\n**Recommendation**: {reasoning['recommendation']}\n\n")
                f.write("---\n\n")
        
        print(f"\n📄 Verification report saved to: verification_report.md")

def main():
    mapper = ReasonedTempleMapper()
    verification_data = mapper.process_with_reasoning()
    
    if verification_data:
        print("\n" + "=" * 60)
        print("✅ Verification data with reasoning generated!")
        print(f"   High confidence: {verification_data['summary']['high_confidence']}")
        print(f"   Medium confidence: {verification_data['summary']['medium_confidence']}")
        print(f"   Needs review: {verification_data['summary']['needs_review']}")
        print("\nFiles created:")
        print("   - verification_with_reasoning.json (full data)")
        print("   - verification_report.md (readable report)")
    
    mapper.conn.close()

if __name__ == "__main__":
    # Note: Run comprehensive_matching.py first to generate matches
    print("⚠️  Make sure to run comprehensive_matching.py first!")
    print("Then run this script to add reasoning to the matches.")
    # main()  # Uncomment to run