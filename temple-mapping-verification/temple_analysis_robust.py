#!/usr/bin/env python3
"""
Robust Temple Data Analysis Script
Handles inconsistent data types and structures
"""

import json
from collections import defaultdict, Counter
from typing import Dict, Any, List, Set, Union
import os

def safe_get_string(value: Any) -> str:
    """Safely convert value to string, handling None and empty cases"""
    if value is None or value == "":
        return ""
    return str(value)

def analyze_temple_data_robust(file_path: str) -> Dict[str, Any]:
    """Robust analysis that handles data inconsistencies"""
    
    # Load the data
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    temples = data.get('temples_scraped', [])
    total_temples = len(temples)
    
    print(f"🔍 Analyzing {total_temples} temples...")
    
    results = {
        'metadata': {
            'source': data.get('source', 'Unknown'),
            'total_available': data.get('total_available', 0),
            'temples_scraped': total_temples,
            'scraping_started': data.get('scraping_started', ''),
            'last_updated': data.get('last_updated', '')
        }
    }
    
    # 1. DUPLICATE ANALYSIS
    print("📊 Checking for duplicates...")
    temple_ids = []
    for temple in temples:
        tid = temple.get('temple_id', '')
        temple_ids.append(tid)
    
    id_counts = Counter(temple_ids)
    duplicates = {tid: count for tid, count in id_counts.items() if count > 1}
    
    results['duplicate_analysis'] = {
        'total_temples': total_temples,
        'total_unique_ids': len(set(filter(None, temple_ids))),  # Filter out None/empty
        'duplicate_ids': duplicates,
        'has_duplicates': len(duplicates) > 0,
        'empty_ids': temple_ids.count('') + temple_ids.count(None)
    }
    
    # 2. SCHEMA ANALYSIS - Get all possible fields
    print("📋 Analyzing schema...")
    all_fields = set()
    field_types = defaultdict(set)
    
    def extract_fields(obj, prefix=""):
        """Recursively extract all field paths"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                field_path = f"{prefix}.{key}" if prefix else key
                all_fields.add(field_path)
                field_types[field_path].add(type(value).__name__)
                
                if isinstance(value, dict):
                    extract_fields(value, field_path)
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    # For lists of objects, analyze first object
                    extract_fields(value[0], f"{field_path}[0]")
    
    for temple in temples:
        extract_fields(temple)
    
    # Convert sets to lists for JSON serialization
    schema_info = {}
    for field, types in field_types.items():
        schema_info[field] = list(types)
    
    results['schema_analysis'] = {
        'total_fields': len(all_fields),
        'all_fields': sorted(list(all_fields)),
        'field_types': schema_info
    }
    
    # 3. FIELD COMPLETENESS ANALYSIS
    print("✅ Calculating completeness...")
    field_presence = defaultdict(int)
    
    def count_present_fields(obj, prefix=""):
        """Count non-empty fields"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                field_path = f"{prefix}.{key}" if prefix else key
                
                # Consider field present if it has meaningful content
                is_present = (
                    value is not None and 
                    value != "" and 
                    value != [] and 
                    value != {}
                )
                
                if is_present:
                    field_presence[field_path] += 1
                
                # Recurse into nested objects
                if isinstance(value, dict):
                    count_present_fields(value, field_path)
    
    for temple in temples:
        count_present_fields(temple)
    
    # Calculate percentages
    completeness_stats = {}
    for field, count in field_presence.items():
        percentage = round((count / total_temples) * 100, 2)
        completeness_stats[field] = {
            'present_count': count,
            'missing_count': total_temples - count,
            'completeness_percentage': percentage
        }
    
    # Sort by completeness
    sorted_by_completeness = sorted(
        completeness_stats.items(), 
        key=lambda x: x[1]['completeness_percentage'], 
        reverse=True
    )
    
    results['completeness_analysis'] = {
        'field_completeness': completeness_stats,
        'most_complete_fields': sorted_by_completeness[:10],
        'least_complete_fields': sorted_by_completeness[-10:] if len(sorted_by_completeness) >= 10 else []
    }
    
    # 4. PATTERN ANALYSIS
    print("🔄 Identifying patterns...")
    patterns = {
        'states': Counter(),
        'districts': Counter(),
        'cities': Counter(),
        'main_deities': Counter(),
        'goddesses': Counter(),
        'sacred_trees': Counter(),
        'festivals': Counter(),
        'temple_name_words': Counter(),
        'holy_water_types': Counter()
    }
    
    for temple in temples:
        # Location patterns
        location = temple.get('location', {})
        if isinstance(location, dict):
            state = safe_get_string(location.get('state'))
            district = safe_get_string(location.get('district'))
            city = safe_get_string(location.get('city'))
            
            if state:
                patterns['states'][state] += 1
            if district:
                patterns['districts'][district] += 1
            if city:
                patterns['cities'][city] += 1
        
        # Deity patterns
        deities = temple.get('deities', {})
        if isinstance(deities, dict):
            main_deity = safe_get_string(deities.get('main_deity'))
            goddess = safe_get_string(deities.get('goddess'))
            
            if main_deity:
                patterns['main_deities'][main_deity] += 1
            if goddess:
                patterns['goddesses'][goddess] += 1
        
        # Sacred tree patterns
        holy_elements = temple.get('holy_elements', {})
        if isinstance(holy_elements, dict):
            sacred_tree = safe_get_string(holy_elements.get('sacred_tree'))
            if sacred_tree:
                patterns['sacred_trees'][sacred_tree] += 1
            
            # Holy water patterns
            holy_water = holy_elements.get('holy_water')
            if isinstance(holy_water, list):
                for water in holy_water:
                    if isinstance(water, str):
                        patterns['holy_water_types'][water] += 1
            elif isinstance(holy_water, str):
                patterns['holy_water_types'][holy_water] += 1
        
        # Festival patterns (handle both string and object formats)
        festivals = temple.get('festivals', [])
        if isinstance(festivals, list):
            for festival in festivals:
                if isinstance(festival, str):
                    patterns['festivals'][festival] += 1
                elif isinstance(festival, dict):
                    festival_name = safe_get_string(festival.get('festival'))
                    if festival_name:
                        patterns['festivals'][festival_name] += 1
        
        # Temple name word patterns
        name = safe_get_string(temple.get('name', ''))
        if name:
            # Extract words from temple names (simple tokenization)
            words = name.replace('Temple', '').replace('Kovil', '').split()
            for word in words:
                clean_word = word.strip('(),')
                if len(clean_word) > 2:  # Only count meaningful words
                    patterns['temple_name_words'][clean_word] += 1
    
    # Convert to serializable format with statistics
    pattern_results = {}
    for category, counter in patterns.items():
        pattern_results[category] = {
            'unique_count': len(counter),
            'total_occurrences': sum(counter.values()),
            'top_10': counter.most_common(10),
            'diversity_score': round(len(counter) / max(sum(counter.values()), 1), 3)
        }
    
    results['pattern_analysis'] = pattern_results
    
    # 5. DATA QUALITY ASSESSMENT
    quality_issues = []
    
    # Check for missing critical fields
    critical_fields = ['temple_id', 'name', 'location.state', 'deities.main_deity']
    for field in critical_fields:
        if field in completeness_stats:
            if completeness_stats[field]['completeness_percentage'] < 95:
                quality_issues.append(f"Critical field '{field}' only {completeness_stats[field]['completeness_percentage']}% complete")
    
    # Check for duplicates
    if results['duplicate_analysis']['has_duplicates']:
        quality_issues.append(f"Found {len(duplicates)} duplicate temple IDs")
    
    # Check for empty IDs
    empty_ids = results['duplicate_analysis']['empty_ids']
    if empty_ids > 0:
        quality_issues.append(f"Found {empty_ids} temples with empty/missing IDs")
    
    results['data_quality'] = {
        'issues': quality_issues,
        'overall_score': max(0, 100 - len(quality_issues) * 10),  # Simple scoring
        'recommendations': [
            "Standardize festival data format (currently mixed strings and objects)",
            "Ensure all temples have unique, non-empty temple_id values",
            "Consider normalizing location data (some district names may vary)",
            "Standardize deity name formats for better pattern recognition"
        ]
    }
    
    return results

