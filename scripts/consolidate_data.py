#!/usr/bin/env python3
"""
Consolidate and organize all temple data into a clean structure
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import os

def load_json(filepath):
    """Safely load JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def save_json(data, filepath, compact=False):
    """Save JSON with consistent formatting"""
    with open(filepath, 'w', encoding='utf-8') as f:
        if compact:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        else:
            json.dump(data, f, ensure_ascii=False, indent=2)

def consolidate_data():
    """Main consolidation function"""
    print("\n🔄 Starting Data Consolidation...")
    
    # Step 1: Create master temple dataset
    print("\n📦 Step 1: Creating master dataset...")
    
    # Use v3 as it has the latest enrichments
    source_data = load_json("integrated_data/unified_temple_data_v3.json")
    if not source_data:
        # Fallback to regular unified_temple_data.json
        source_data = load_json("integrated_data/unified_temple_data.json")
    
    if source_data:
        save_json(source_data, "data/temples.json")
        print(f"  ✓ Created data/temples.json with {len(source_data)} temples")
    
    # Step 2: Consolidate enrichments
    print("\n🔗 Step 2: Consolidating enrichments...")
    
    enrichments = {
        "coordinates": {},
        "websites": {},
        "corrections": [],
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "coordinate_sources": ["OpenStreetMap Nominatim"],
            "total_temples": len(source_data) if source_data else 0,
            "enriched_temples": 0
        }
    }
    
    # Load coordinate data
    coords_file = Path("enriched_data/578_temples_coordinates_final.json")
    if coords_file.exists():
        coords_data = load_json(coords_file)
        if coords_data:
            enrichments["coordinates"] = coords_data
            enrichments["metadata"]["enriched_temples"] = len(coords_data)
    
    # Load website data
    websites_file = Path("enriched_data/578_temples_websites_final.json")
    if websites_file.exists():
        websites_data = load_json(websites_file)
        if websites_data:
            enrichments["websites"] = websites_data
    
    # Load corrections
    corrections_file = Path("enriched_data/coordinate_corrections.json")
    if corrections_file.exists():
        corrections_data = load_json(corrections_file)
        if corrections_data:
            enrichments["corrections"] = corrections_data.get("corrections", [])
    
    save_json(enrichments, "data/enrichments.json")
    print(f"  ✓ Created data/enrichments.json")
    print(f"    - {len(enrichments['coordinates'])} coordinates")
    print(f"    - {len(enrichments['websites'])} websites")
    print(f"    - {len(enrichments['corrections'])} corrections")
    
    # Step 3: Copy festival data
    print("\n🎊 Step 3: Organizing festival data...")
    
    festivals_source = Path("festivals/universal_festivals_2025.json")
    if festivals_source.exists():
        shutil.copy2(festivals_source, "data/festivals_2025.json")
        print("  ✓ Copied festivals_2025.json")
    
    # Step 4: Create metadata file
    print("\n📋 Step 4: Creating metadata...")
    
    metadata = {
        "project": "Tamil Temple Calendar",
        "total_temples": len(source_data) if source_data else 0,
        "data_sources": {
            "primary": "Tamil Nadu HR&CE Department",
            "geocoding": "OpenStreetMap Nominatim",
            "enrichment_date": "2025-08-24"
        },
        "coverage": {
            "total_temples": 46004,
            "major_temples": 578,
            "geocoded_temples": len(enrichments["coordinates"]),
            "temples_with_websites": len(enrichments["websites"])
        },
        "income_categories": {
            "46_iii": "Annual income above Rs. 10 lakhs (Major temples)",
            "46_ii": "Annual income between Rs. 5 lakhs and Rs. 10 lakhs",
            "46_i": "Annual income less than Rs. 5 lakhs",
            "49_i": "Annual income less than Rs. 10,000"
        },
        "file_structure": {
            "temples.json": "Main temple dataset with all 46,004 temples",
            "enrichments.json": "Geocoding and website data for major temples",
            "festivals_2025.json": "Universal festival calendar for 2025",
            "metadata.json": "This file - project and data information"
        },
        "last_updated": datetime.now().isoformat(),
        "version": "1.0.0"
    }
    
    save_json(metadata, "data/metadata.json")
    print("  ✓ Created data/metadata.json")
    
    # Step 5: Create reference files
    print("\n📚 Step 5: Creating reference files...")
    
    # Extract deity patterns
    deity_file = Path("festivals/deity_patterns.json")
    if deity_file.exists():
        shutil.copy2(deity_file, "reference/deity_patterns.json")
        print("  ✓ Copied deity_patterns.json")
    
    # Copy coordinate corrections
    if corrections_file.exists():
        shutil.copy2(corrections_file, "reference/coordinate_corrections.json")
        print("  ✓ Copied coordinate_corrections.json")
    
    # Create income categories reference
    income_categories = {
        "46_iii": {
            "description": "Annual income above Rs. 10 lakhs",
            "classification": "Major temple",
            "count": 578
        },
        "46_ii": {
            "description": "Annual income between Rs. 5 lakhs and Rs. 10 lakhs",
            "classification": "Medium temple",
            "count": 0  # To be calculated
        },
        "46_i": {
            "description": "Annual income less than Rs. 5 lakhs",
            "classification": "Small temple",
            "count": 0
        },
        "49_i": {
            "description": "Annual income less than Rs. 10,000",
            "classification": "Very small temple",
            "count": 0
        }
    }
    
    # Count temples by category
    if source_data:
        for temple in source_data.values():
            category = temple.get("income_category")
            if category in income_categories:
                income_categories[category]["count"] += 1
    
    save_json(income_categories, "reference/income_categories.json")
    print("  ✓ Created income_categories.json")
    
    # Step 6: Create sample files
    print("\n🧪 Step 6: Creating sample files...")
    
    if source_data:
        # Create 20-temple sample
        temple_ids = list(source_data.keys())[:20]
        sample_20 = {tid: source_data[tid] for tid in temple_ids}
        save_json(sample_20, "samples/temples_sample_20.json")
        print("  ✓ Created temples_sample_20.json")
        
        # Create major temples subset
        major_temples = {
            tid: temple for tid, temple in source_data.items()
            if temple.get("income_category") == "46_iii"
        }
        save_json(major_temples, "samples/major_temples_578.json")
        print(f"  ✓ Created major_temples_578.json with {len(major_temples)} temples")
        
        # Create single temple for testing
        test_temple = {temple_ids[0]: source_data[temple_ids[0]]}
        save_json(test_temple, "samples/test_temple.json")
        print("  ✓ Created test_temple.json")
    
    print("\n✅ Data consolidation complete!")
    
    # Generate summary
    print("\n📊 Summary:")
    print(f"  Main dataset: {len(source_data) if source_data else 0} temples")
    print(f"  Enrichments: {len(enrichments['coordinates'])} coordinates, {len(enrichments['websites'])} websites")
    print(f"  Reference files: 3 created")
    print(f"  Sample files: 3 created")
    
    return True

