#!/usr/bin/env python3
"""
Safe Temple Verification Process
=================================
Implements safeguards to prevent wrong matches from corrupting the database
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class SafeVerificationProcessor:
    """Process verified matches with safety checks and rollback capabilities"""
    
    def __init__(self, verification_file: str):
        self.verification_file = verification_file
        self.backup_dir = Path("verification_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Categories for safe processing
        self.high_confidence = []  # >80% - likely safe
        self.medium_confidence = []  # 60-80% - needs review
        self.low_confidence = []  # <60% - likely wrong
        self.new_temples = []  # No match found
        self.suspicious = []  # Flagged for issues
        
    def load_verifications(self) -> Dict:
        """Load verification results from JSON export"""
        with open(self.verification_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('verifications', {})
    
    def analyze_verifications(self, verifications: Dict) -> Dict:
        """Analyze verified matches for safety issues"""
        
        analysis = {
            'total_verified': len(verifications),
            'safe_to_process': [],
            'needs_review': [],
            'likely_wrong': [],
            'suspicious_patterns': [],
            'new_temples': []
        }
        
        for temple_id, verification in verifications.items():
            confidence = verification.get('confidence', 0)
            db_id = verification.get('db_id')
            notes = verification.get('notes', '')
            
            # Categorize by confidence
            if db_id == 'new_temple':
                analysis['new_temples'].append({
                    'findmytemple_id': temple_id,
                    'name': verification.get('findmytemple_name'),
                    'notes': notes
                })
            elif confidence >= 80:
                # High confidence but check for suspicious patterns
                if self._check_suspicious_patterns(verification):
                    analysis['suspicious_patterns'].append({
                        'findmytemple_id': temple_id,
                        'db_id': db_id,
                        'confidence': confidence,
                        'reason': 'Pattern mismatch despite high score'
                    })
                else:
                    analysis['safe_to_process'].append(verification)
            elif confidence >= 60:
                analysis['needs_review'].append(verification)
            else:
                analysis['likely_wrong'].append(verification)
        
        return analysis
    
    def _check_suspicious_patterns(self, verification: Dict) -> bool:
        """Check for suspicious matching patterns"""
        
        suspicious = False
        
        # Check if temple names are too different despite high score
        fmt_name = verification.get('findmytemple_name', '').lower()
        db_name = verification.get('db_name', '').lower()
        
        # Common suspicious patterns
        if fmt_name and db_name:
            # Different deity types (Shiva vs Vishnu temples)
            shiva_keywords = ['sivan', 'swara', 'linga', 'natha']
            vishnu_keywords = ['perumal', 'vishnu', 'rama', 'krishna']
            
            fmt_is_shiva = any(kw in fmt_name for kw in shiva_keywords)
            fmt_is_vishnu = any(kw in fmt_name for kw in vishnu_keywords)
            db_is_shiva = any(kw in db_name for kw in shiva_keywords)
            db_is_vishnu = any(kw in db_name for kw in vishnu_keywords)
            
            if (fmt_is_shiva and db_is_vishnu) or (fmt_is_vishnu and db_is_shiva):
                suspicious = True
        
        return suspicious
    
    def create_safe_update_script(self, analysis: Dict) -> str:
        """Create SQL script for safe updates only"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_file = f"safe_update_{timestamp}.sql"
        
        with open(script_file, 'w') as f:
            f.write(f"-- Safe Temple Mapping Update Script\n")
            f.write(f"-- Generated: {datetime.now().isoformat()}\n")
            f.write(f"-- Total Safe Updates: {len(analysis['safe_to_process'])}\n\n")
            
            f.write("-- Create backup table\n")
            f.write(f"CREATE TABLE IF NOT EXISTS temple_mapping_backup_{timestamp} AS SELECT * FROM temples;\n\n")
            
            f.write("-- Add findmytemple_id column if not exists\n")
            f.write("ALTER TABLE temples ADD COLUMN IF NOT EXISTS findmytemple_id TEXT;\n\n")
            
            f.write("BEGIN TRANSACTION;\n\n")
            
            # Only process high confidence matches
            for verification in analysis['safe_to_process']:
                fmt_id = verification['findmytemple_id']
                db_id = verification['db_id']
                confidence = verification['confidence']
                
                f.write(f"-- Mapping: {verification['findmytemple_name']} -> {verification['db_name']} ({confidence}%)\n")
                f.write(f"UPDATE temples SET findmytemple_id = '{fmt_id}' WHERE temple_id = '{db_id}';\n\n")
            
            f.write("-- Verification check\n")
            f.write("SELECT COUNT(*) as updated_count FROM temples WHERE findmytemple_id IS NOT NULL;\n\n")
            
            f.write("-- COMMIT; -- Uncomment only after reviewing the updates\n")
            f.write("-- ROLLBACK; -- Uncomment to undo changes\n")
        
        return script_file
    
    def generate_review_report(self, analysis: Dict) -> str:
        """Generate detailed review report"""
        
        report_file = "verification_safety_report.md"
        
        with open(report_file, 'w') as f:
            f.write("# Temple Verification Safety Report\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Verified**: {analysis['total_verified']}\n")
            f.write(f"- **Safe to Process**: {len(analysis['safe_to_process'])} ✅\n")
            f.write(f"- **Needs Review**: {len(analysis['needs_review'])} ⚠️\n")
            f.write(f"- **Likely Wrong**: {len(analysis['likely_wrong'])} ❌\n")
            f.write(f"- **Suspicious**: {len(analysis['suspicious_patterns'])} 🔍\n")
            f.write(f"- **New Temples**: {len(analysis['new_temples'])} 🆕\n\n")
            
            f.write("## ⚠️ NEEDS MANUAL REVIEW\n\n")
            if analysis['needs_review']:
                f.write("These matches have medium confidence (60-80%) and should be reviewed:\n\n")
                for item in analysis['needs_review'][:10]:  # Show first 10
                    f.write(f"- **{item['findmytemple_name']}** → {item['db_name']} ({item['confidence']}%)\n")
                    f.write(f"  - FMT ID: {item['findmytemple_id']}\n")
                    f.write(f"  - DB ID: {item['db_id']}\n")
                    if item.get('notes'):
                        f.write(f"  - Notes: {item['notes']}\n")
                    f.write("\n")
            
            f.write("## ❌ LIKELY WRONG MATCHES\n\n")
            if analysis['likely_wrong']:
                f.write("These matches have low confidence (<60%) and are probably incorrect:\n\n")
                for item in analysis['likely_wrong'][:10]:  # Show first 10
                    f.write(f"- **{item['findmytemple_name']}** → {item['db_name']} ({item['confidence']}%)\n")
                    f.write(f"  - Should probably be marked as NEW TEMPLE\n\n")
            
            f.write("## 🔍 SUSPICIOUS PATTERNS DETECTED\n\n")
            if analysis['suspicious_patterns']:
                f.write("These matches have high scores but suspicious patterns:\n\n")
                for item in analysis['suspicious_patterns']:
                    f.write(f"- Temple: {item['findmytemple_id']}\n")
                    f.write(f"  - Reason: {item['reason']}\n")
                    f.write(f"  - Confidence: {item['confidence']}%\n\n")
            
            f.write("## 🆕 NEW TEMPLES TO ADD\n\n")
            if analysis['new_temples']:
                f.write(f"Found {len(analysis['new_temples'])} temples not in HRCE database:\n\n")
                for item in analysis['new_temples'][:20]:  # Show first 20
                    f.write(f"- {item['name']} (ID: {item['findmytemple_id']})\n")
                    if item.get('notes'):
                        f.write(f"  - Notes: {item['notes']}\n")
            
            f.write("\n## Recommendations\n\n")
            f.write("1. **Review all medium confidence matches** before processing\n")
            f.write("2. **Do NOT process low confidence matches** - mark as new temples instead\n")
            f.write("3. **Investigate suspicious patterns** manually\n")
            f.write("4. **Run the safe update script** only after review\n")
            f.write("5. **Keep the backup table** until verification is complete\n")
        
        return report_file

