#!/usr/bin/env python3
"""
Server endpoint for saving verification results
Provides persistent storage beyond browser localStorage
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Create saves directory if it doesn't exist
SAVES_DIR = Path(__file__).parent / "verification_saves"
SAVES_DIR.mkdir(exist_ok=True)

def save_verification_data(data, session_name=None):
    """Save verification data to a JSON file"""
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if session_name:
        filename = f"verification_{session_name}_{timestamp}.json"
    else:
        filename = f"verification_{timestamp}.json"
    
    filepath = SAVES_DIR / filename
    
    # Add metadata
    save_data = {
        "metadata": {
            "saved_at": datetime.now().isoformat(),
            "filename": filename,
            "total_temples": data.get("total_temples", 0),
            "verified_count": len(data.get("verifications", {})),
            "session_name": session_name
        },
        "verifications": data.get("verifications", {}),
        "statistics": calculate_statistics(data.get("verifications", {}))
    }
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    return filepath

def load_latest_session():
    """Load the most recent verification session"""
    
    if not SAVES_DIR.exists():
        return None
    
    # Get all save files
    save_files = list(SAVES_DIR.glob("verification_*.json"))
    
    if not save_files:
        return None
    
    # Get most recent file
    latest_file = max(save_files, key=lambda f: f.stat().st_mtime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_saved_sessions():
    """List all saved verification sessions"""
    
    sessions = []
    
    if SAVES_DIR.exists():
        for filepath in sorted(SAVES_DIR.glob("verification_*.json"), reverse=True):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                sessions.append({
                    "filename": filepath.name,
                    "saved_at": data["metadata"]["saved_at"],
                    "verified_count": data["metadata"]["verified_count"],
                    "total_temples": data["metadata"]["total_temples"],
                    "session_name": data["metadata"].get("session_name", "")
                })
    
    return sessions

def calculate_statistics(verifications):
    """Calculate statistics from verification data"""
    
    stats = {
        "total_verified": len(verifications),
        "new_temples": 0,
        "matched_temples": 0,
        "high_confidence": 0,
        "medium_confidence": 0,
        "low_confidence": 0,
        "with_notes": 0
    }
    
    for temple_id, data in verifications.items():
        if data.get("db_id") == "new_temple":
            stats["new_temples"] += 1
        else:
            stats["matched_temples"] += 1
            
            confidence = data.get("confidence", 0)
            if confidence >= 80:
                stats["high_confidence"] += 1
            elif confidence >= 60:
                stats["medium_confidence"] += 1
            else:
                stats["low_confidence"] += 1
        
        if data.get("notes"):
            stats["with_notes"] += 1
    
    return stats

def merge_sessions(session_files):
    """Merge multiple verification sessions"""
    
    merged = {}
    
    for session_file in session_files:
        filepath = SAVES_DIR / session_file
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Later verifications override earlier ones
                merged.update(data.get("verifications", {}))
    
    return merged

if __name__ == "__main__":
    # Test the functions
    print(f"📁 Verification saves directory: {SAVES_DIR}")
    print(f"📊 Saved sessions: {len(list_saved_sessions())}")
    
    sessions = list_saved_sessions()
    if sessions:
        print("\nRecent sessions:")
        for session in sessions[:5]:
            print(f"  - {session['filename']}: {session['verified_count']} verified")