def archive_old_files():
    """Archive old files before deletion"""
    print("\n📦 Archiving old files...")
    
    archive_dir = Path("archive/2025-08-24")
    
    # Files to archive
    files_to_archive = [
        ("integrated_data/unified_temple_data_v2.json", "old_versions/"),
        ("integrated_data/unified_temple_data_v3.json", "old_versions/"),
        ("integrated_data/unified_temple_data_v2_backup_20250824_152047.json", "old_versions/"),
        ("integrated_data/unified_temple_data_backup_20250824_041127.json", "old_versions/"),
        ("raw_data/tn_temples_full.json", "raw_scraping_data/"),
        ("raw_data/temples_app_format.json", "raw_scraping_data/"),
    ]
    
    archived_count = 0
    for source, dest_dir in files_to_archive:
        source_path = Path(source)
        if source_path.exists():
            dest_path = archive_dir / dest_dir / source_path.name
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)
            archived_count += 1
            print(f"  ✓ Archived {source_path.name}")
    
    print(f"  Total files archived: {archived_count}")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print(" 🧹 TEMPLE DATA CONSOLIDATION & CLEANUP")
    print("=" * 60)
    
    # Run consolidation
    if consolidate_data():
        # Archive before cleanup
        archive_old_files()
        
        print("\n" + "=" * 60)
        print(" ✨ CONSOLIDATION COMPLETE!")
        print("=" * 60)
        print("\nNew structure created:")
        print("  data/        - Core data files")
        print("  reference/   - Lookup/reference files")
        print("  samples/     - Sample datasets")
        print("  archive/     - Old versions (backup)")
        print("\nNext step: Run cleanup_old_files.py to remove duplicates")
    else:
        print("\n❌ Consolidation failed. Check errors above.")