def create_undo_script():
    """Create a script to undo temple mappings if needed"""
    
    undo_script = """#!/usr/bin/env python3
'''
Undo Temple Mappings
Removes findmytemple_id mappings from database
'''

import sqlite3
import sys

def undo_mappings(backup_table):
    conn = sqlite3.connect('../database/temples.db')
    
    try:
        # Remove all findmytemple mappings
        conn.execute("UPDATE temples SET findmytemple_id = NULL")
        conn.commit()
        print("✅ Removed all FindMyTemple mappings")
        
        # Optionally restore from backup
        if backup_table:
            conn.execute(f"DROP TABLE temples")
            conn.execute(f"ALTER TABLE {backup_table} RENAME TO temples")
            conn.commit()
            print(f"✅ Restored from backup: {backup_table}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    backup = input("Enter backup table name (or press Enter to skip): ")
    confirm = input("Are you sure you want to undo mappings? (yes/no): ")
    
    if confirm.lower() == 'yes':
        undo_mappings(backup.strip() if backup else None)
    else:
        print("Cancelled")
"""
    
    with open('undo_mappings.py', 'w') as f:
        f.write(undo_script)
    
    return 'undo_mappings.py'

def main():
    """Run safe verification process"""
    
    print("🔒 Safe Temple Verification Process")
    print("=" * 60)
    
    # Check for verification file
    verification_files = list(Path('.').glob('temple_verifications*.json'))
    
    if not verification_files:
        print("❌ No verification files found!")
        print("Please export your verifications from the UI first.")
        return
    
    # Use most recent file
    latest_file = max(verification_files, key=lambda f: f.stat().st_mtime)
    print(f"📄 Using verification file: {latest_file}")
    
    processor = SafeVerificationProcessor(str(latest_file))
    
    # Load and analyze
    print("\n🔍 Analyzing verifications...")
    verifications = processor.load_verifications()
    analysis = processor.analyze_verifications(verifications)
    
    # Generate reports
    print("\n📊 Generating safety report...")
    report_file = processor.generate_review_report(analysis)
    print(f"✅ Safety report: {report_file}")
    
    # Create safe update script
    if analysis['safe_to_process']:
        print("\n💾 Creating safe update script...")
        script_file = processor.create_safe_update_script(analysis)
        print(f"✅ SQL script: {script_file}")
    else:
        print("\n⚠️ No safe matches found to process!")
    
    # Create undo script
    print("\n🔄 Creating undo script...")
    undo_file = create_undo_script()
    print(f"✅ Undo script: {undo_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"✅ Safe to process: {len(analysis['safe_to_process'])}")
    print(f"⚠️  Needs review: {len(analysis['needs_review'])}")
    print(f"❌ Likely wrong: {len(analysis['likely_wrong'])}")
    print(f"🔍 Suspicious: {len(analysis['suspicious_patterns'])}")
    print(f"🆕 New temples: {len(analysis['new_temples'])}")
    
    print("\n📌 NEXT STEPS:")
    print("1. Review the safety report: verification_safety_report.md")
    print("2. Manually check medium-confidence matches")
    print("3. Run the SQL script to update only safe matches")
    print("4. Use undo_mappings.py if you need to rollback")

if __name__ == "__main__":
    main()