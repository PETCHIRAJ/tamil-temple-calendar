#!/usr/bin/env python3
"""
Fixed Complete Temple Database Update
====================================
Apply ALL approved temple matches with correct data structure handling
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List
import shutil

class FixedCompleteUpdater:
    def __init__(self):
        # Create backup first
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = f"../database/temples_backup_fixed_{timestamp}.db"
        
        print(f"Creating database backup: {self.backup_path}")
        shutil.copy2('../database/temples.db', self.backup_path)
        
        # Connect to database
        self.conn = sqlite3.connect('../database/temples.db')
        self.conn.row_factory = sqlite3.Row
        
        # Load FindMyTemple master data
        with open('../findmytemple_master_scraped_data.json', 'r') as f:
            fmt_full = json.load(f)
            self.fmt_data = fmt_full.get('temples_scraped', [])
            # Create lookup dict by temple_id
            self.fmt_lookup = {t.get('temple_id'): t for t in self.fmt_data}
        
        # Statistics
        self.stats = {
            'temples_updated': 0,
            'high_confidence_updates': 0,
            'medium_confidence_updates': 0,
            'skipped_no_temple_id': 0,
            'skipped_no_fmt_data': 0,
            'errors': []
        }
        
        # Collect all matches
        self.all_matches = []
    
    def load_all_matching_data(self):
        """Load and consolidate all matching results with correct structure"""
        
        print("Loading all matching data sources...")
        
        # 1. Load improved matching results (153 temples) - CORRECTED STRUCTURE
        try:
            with open('improved_matching_results.json', 'r') as f:
                improved = json.load(f)
            
            # Add high confidence matches - use 'matches' key and take first match
            for item in improved.get('high_confidence', []):
                matches = item.get('matches', [])
                if matches:  # Take the first (best) match
                    best_match = matches[0]
                    self.all_matches.append({
                        'source': 'improved_matching',
                        'confidence': 'high',
                        'findmytemple': item.get('findmytemple', {}),
                        'match': best_match,
                        'score': best_match.get('score', 0)
                    })
            
            # Add medium confidence matches
            for item in improved.get('medium_confidence', []):
                matches = item.get('matches', [])
                if matches:  # Take the first (best) match
                    best_match = matches[0]
                    self.all_matches.append({
                        'source': 'improved_matching',
                        'confidence': 'medium',
                        'findmytemple': item.get('findmytemple', {}),
                        'match': best_match,
                        'score': best_match.get('score', 0)
                    })
                
            print(f"✅ Loaded {len(improved.get('high_confidence', []))} high + {len(improved.get('medium_confidence', []))} medium from improved matching")
            
        except Exception as e:
            print(f"❌ Error loading improved matching: {e}")
        
        # 2. Load location fix results (15 temples)
        try:
            with open('location_fix_results.json', 'r') as f:
                location = json.load(f)
            
            for match in location.get('newly_matched', []):
                self.all_matches.append({
                    'source': 'location_fix',
                    'confidence': 'medium',  # Assume medium confidence for location fixes
                    'findmytemple': match.get('findmytemple', {}),
                    'match': match.get('match', {}),
                    'score': match.get('match', {}).get('score', 0)
                })
                
            print(f"✅ Loaded {len(location.get('newly_matched', []))} from location fix")
            
        except Exception as e:
            print(f"❌ Error loading location fix: {e}")
        
        # Remove duplicates based on FindMyTemple temple_id
        seen_fmt_ids = set()
        unique_matches = []
        
        for match in self.all_matches:
            fmt_temple = match['findmytemple']
            fmt_id = fmt_temple.get('temple_id') or fmt_temple.get('id')
            
            if fmt_id and fmt_id not in seen_fmt_ids:
                seen_fmt_ids.add(fmt_id)
                unique_matches.append(match)
            elif not fmt_id:
                # If no ID, use temple name as fallback
                fmt_name = fmt_temple.get('name', '')
                if fmt_name and fmt_name not in seen_fmt_ids:
                    seen_fmt_ids.add(fmt_name)
                    unique_matches.append(match)
        
        self.all_matches = unique_matches
        
        print(f"\n📊 TOTAL UNIQUE MATCHES TO PROCESS: {len(self.all_matches)}")
        
        # Show breakdown
        high_count = sum(1 for m in self.all_matches if m['confidence'] == 'high')
        medium_count = sum(1 for m in self.all_matches if m['confidence'] == 'medium')
        print(f"   High confidence: {high_count}")
        print(f"   Medium confidence: {medium_count}")
        
        return len(self.all_matches)
    
    def extract_fmt_data(self, fmt_temple: Dict) -> Dict:
        """Extract relevant data from FindMyTemple temple"""
        
        extracted = {}
        
        # Goddess (from deities)
        deities = fmt_temple.get('deities', {})
        if isinstance(deities, dict):
            goddess_list = deities.get('goddess', [])
            if goddess_list:
                extracted['goddess'] = ', '.join(goddess_list) if isinstance(goddess_list, list) else str(goddess_list)
        elif isinstance(deities, list):
            # Sometimes deities is a list
            extracted['goddess'] = ', '.join(str(d) for d in deities[:3])
        
        # Holy water (from features or holy_elements)
        features = fmt_temple.get('features', {}) or fmt_temple.get('holy_elements', {})
        if isinstance(features, dict):
            holy_water = features.get('holy_water', {})
            if isinstance(holy_water, dict):
                extracted['holy_water'] = holy_water.get('name', '')
            elif isinstance(holy_water, list) and holy_water:
                extracted['holy_water'] = ', '.join(str(h) for h in holy_water[:2])
            elif holy_water:
                extracted['holy_water'] = str(holy_water)
        
        # Sacred tree
        if isinstance(features, dict):
            sacred_tree = features.get('sacred_tree', {}) or features.get('temple_tree', '')
            if isinstance(sacred_tree, dict):
                extracted['sacred_tree'] = sacred_tree.get('name', '')
            elif sacred_tree:
                extracted['sacred_tree'] = str(sacred_tree)
        
        # Special rituals (from rituals or festivals)
        rituals = fmt_temple.get('rituals', {}) or fmt_temple.get('festivals', [])
        if isinstance(rituals, dict):
            special_rituals = []
            for ritual_type in ['special_rituals', 'unique_rituals', 'festivals']:
                if ritual_type in rituals:
                    ritual_list = rituals[ritual_type]
                    if isinstance(ritual_list, list):
                        special_rituals.extend(str(r) for r in ritual_list)
                    elif ritual_list:
                        special_rituals.append(str(ritual_list))
            if special_rituals:
                extracted['special_rituals'] = ', '.join(special_rituals[:3])
        elif isinstance(rituals, list) and rituals:
            extracted['special_rituals'] = ', '.join(str(r) for r in rituals[:3])
        
        # Temple tank
        if isinstance(features, dict):
            temple_tank = features.get('temple_tank', {})
            if isinstance(temple_tank, dict):
                extracted['temple_tank'] = temple_tank.get('name', '')
            elif temple_tank:
                extracted['temple_tank'] = str(temple_tank)
        
        # Inscriptions
        history = fmt_temple.get('history', {}) or fmt_temple.get('historical_info', '')
        if isinstance(history, dict):
            inscriptions = history.get('inscriptions', [])
            if isinstance(inscriptions, list) and inscriptions:
                extracted['inscriptions'] = ', '.join(str(i) for i in inscriptions[:2])
            elif inscriptions:
                extracted['inscriptions'] = str(inscriptions)
        elif history:
            extracted['inscriptions'] = str(history)[:200]  # Truncate long text
        
        # Temple age
        if isinstance(history, dict):
            age = history.get('age', '') or history.get('period', '')
            extracted['temple_age'] = str(age) if age else ''
        
        return extracted
    
    def update_temple(self, match_data: Dict):
        """Update a single temple with matched data"""
        
        fmt_temple = match_data.get('findmytemple', {})
        db_match = match_data.get('match', {})
        confidence = match_data.get('confidence', 'medium')
        source = match_data.get('source', 'unknown')
        
        # Check if we have temple_id in the match
        temple_id = db_match.get('temple_id')
        if not temple_id:
            self.stats['skipped_no_temple_id'] += 1
            return False
        
        # Get full FindMyTemple data
        fmt_id = fmt_temple.get('temple_id') or fmt_temple.get('id')
        full_fmt = self.fmt_lookup.get(fmt_id, fmt_temple)
        
        if not full_fmt:
            self.stats['skipped_no_fmt_data'] += 1
            return False
        
        # Extract data to update
        update_data = self.extract_fmt_data(full_fmt)
        
        # Prepare raw_data (complete JSON)
        existing_raw = None
        cursor = self.conn.execute(
            "SELECT raw_data FROM temples WHERE temple_id = ?",
            (temple_id,)
        )
        row = cursor.fetchone()
        if row and row[0]:
            try:
                existing_raw = json.loads(row[0])
            except:
                existing_raw = {}
        
        # Merge with FindMyTemple data
        if existing_raw is None:
            existing_raw = {}
        existing_raw['findmytemple'] = full_fmt
        existing_raw['match_confidence'] = confidence
        existing_raw['match_score'] = match_data.get('score', 0)
        existing_raw['match_source'] = source
        existing_raw['matched_on'] = datetime.now().isoformat()
        
        # Build UPDATE query
        update_fields = []
        params = []
        
        for field, value in update_data.items():
            if value:  # Only update non-empty values
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        # Always update raw_data
        update_fields.append("raw_data = ?")
        params.append(json.dumps(existing_raw, ensure_ascii=False))
        
        # Add temple_id at the end for WHERE clause
        params.append(temple_id)
        
        if update_fields:
            query = f"UPDATE temples SET {', '.join(update_fields)} WHERE temple_id = ?"
            
            try:
                self.conn.execute(query, params)
                self.stats['temples_updated'] += 1
                
                if confidence == 'high':
                    self.stats['high_confidence_updates'] += 1
                elif confidence == 'medium':
                    self.stats['medium_confidence_updates'] += 1
                
                fmt_name = fmt_temple.get('name', full_fmt.get('name', 'Unknown'))
                db_name = db_match.get('name', 'Unknown')
                print(f"✅ Updated: {fmt_name[:35]:<35} -> {db_name[:35]:<35} ({confidence}/{source})")
                return True
                
            except Exception as e:
                self.stats['errors'].append({
                    'temple': fmt_temple.get('name', 'Unknown'),
                    'error': str(e)
                })
                print(f"❌ Error updating {fmt_temple.get('name', 'Unknown')}: {e}")
                return False
        
        return False
    
    def run_complete_update(self):
        """Execute the complete update process"""
        
        print("\n" + "="*80)
        print("🚀 FIXED COMPLETE TEMPLE DATABASE UPDATE - ALL APPROVED MATCHES")
        print("="*80)
        
        # Step 1: Load all matching data
        total_matches = self.load_all_matching_data()
        
        if total_matches == 0:
            print("❌ No matching data found!")
            return
        
        # Step 2: Process all matches
        print(f"\n2️⃣ Processing {total_matches} temple matches...")
        
        for i, match_data in enumerate(self.all_matches, 1):
            if i % 25 == 0:
                print(f"   Progress: {i}/{total_matches} temples...")
            self.update_temple(match_data)
        
        # Commit all changes
        self.conn.commit()
        
        # Print summary
        print("\n" + "="*80)
        print("📊 FIXED COMPLETE UPDATE SUMMARY")
        print("="*80)
        print(f"✅ Total matches processed: {total_matches}")
        print(f"✅ Temples successfully updated: {self.stats['temples_updated']}")
        print(f"   - High confidence: {self.stats['high_confidence_updates']}")
        print(f"   - Medium confidence: {self.stats['medium_confidence_updates']}")
        print(f"⚠️ Skipped (no temple_id): {self.stats['skipped_no_temple_id']}")
        print(f"⚠️ Skipped (no FindMyTemple data): {self.stats['skipped_no_fmt_data']}")
        
        if self.stats['errors']:
            print(f"\n❌ Errors encountered: {len(self.stats['errors'])}")
            for err in self.stats['errors'][:3]:
                print(f"   - {err['temple']}: {err['error']}")
        
        print(f"\n💾 Database backup saved to: {self.backup_path}")
        print("✅ FIXED COMPLETE UPDATE FINISHED!")
        
        self.conn.close()

if __name__ == "__main__":
    updater = FixedCompleteUpdater()
    updater.run_complete_update()