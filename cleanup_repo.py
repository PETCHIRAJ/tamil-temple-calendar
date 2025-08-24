#!/usr/bin/env python3
"""
Clean up repository - Remove duplicate and unnecessary files
All files are preserved in Git history and can be recovered
"""

import os
import shutil
from pathlib import Path

def cleanup_repository():
    """Remove unnecessary files while keeping essentials"""
    
    print("\n🧹 Starting Repository Cleanup...")
    print("(All files are preserved in Git history)")
    
    files_removed = 0
    dirs_removed = 0
    
    # Files to remove
    files_to_remove = [
        # Duplicate unified data (we have data/temples.json)
        "integrated_data/unified_temple_data.json",
        "integrated_data/unified_temple_data_v2.json",
        "integrated_data/unified_temple_data_v3.json",
        "integrated_data/enriched_temples.json",
        "integrated_data/sample_unified_data.json",
        "integrated_data/templekb_corpus.json",
        "integrated_data/connection_indices.json",
        "integrated_data/integration_stats.json",
        "integrated_data/integration_stats_v2.json",
        "integrated_data/v3_change_log.json",
        "integrated_data/v3_statistics.json",
        
        # Test and temporary files
        "enriched_data/test_coordinates.json",
        "enriched_data/test_summary.json",
        "enriched_data/578_temples_intermediate.json",
        "label_data.json",
        "setup_data_privacy.sh",
        
        # Old migration scripts (already executed)
        "migrate_to_git_versioning.py",
        "fix_festival_import.py",
        
        # Old/duplicate festival data
        "data/festivals_2025.json",  # We have festivals/ directory
        
        # Cleanup plan (will be in Git history)
        "cleanup_plan.md",
    ]
    
    # Directories to remove
    dirs_to_remove = [
        "raw_data",  # Old scraping data
        "data/raw_data",  # HTML files
        "data/major_temples_data",  # Intermediate data
        "data/wikipedia_data",  # Intermediate data
        "data/dinamalar_data",  # Intermediate data
        "data/venv",  # Virtual environment
        "archive",  # Old versions (in Git history)
    ]
    
    # Python scripts to remove (old/test scripts)
    scripts_to_remove = [
        "data/fetch_temple_list.py",
        "data/fetch_10_major_temples.py",
        "data/fetch_wikipedia_temples.py",
        "data/scrape_all_major_temples.py",
        "data/scrape_dinamalar_temples.py",
        "data/scrape_hrce_temples.py",
        "data/explore_major_temples.py",
        "data/explore_templekb.py",
        "data/discover_more_subdomains.py",
        "data/simple_hrce_scraper.py",
        "data/hrce_scraper.py",
        "data/hrce_direct_scraper.py",
        "data/hrce_selenium_scraper.py",
        "data/hrce_synced_scraper.py",
        "data/hrce_temple_list_scraper.py",
        "data/hrce_simple_check.py",
        "data/hrce_detail_explorer.py",
        "data/test_hrce_endpoints.py",
        "data/analyze_github_temples.py",
        "data/integrate_all_temple_data.py",
        "data/integrate_new_sources.py",
        "data/generate_universal_festivals.py",
        "data/generate_festivals_simple.py",
        "data/validate_sankarankovil.py",
        "data/enrich_test_temples.py",
        "data/enrich_578_temples_free.py",  # Keep improved version
        "data/setup_selenium.sh",
    ]
    
    # Remove individual files
    print("\n📄 Removing duplicate/temporary files...")
    for file_path in files_to_remove + scripts_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            files_removed += 1
            print(f"  ✓ Removed: {file_path}")
    
    # Remove directories
    print("\n📁 Removing intermediate data directories...")
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            dirs_removed += 1
            print(f"  ✓ Removed directory: {dir_path}")
    
    # Clean up enriched_data (keep only essential files)
    enriched_keep = [
        "enriched_data/temple_enrichments.json",
        "enriched_data/578_temples_coordinates_final.json",
        "enriched_data/578_temples_websites_final.json",
        "enriched_data/578_temples_enriched_final.json",
        "enriched_data/coordinate_corrections.json",
        "enriched_data/enrichment_statistics.json",
        "enriched_data/validation_report.json",
    ]
    
    if os.path.exists("enriched_data"):
        for file in Path("enriched_data").glob("*.json"):
            if str(file) not in enriched_keep:
                os.remove(file)
                files_removed += 1
                print(f"  ✓ Removed: {file}")
    
    print(f"\n📊 Cleanup Summary:")
    print(f"  Files removed: {files_removed}")
    print(f"  Directories removed: {dirs_removed}")
    
    # Show what remains
    print("\n✅ Essential files kept:")
    essential_files = [
        "data/temples.db",
        "data/temples.json",
        "data/temple_calendar_calculator.py",
        "data/hrce_subdomain_scraper.py",
        "data/enrich_578_temples_improved.py",
        "data/validate_and_integrate.py",
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / (1024 * 1024)  # MB
            print(f"  • {file} ({size:.1f} MB)")

def main():
    """Main cleanup function"""
    
    print("=" * 60)
    print(" 🧹 REPOSITORY CLEANUP")
    print("=" * 60)
    print("\n⚠️  This will remove duplicate and unnecessary files.")
    print("   All files are preserved in Git history.")
    print("   Last commit before cleanup: 497fc78")
    
    response = input("\nProceed with cleanup? (yes/no): ")
    
    if response.lower() == 'yes':
        cleanup_repository()
        
        print("\n" + "=" * 60)
        print(" ✨ CLEANUP COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Review changes: git status")
        print("  2. Commit cleanup: git add -A && git commit -m 'chore: Clean up repository'")
        print("  3. Push to GitHub: git push")
        print("\nTo recover any file:")
        print("  git checkout 497fc78 -- <filename>")
    else:
        print("\n❌ Cleanup cancelled")

if __name__ == "__main__":
    main()