def print_comprehensive_summary(results: Dict[str, Any]):
    """Print detailed analysis summary"""
    
    print("\n" + "=" * 70)
    print("🏛️  COMPREHENSIVE TEMPLE DATA ANALYSIS")
    print("=" * 70)
    
    # Metadata
    meta = results['metadata']
    print(f"\n📊 DATASET OVERVIEW:")
    print(f"   📍 Source: {meta['source']}")
    print(f"   📈 Total Available: {meta['total_available']}")
    print(f"   ✅ Temples Scraped: {meta['temples_scraped']}")
    print(f"   🕐 Last Updated: {meta['last_updated']}")
    
    # Duplicates
    dup = results['duplicate_analysis']
    print(f"\n🔍 DUPLICATE ANALYSIS:")
    print(f"   📊 Total Temples: {dup['total_temples']}")
    print(f"   🆔 Unique IDs: {dup['total_unique_ids']}")
    print(f"   ⚠️  Empty IDs: {dup['empty_ids']}")
    print(f"   🔄 Has Duplicates: {'❌ Yes' if dup['has_duplicates'] else '✅ No'}")
    if dup['duplicate_ids']:
        print(f"   🔄 Duplicate IDs: {dup['duplicate_ids']}")
    
    # Schema
    schema = results['schema_analysis']
    print(f"\n📋 SCHEMA ANALYSIS:")
    print(f"   📊 Total Fields: {schema['total_fields']}")
    print(f"   🗂️  Top-Level Fields: {len([f for f in schema['all_fields'] if '.' not in f])}")
    
    # Most complete fields
    comp = results['completeness_analysis']
    print(f"\n✅ FIELD COMPLETENESS:")
    print("   🏆 Most Complete Fields:")
    for field, stats in comp['most_complete_fields'][:5]:
        print(f"     • {field}: {stats['completeness_percentage']}% ({stats['present_count']}/{dup['total_temples']})")
    
    print("   ⚠️  Least Complete Fields:")
    for field, stats in comp['least_complete_fields'][:5]:
        print(f"     • {field}: {stats['completeness_percentage']}% ({stats['present_count']}/{dup['total_temples']})")
    
    # Patterns
    patterns = results['pattern_analysis']
    print(f"\n🔄 DATA PATTERNS:")
    
    print(f"   🗺️  Geographic Distribution:")
    states = patterns['states']
    print(f"     States: {states['unique_count']} unique")
    for state, count in states['top_10'][:3]:
        print(f"       • {state}: {count} temples")
    
    districts = patterns['districts']
    print(f"     Districts: {districts['unique_count']} unique")
    for district, count in districts['top_10'][:3]:
        print(f"       • {district}: {count} temples")
    
    print(f"   🕉️  Religious Patterns:")
    deities = patterns['main_deities']
    print(f"     Main Deities: {deities['unique_count']} unique")
    for deity, count in deities['top_10'][:3]:
        print(f"       • {deity}: {count} temples")
    
    festivals = patterns['festivals']
    print(f"     Festivals: {festivals['unique_count']} unique")
    for festival, count in festivals['top_10'][:3]:
        print(f"       • {festival}: {count} temples")
    
    trees = patterns['sacred_trees']
    print(f"     Sacred Trees: {trees['unique_count']} unique")
    for tree, count in trees['top_10'][:3]:
        print(f"       • {tree}: {count} temples")
    
    # Data Quality
    quality = results['data_quality']
    print(f"\n🎯 DATA QUALITY ASSESSMENT:")
    print(f"   📊 Overall Score: {quality['overall_score']}/100")
    
    if quality['issues']:
        print(f"   ⚠️  Issues Found:")
        for issue in quality['issues']:
            print(f"     • {issue}")
    else:
        print(f"   ✅ No major issues detected!")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(quality['recommendations'], 1):
        print(f"   {i}. {rec}")

if __name__ == "__main__":
    file_path = "findmytemple_master_scraped_data.json"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: Could not find file '{file_path}'")
        print("Make sure the file exists in the current directory.")
        exit(1)
    
    try:
        print("🚀 Starting comprehensive temple data analysis...")
        results = analyze_temple_data_robust(file_path)
        
        # Print summary
        print_comprehensive_summary(results)
        
        # Save detailed results
        output_file = "comprehensive_temple_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed analysis saved to: {os.path.abspath(output_file)}")
        print(f"📊 Analysis complete! Processed {results['metadata']['temples_scraped']} temples.")
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format - {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()