#!/usr/bin/env python3
"""
Migrate from v2/v3 file versioning to Git-based versioning
Consolidates data into single files tracked by Git
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def migrate_to_git_versioning():
    """Consolidate versioned files into single files for Git tracking"""
    
    print("\n🔄 Migrating to Git-based versioning...")
    
    # 1. Use v3 as the main unified data (it has the latest enrichments)
    v3_file = Path("integrated_data/unified_temple_data_v3.json")
    main_file = Path("integrated_data/unified_temple_data.json")
    
    if v3_file.exists():
        print("  ✓ Using v3 as main unified dataset")
        shutil.copy2(v3_file, main_file)
    
    # 2. Consolidate enrichment data
    enriched_dir = Path("enriched_data")
    
    # Create main enrichments file
    enrichments = {
        "coordinates": {},
        "websites": {},
        "corrections": {},
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "sources": ["OpenStreetMap Nominatim", "Manual corrections"]
        }
    }
    
    # Load coordinates
    coords_file = enriched_dir / "578_temples_coordinates_final.json"
    if coords_file.exists():
        with open(coords_file, 'r') as f:
            enrichments["coordinates"] = json.load(f)
    
    # Load websites  
    websites_file = enriched_dir / "578_temples_websites_final.json"
    if websites_file.exists():
        with open(websites_file, 'r') as f:
            enrichments["websites"] = json.load(f)
    
    # Load corrections
    corrections_file = enriched_dir / "coordinate_corrections.json"
    if corrections_file.exists():
        with open(corrections_file, 'r') as f:
            corrections_data = json.load(f)
            enrichments["corrections"] = corrections_data.get("corrections", [])
    
    # Save consolidated enrichments
    enrichments_file = enriched_dir / "temple_enrichments.json"
    with open(enrichments_file, 'w') as f:
        json.dump(enrichments, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Created consolidated enrichments: {enrichments_file}")
    
    # 3. Create README for data structure
    readme_content = """# Temple Calendar App - Data Structure

## Main Data Files (Git Tracked)

### `integrated_data/unified_temple_data.json`
The main dataset with all 46,004 temples. This is the single source of truth.
- Track changes with Git commits
- No more v2, v3 suffixes needed

### `enriched_data/temple_enrichments.json`
Consolidated enrichment data:
- Coordinates from OpenStreetMap
- Website URLs
- Manual corrections
- Metadata about sources

### `festivals/universal_festivals_2025.json`
Festival calendar data (kept separate for efficiency)

## Version History
Use `git log` to see the history of changes:
```bash
git log --oneline integrated_data/unified_temple_data.json
```

## Rollback to Previous Version
```bash
git checkout <commit-hash> -- integrated_data/unified_temple_data.json
```

## Data Statistics
- Total temples: 46,004
- Temples with coordinates: 440
- Major temples (income > 10L): 578
- Major temples with coordinates: 428 (74%)

Last enrichment: 2025-08-24
"""
    
    readme_file = Path("integrated_data/README.md")
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    print(f"  ✓ Created data documentation: {readme_file}")
    
    # 4. Clean up old versioned files (optional - keeping for now)
    print("\n📁 Old versioned files preserved in:")
    for pattern in ["*_v2*.json", "*_v3*.json", "*backup*.json"]:
        for file in Path("integrated_data").glob(pattern):
            print(f"    - {file.name}")
    
    print("\n✅ Migration complete! Now using Git for version control")
    print("\n📝 Next steps:")
    print("  1. git add integrated_data/unified_temple_data.json")
    print("  2. git add enriched_data/temple_enrichments.json")  
    print("  3. git commit -m 'feat: Migrate to Git versioning with 428 geocoded temples'")
    print("  4. Remove old versioned files when comfortable")

if __name__ == "__main__":
    migrate_to_git_versioning()