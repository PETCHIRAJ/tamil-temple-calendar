#!/usr/bin/env python3
"""
Temple Data Analysis Script
Analyzes the findmytemple_master_scraped_data.json file for:
1. Duplicate temple_ids
2. Unique keys and data types
3. Field completeness percentages
4. Common data patterns
"""

import json
from collections import defaultdict, Counter
from typing import Dict, Any, List, Set
import statistics

def analyze_temple_data(file_path: str) -> Dict[str, Any]:
    """Comprehensive analysis of temple data"""
    
    # Load the data
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    temples = data['temples_scraped']
    total_temples = len(temples)
    
    # Analysis results
    results = {
        'metadata': {
            'source': data.get('source'),
            'total_available': data.get('total_available'),
            'temples_scraped': total_temples,
            'scraping_started': data.get('scraping_started'),
            'last_updated': data.get('last_updated')
        },
        'duplicate_analysis': {},
        'schema_analysis': {},
        'completeness_analysis': {},
        'pattern_analysis': {}
    }
    
    # 1. Check for duplicate temple_ids
    temple_ids = [temple.get('temple_id') for temple in temples]
    id_counts = Counter(temple_ids)
    duplicates = {tid: count for tid, count in id_counts.items() if count > 1}
    
    results['duplicate_analysis'] = {
        'total_unique_ids': len(set(temple_ids)),
        'duplicate_ids': duplicates,
        'has_duplicates': len(duplicates) > 0,
        'duplicate_count': sum(duplicates.values()) - len(duplicates) if duplicates else 0
    }
    
    # 2. Extract all unique keys and analyze data types
    def get_all_keys(obj, prefix='', all_keys=None):
        if all_keys is None:
            all_keys = defaultdict(set)
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                all_keys[full_key].add(type(value).__name__)
                
                if isinstance(value, (dict, list)):
                    get_all_keys(value, full_key, all_keys)
                    
        elif isinstance(obj, list) and obj:
            # Analyze first few items to understand list structure
            for i, item in enumerate(obj[:3]):  # Sample first 3 items
                item_prefix = f"{prefix}[{i}]" if isinstance(item, dict) else f"{prefix}[item]"
                get_all_keys(item, item_prefix, all_keys)
        
        return all_keys
    
    # Get all unique keys across all temples
    all_keys = defaultdict(set)
    for temple in temples:
        temple_keys = get_all_keys(temple)
        for key, types in temple_keys.items():
            all_keys[key].update(types)
    
    # Convert sets to lists for JSON serialization
    schema = {key: list(types) for key, types in all_keys.items()}
    
    results['schema_analysis'] = {
        'total_unique_fields': len(schema),
        'field_types': schema,
        'top_level_fields': [key for key in schema.keys() if '.' not in key]
    }
    
    # 3. Calculate field completeness percentages
    def calculate_completeness(temples_list):
        field_counts = defaultdict(int)
        
        def count_fields(obj, prefix=''):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    
                    # Count as complete if value exists and is not empty
                    is_complete = value is not None and value != '' and value != []
                    if is_complete:
                        field_counts[full_key] += 1
                    
                    # Recursively count nested fields
                    if isinstance(value, dict):
                        count_fields(value, full_key)
                    elif isinstance(value, list) and value:
                        # For lists, check if any items exist
                        if value:
                            field_counts[full_key] += 1
            
        for temple in temples_list:
            count_fields(temple)
        
        # Calculate percentages
        completeness = {}
        for field, count in field_counts.items():
            completeness[field] = {
                'count': count,
                'percentage': round((count / total_temples) * 100, 2)
            }
        
        return completeness
    
    completeness = calculate_completeness(temples)
    results['completeness_analysis'] = {
        'field_completeness': completeness,
        'most_complete_fields': sorted(
            [(field, stats['percentage']) for field, stats in completeness.items()],
            key=lambda x: x[1], reverse=True
        )[:10],
        'least_complete_fields': sorted(
            [(field, stats['percentage']) for field, stats in completeness.items()],
            key=lambda x: x[1]
        )[:10]
    }
    
    # 4. Identify common data patterns
    def analyze_patterns(temples_list):
        patterns = {
            'states': Counter(),
            'districts': Counter(),
            'cities': Counter(),
            'main_deities': Counter(),
            'goddesses': Counter(),
            'sacred_trees': Counter(),
            'festivals': Counter(),
            'special_features': Counter(),
            'temple_id_prefixes': Counter()
        }
        
        for temple in temples_list:
            # Location patterns
            location = temple.get('location', {})
            if location.get('state'):
                patterns['states'][location['state']] += 1
            if location.get('district'):
                patterns['districts'][location['district']] += 1
            if location.get('city'):
                patterns['cities'][location['city']] += 1
            
            # Deity patterns
            deities = temple.get('deities', {})
            if deities.get('main_deity'):
                patterns['main_deities'][deities['main_deity']] += 1
            if deities.get('goddess'):
                patterns['goddesses'][deities['goddess']] += 1
            
            # Holy elements
            holy_elements = temple.get('holy_elements', {})
            sacred_tree = holy_elements.get('sacred_tree') if isinstance(holy_elements, dict) else None
            if sacred_tree and isinstance(sacred_tree, str):
                patterns['sacred_trees'][sacred_tree] += 1
            
            # Festivals and features
            festivals = temple.get('festivals', [])
            if isinstance(festivals, list):
                for festival in festivals:
                    if isinstance(festival, str):
                        patterns['festivals'][festival] += 1
                
            features = temple.get('special_features', [])
            if isinstance(features, list):
                for feature in features:
                    if isinstance(feature, str):
                        patterns['special_features'][feature] += 1
            
            # Temple ID patterns
            temple_id = temple.get('temple_id', '')
            if temple_id:
                prefix = temple_id[0] if temple_id else ''
                patterns['temple_id_prefixes'][prefix] += 1
        
        return patterns
    
    patterns = analyze_patterns(temples)
    
    # Convert Counter objects to regular dicts for JSON serialization
    pattern_results = {}
    for category, counter in patterns.items():
        pattern_results[category] = {
            'total_unique': len(counter),
            'most_common': counter.most_common(10),
            'distribution': dict(counter)
        }
    
    results['pattern_analysis'] = pattern_results
    
    return results

