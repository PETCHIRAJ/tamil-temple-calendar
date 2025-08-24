#!/usr/bin/env python3
"""
Integrate All Temple Data Sources
Combines HR&CE, TempleKB, and scraped data into a unified dataset
Preserves all data for future connections
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
import requests

class TempleDataIntegrator:
    def __init__(self):
        self.unified_data = {}
        self.temple_name_map = {}
        self.deity_map = {}
        self.location_map = {}
        Path("integrated_data").mkdir(exist_ok=True)
    
    def load_hrce_data(self):
        """Load the main HR&CE dataset"""
        print("\n1. Loading HR&CE Dataset...")
        
        with open("raw_data/tn_temples_full.json", "r", encoding="utf-8") as f:
            hrce_data = json.load(f)
        
        print(f"   ✓ Loaded {len(hrce_data)} temples from HR&CE")
        
        # Initialize unified data with HR&CE as base
        for temple in hrce_data:
            temple_id = temple.get('id', '')
            self.unified_data[temple_id] = {
                "temple_id": temple_id,
                "sources": {
                    "hrce_basic": temple
                },
                "name": temple.get('temple_name', ''),
                "district": temple.get('district', ''),
                "address": temple.get('address', ''),
                "pincode": temple.get('pincode', ''),
                "income_category": temple.get('temple_12a_category', ''),
                "temple_type": temple.get('temple_type', ''),
                
                # Placeholders for enriched data
                "deities": [],
                "festivals": [],
                "timings": [],
                "images": [],
                "legends": [],
                "tamil_content": {},
                "contact_info": {},
                "additional_info": {}
            }
            
            # Build name mapping for fuzzy matching
            clean_name = self.clean_temple_name(temple.get('temple_name', ''))
            if clean_name:
                if clean_name not in self.temple_name_map:
                    self.temple_name_map[clean_name] = []
                self.temple_name_map[clean_name].append(temple_id)
        
        return len(hrce_data)
    
    def load_subdomain_data(self):
        """Load scraped subdomain data"""
        print("\n2. Loading Subdomain Data...")
        
        try:
            # Load 10 major temples data
            with open("raw_data/10_major_temples_complete.json", "r", encoding="utf-8") as f:
                major_temples = json.load(f)
            
            enriched_count = 0
            for temple in major_temples:
                temple_id = temple.get('temple_id', '')
                
                if temple_id in self.unified_data:
                    # Add subdomain data
                    self.unified_data[temple_id]["sources"]["hrce_subdomain"] = temple
                    
                    # Extract key fields
                    if temple.get('extraction_status') == 'success':
                        # Deities
                        if temple.get('other_deities'):
                            self.unified_data[temple_id]["deities"] = temple['other_deities']
                        
                        # Timings
                        if temple.get('timings'):
                            self.unified_data[temple_id]["timings"] = temple['timings']
                        
                        # Images
                        if temple.get('images'):
                            self.unified_data[temple_id]["images"] = temple['images']
                        
                        # Tamil content
                        if temple.get('tamil_content'):
                            self.unified_data[temple_id]["tamil_content"] = temple['tamil_content']
                        
                        # Festival mentions
                        if temple.get('festival_mentions'):
                            self.unified_data[temple_id]["festivals"] = temple['festival_mentions']
                        
                        enriched_count += 1
            
            print(f"   ✓ Enriched {enriched_count} temples with subdomain data")
            
        except FileNotFoundError:
            print("   ⚠ Subdomain data not found")
        
        return enriched_count
    
    def load_templekb_data(self):
        """Load and integrate TempleKB data"""
        print("\n3. Loading TempleKB Data...")
        
        # Download full TempleKB corpus
        try:
            url = "https://raw.githubusercontent.com/priyaradhakrishnan0/templeKB/master/corpus/WebTempleCorpus.json"
            print("   Downloading TempleKB corpus...")
            resp = requests.get(url, timeout=30)
            
            if resp.status_code == 200:
                templekb_data = resp.json()
                
                # Save locally
                with open("integrated_data/templekb_corpus.json", "w", encoding="utf-8") as f:
                    json.dump(templekb_data, f, ensure_ascii=False, indent=2)
                
                print(f"   ✓ Downloaded TempleKB with {len(templekb_data)} entries")
                
                # Process TempleKB data
                matched_count = 0
                for filename, temple_data in templekb_data.items():
                    if filename == "head_line":
                        continue
                    
                    # Extract temple info
                    context = temple_data.get('context', '')
                    answers = temple_data.get('answers', [])
                    
                    # Try to match with our temples
                    temple_match = self.match_temple_from_text(context)
                    
                    if temple_match:
                        temple_id = temple_match
                        
                        # Add TempleKB data
                        if temple_id in self.unified_data:
                            if "templekb" not in self.unified_data[temple_id]["sources"]:
                                self.unified_data[temple_id]["sources"]["templekb"] = []
                            
                            self.unified_data[temple_id]["sources"]["templekb"].append({
                                "filename": filename,
                                "context": context,
                                "qa_pairs": self.extract_qa_pairs(answers, templekb_data.get('head_line', {}))
                            })
                            
                            # Extract legends
                            legends = self.extract_legends(context)
                            if legends:
                                self.unified_data[temple_id]["legends"].extend(legends)
                            
                            matched_count += 1
                
                print(f"   ✓ Matched {matched_count} TempleKB entries with our temples")
                
        except Exception as e:
            print(f"   ⚠ Error loading TempleKB: {e}")
            return 0
        
        return matched_count
    
    def clean_temple_name(self, name):
        """Clean temple name for matching"""
        if not name:
            return ""
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove common prefixes/suffixes
        remove_words = ['arulmigu', 'temple', 'shri', 'sri', 'the', 'at']
        for word in remove_words:
            name = name.replace(word, '')
        
        # Remove special characters
        name = re.sub(r'[^a-z0-9\s]', '', name)
        
        # Remove extra spaces
        name = ' '.join(name.split())
        
        return name.strip()
    
    def match_temple_from_text(self, text):
        """Try to match temple from text content"""
        text_lower = text.lower()
        
        # Look for Tamil Nadu locations
        tn_locations = [
            'chennai', 'madurai', 'coimbatore', 'trichy', 'tiruchirappalli',
            'thanjavur', 'kanyakumari', 'tirunelveli', 'salem', 'erode',
            'tiruppur', 'vellore', 'thoothukudi', 'dindigul', 'kanchipuram',
            'tiruvannamalai', 'karur', 'namakkal', 'dharmapuri', 'cuddalore'
        ]
        
        found_location = None
        for location in tn_locations:
            if location in text_lower:
                found_location = location
                break
        
        if not found_location:
            return None
        
        # Try to extract temple name
        temple_patterns = [
            r'(\w+(?:\s+\w+)*)\s+temple',
            r'temple\s+(?:of|to)\s+(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*)\s+(?:swamy|swami|amman|perumal)'
        ]
        
        for pattern in temple_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                temple_name = matches[0] if isinstance(matches[0], str) else matches[0][0]
                clean_name = self.clean_temple_name(temple_name)
                
                # Check if we have this temple
                if clean_name in self.temple_name_map:
                    return self.temple_name_map[clean_name][0]
        
        return None
    
    def extract_legends(self, text):
        """Extract legend snippets from text"""
        legends = []
        
        # Look for legend markers
        legend_markers = ['legend', 'it is believed', 'it is said', 'story', 'once upon']
        
        sentences = text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for marker in legend_markers:
                if marker in sentence_lower and len(sentence) > 50:
                    legends.append(sentence.strip())
                    break
        
        return legends[:3]  # Limit to 3 legends
    
    def extract_qa_pairs(self, answers, questions):
        """Extract Q&A pairs from TempleKB format"""
        qa_pairs = []
        
        if not questions or 'questions' not in questions:
            return qa_pairs
        
        question_list = questions['questions']
        
        for i, question in enumerate(question_list):
            if i < len(answers):
                answer_set = answers[i] if isinstance(answers[i], list) else [answers[i]]
                
                # Get non-empty answers
                valid_answers = [a for a in answer_set if a and a.strip() and not a.startswith('[CLS]')]
                
                if valid_answers:
                    qa_pairs.append({
                        "question": question,
                        "answers": valid_answers
                    })
        
        return qa_pairs
    
    def create_connection_indices(self):
        """Create indices for connecting data"""
        print("\n4. Creating Connection Indices...")
        
        # Deity index
        deity_index = {}
        
        # District index
        district_index = {}
        
        # Income category index
        income_index = {}
        
        # Location index (pincode based)
        location_index = {}
        
        for temple_id, temple_data in self.unified_data.items():
            # Index by deities
            for deity in temple_data.get('deities', []):
                deity_clean = self.clean_temple_name(deity)
                if deity_clean:
                    if deity_clean not in deity_index:
                        deity_index[deity_clean] = []
                    deity_index[deity_clean].append(temple_id)
            
            # Index by district
            district = temple_data.get('district', '')
            if district:
                if district not in district_index:
                    district_index[district] = []
                district_index[district].append(temple_id)
            
            # Index by income category
            income_cat = temple_data.get('income_category', '')
            if income_cat:
                if income_cat not in income_index:
                    income_index[income_cat] = []
                income_index[income_cat].append(temple_id)
            
            # Index by pincode
            pincode = temple_data.get('pincode', '')
            if pincode:
                if pincode not in location_index:
                    location_index[pincode] = []
                location_index[pincode].append(temple_id)
        
        # Save indices
        indices = {
            "deity_index": deity_index,
            "district_index": district_index,
            "income_index": income_index,
            "location_index": location_index,
            "name_index": self.temple_name_map
        }
        
        with open("integrated_data/connection_indices.json", "w", encoding="utf-8") as f:
            json.dump(indices, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ Created indices:")
        print(f"     - Deity index: {len(deity_index)} unique deities")
        print(f"     - District index: {len(district_index)} districts")
        print(f"     - Income index: {len(income_index)} categories")
        print(f"     - Location index: {len(location_index)} pincodes")
        print(f"     - Name index: {len(self.temple_name_map)} unique names")
        
        return indices
    
    def generate_statistics(self):
        """Generate statistics about the integrated data"""
        print("\n5. Generating Statistics...")
        
        stats = {
            "total_temples": len(self.unified_data),
            "temples_with_subdomain": 0,
            "temples_with_templekb": 0,
            "temples_with_images": 0,
            "temples_with_timings": 0,
            "temples_with_legends": 0,
            "temples_with_deities": 0,
            "temples_with_festivals": 0,
            "data_completeness": {}
        }
        
        for temple_id, temple_data in self.unified_data.items():
            sources = temple_data.get('sources', {})
            
            if 'hrce_subdomain' in sources:
                stats['temples_with_subdomain'] += 1
            
            if 'templekb' in sources:
                stats['temples_with_templekb'] += 1
            
            if temple_data.get('images'):
                stats['temples_with_images'] += 1
            
            if temple_data.get('timings'):
                stats['temples_with_timings'] += 1
            
            if temple_data.get('legends'):
                stats['temples_with_legends'] += 1
            
            if temple_data.get('deities'):
                stats['temples_with_deities'] += 1
            
            if temple_data.get('festivals'):
                stats['temples_with_festivals'] += 1
        
        # Calculate completeness percentages
        stats['data_completeness'] = {
            "basic_info": "100%",
            "subdomain_data": f"{stats['temples_with_subdomain']/stats['total_temples']*100:.1f}%",
            "templekb_data": f"{stats['temples_with_templekb']/stats['total_temples']*100:.1f}%",
            "images": f"{stats['temples_with_images']/stats['total_temples']*100:.1f}%",
            "timings": f"{stats['temples_with_timings']/stats['total_temples']*100:.1f}%",
            "legends": f"{stats['temples_with_legends']/stats['total_temples']*100:.1f}%",
            "deities": f"{stats['temples_with_deities']/stats['total_temples']*100:.1f}%",
            "festivals": f"{stats['temples_with_festivals']/stats['total_temples']*100:.1f}%"
        }
        
        return stats
    
    def save_integrated_data(self):
        """Save all integrated data"""
        print("\n6. Saving Integrated Data...")
        
        # Save full integrated dataset
        with open("integrated_data/unified_temple_data.json", "w", encoding="utf-8") as f:
            json.dump(self.unified_data, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ Saved unified data: integrated_data/unified_temple_data.json")
        
        # Save sample for verification
        sample_data = dict(list(self.unified_data.items())[:10])
        with open("integrated_data/sample_unified_data.json", "w", encoding="utf-8") as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ Saved sample: integrated_data/sample_unified_data.json")
        
        # Save enriched temples only
        enriched_temples = {
            tid: data for tid, data in self.unified_data.items()
            if len(data.get('sources', {})) > 1
        }
        
        with open("integrated_data/enriched_temples.json", "w", encoding="utf-8") as f:
            json.dump(enriched_temples, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ Saved {len(enriched_temples)} enriched temples")
        
        return len(self.unified_data)

def main():
    print("\n" + "="*60)
    print(" TEMPLE DATA INTEGRATION")
    print("="*60)
    
    integrator = TempleDataIntegrator()
    
    # Load all data sources
    hrce_count = integrator.load_hrce_data()
    subdomain_count = integrator.load_subdomain_data()
    templekb_count = integrator.load_templekb_data()
    
    # Create connections
    indices = integrator.create_connection_indices()
    
    # Generate statistics
    stats = integrator.generate_statistics()
    
    # Save everything
    total_saved = integrator.save_integrated_data()
    
    # Save statistics
    with open("integrated_data/integration_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print(" INTEGRATION COMPLETE")
    print("="*60)
    
    print(f"\n📊 Integration Summary:")
    print(f"   Total temples: {stats['total_temples']}")
    print(f"   With subdomain data: {stats['temples_with_subdomain']}")
    print(f"   With TempleKB data: {stats['temples_with_templekb']}")
    print(f"   With images: {stats['temples_with_images']}")
    print(f"   With timings: {stats['temples_with_timings']}")
    print(f"   With legends: {stats['temples_with_legends']}")
    
    print(f"\n📁 Output Files:")
    print(f"   1. integrated_data/unified_temple_data.json - Complete dataset")
    print(f"   2. integrated_data/enriched_temples.json - Temples with multiple sources")
    print(f"   3. integrated_data/connection_indices.json - Relationship indices")
    print(f"   4. integrated_data/integration_stats.json - Statistics")
    print(f"   5. integrated_data/templekb_corpus.json - TempleKB data")
    
    print(f"\n✅ Successfully integrated all available temple data!")
    print(f"   Ready for app development with comprehensive temple information")

if __name__ == "__main__":
    main()