def print_analysis_summary(results: Dict[str, Any]):
    """Print a formatted summary of the analysis"""
    
    print("=" * 60)
    print("TEMPLE DATA ANALYSIS SUMMARY")
    print("=" * 60)
    
    # Metadata
    meta = results['metadata']
    print(f"\n📊 METADATA:")
    print(f"   Source: {meta['source']}")
    print(f"   Total Available: {meta['total_available']}")
    print(f"   Temples Scraped: {meta['temples_scraped']}")
    print(f"   Last Updated: {meta['last_updated']}")
    
    # Duplicates
    dup = results['duplicate_analysis']
    print(f"\n🔍 DUPLICATE ANALYSIS:")
    print(f"   Unique Temple IDs: {dup['total_unique_ids']}")
    print(f"   Has Duplicates: {dup['has_duplicates']}")
    if dup['duplicate_ids']:
        print(f"   Duplicate IDs: {dup['duplicate_ids']}")
    
    # Schema
    schema = results['schema_analysis']
    print(f"\n📋 SCHEMA ANALYSIS:")
    print(f"   Total Unique Fields: {schema['total_unique_fields']}")
    print(f"   Top-level Fields: {len(schema['top_level_fields'])}")
    print(f"   Fields: {', '.join(schema['top_level_fields'])}")
    
    # Completeness
    comp = results['completeness_analysis']
    print(f"\n✅ COMPLETENESS ANALYSIS:")
    print(f"   Most Complete Fields:")
    for field, percentage in comp['most_complete_fields'][:5]:
        print(f"     {field}: {percentage}%")
    
    print(f"   Least Complete Fields:")
    for field, percentage in comp['least_complete_fields'][:5]:
        print(f"     {field}: {percentage}%")
    
    # Patterns
    patterns = results['pattern_analysis']
    print(f"\n🔄 PATTERN ANALYSIS:")
    
    print(f"   States ({patterns['states']['total_unique']} unique):")
    for state, count in patterns['states']['most_common'][:3]:
        print(f"     {state}: {count} temples")
    
    print(f"   Districts ({patterns['districts']['total_unique']} unique):")
    for district, count in patterns['districts']['most_common'][:3]:
        print(f"     {district}: {count} temples")
    
    print(f"   Most Common Festivals ({patterns['festivals']['total_unique']} unique):")
    for festival, count in patterns['festivals']['most_common'][:3]:
        print(f"     {festival}: {count} temples")

if __name__ == "__main__":
    file_path = "findmytemple_master_scraped_data.json"
    
    try:
        results = analyze_temple_data(file_path)
        
        # Print summary
        print_analysis_summary(results)
        
        # Save detailed results to JSON
        with open("temple_data_analysis_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed analysis saved to: temple_data_analysis_results.json")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find file '{file_path}'")
        print("Make sure the file exists in the current directory.")
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format - {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")