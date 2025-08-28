#!/usr/bin/env python3
"""
Temple Data Quality Analysis
============================
Analyze data completeness across all 193 updated temples
"""

import json
import sqlite3
from collections import defaultdict
from typing import Dict, List, Any

class TempleDataQualityAnalyzer:
    def __init__(self):
        self.conn = sqlite3.connect('../database/temples.db')
        self.conn.row_factory = sqlite3.Row
        
        self.analysis = {
            'total_temples': 0,
            'hrce_fields': {},
            'enhanced_fields': {},
            'json_fields': {},
            'confidence_breakdown': {},
            'source_breakdown': {}
        }
    
    def get_all_updated_temples(self) -> List[Dict]:
        """Get all 193 temples with FindMyTemple data"""
        
        query = """
        SELECT 
            temple_id, name, tamil_name, district, location, address, 
            main_deity, deity_type, income_category, temple_type,
            goddess, holy_water, sacred_tree, special_rituals, 
            temple_tank, inscriptions, temple_age, raw_data
        FROM temples 
        WHERE raw_data LIKE '%findmytemple%'
        ORDER BY name
        """
        
        cursor = self.conn.execute(query)
        temples = []
        
        for row in cursor:
            temple = dict(row)
            # Parse JSON data
            try:
                temple['parsed_json'] = json.loads(temple['raw_data'])
            except:
                temple['parsed_json'] = {}
            
            temples.append(temple)
        
        return temples
    
    def analyze_field_completeness(self, temples: List[Dict], field_name: str, 
                                   source: str = 'hrce') -> Dict:
        """Analyze completeness of a specific field"""
        
        total = len(temples)
        non_empty = 0
        non_null = 0
        sample_values = []
        
        for temple in temples:
            value = temple.get(field_name)
            
            if value is not None:
                non_null += 1
                if isinstance(value, str) and value.strip():
                    non_empty += 1
                    if len(sample_values) < 3:
                        sample_values.append(value[:50])
                elif isinstance(value, (list, dict)) and value:
                    non_empty += 1
                    if len(sample_values) < 3:
                        sample_values.append(str(value)[:50])
                elif not isinstance(value, str):
                    non_empty += 1
        
        return {
            'field': field_name,
            'source': source,
            'total_temples': total,
            'non_null_count': non_null,
            'non_empty_count': non_empty,
            'null_percentage': round((total - non_null) / total * 100, 1),
            'empty_percentage': round((total - non_empty) / total * 100, 1),
            'completeness_percentage': round(non_empty / total * 100, 1),
            'sample_values': sample_values
        }
    
    def analyze_json_field(self, temples: List[Dict], json_path: List[str]) -> Dict:
        """Analyze completeness of fields within JSON data"""
        
        total = len(temples)
        found_count = 0
        non_empty_count = 0
        sample_values = []
        
        for temple in temples:
            parsed_json = temple.get('parsed_json', {})
            
            # Navigate JSON path
            current = parsed_json
            for key in json_path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    current = None
                    break
            
            if current is not None:
                found_count += 1
                
                # Check if meaningful content
                if isinstance(current, str) and current.strip():
                    non_empty_count += 1
                    if len(sample_values) < 3:
                        sample_values.append(current[:50])
                elif isinstance(current, (list, dict)) and current:
                    non_empty_count += 1
                    if len(sample_values) < 3:
                        sample_values.append(str(current)[:50])
                elif not isinstance(current, str):
                    non_empty_count += 1
        
        field_name = '.'.join(json_path)
        return {
            'field': field_name,
            'source': 'json',
            'total_temples': total,
            'found_count': found_count,
            'non_empty_count': non_empty_count,
            'missing_percentage': round((total - found_count) / total * 100, 1),
            'empty_percentage': round((found_count - non_empty_count) / total * 100, 1),
            'completeness_percentage': round(non_empty_count / total * 100, 1),
            'sample_values': sample_values
        }
    
    def analyze_confidence_and_sources(self, temples: List[Dict]):
        """Analyze match confidence and sources"""
        
        confidence_counts = defaultdict(int)
        source_counts = defaultdict(int)
        
        for temple in temples:
            parsed_json = temple.get('parsed_json', {})
            
            confidence = parsed_json.get('match_confidence', 'unknown')
            source = parsed_json.get('match_source', 'unknown')
            
            confidence_counts[confidence] += 1
            source_counts[source] += 1
        
        total = len(temples)
        
        self.analysis['confidence_breakdown'] = {
            conf: {
                'count': count,
                'percentage': round(count / total * 100, 1)
            }
            for conf, count in confidence_counts.items()
        }
        
        self.analysis['source_breakdown'] = {
            source: {
                'count': count,
                'percentage': round(count / total * 100, 1)
            }
            for source, count in source_counts.items()
        }
    
    def run_complete_analysis(self):
        """Run comprehensive data quality analysis"""
        
        print("🔍 TEMPLE DATA QUALITY ANALYSIS")
        print("=" * 60)
        
        # Get all updated temples
        print("Loading all updated temples...")
        temples = self.get_all_updated_temples()
        self.analysis['total_temples'] = len(temples)
        
        print(f"✅ Loaded {len(temples)} temples with FindMyTemple data")
        
        # Analyze HRCE core fields
        print("\n1️⃣ Analyzing HRCE Core Fields...")
        hrce_fields = [
            'name', 'tamil_name', 'district', 'location', 'address',
            'main_deity', 'deity_type', 'income_category', 'temple_type'
        ]
        
        for field in hrce_fields:
            analysis = self.analyze_field_completeness(temples, field, 'hrce')
            self.analysis['hrce_fields'][field] = analysis
            print(f"   {field}: {analysis['completeness_percentage']}% complete")
        
        # Analyze enhanced fields (new columns)
        print("\n2️⃣ Analyzing Enhanced Fields...")
        enhanced_fields = [
            'goddess', 'holy_water', 'sacred_tree', 'special_rituals',
            'temple_tank', 'inscriptions', 'temple_age'
        ]
        
        for field in enhanced_fields:
            analysis = self.analyze_field_completeness(temples, field, 'enhanced')
            self.analysis['enhanced_fields'][field] = analysis
            print(f"   {field}: {analysis['completeness_percentage']}% complete")
        
        # Analyze JSON fields
        print("\n3️⃣ Analyzing FindMyTemple JSON Data...")
        json_field_paths = [
            ['findmytemple', 'temple_id'],
            ['findmytemple', 'name'],
            ['findmytemple', 'location'],
            ['findmytemple', 'deities', 'main_deity'],
            ['findmytemple', 'deities', 'goddess'],
            ['findmytemple', 'timings'],
            ['findmytemple', 'festivals'],
            ['findmytemple', 'features'],
            ['findmytemple', 'history'],
            ['findmytemple', 'contact'],
            ['match_score'],
            ['matched_on']
        ]
        
        for path in json_field_paths:
            analysis = self.analyze_json_field(temples, path)
            self.analysis['json_fields'][analysis['field']] = analysis
            print(f"   {analysis['field']}: {analysis['completeness_percentage']}% complete")
        
        # Analyze confidence and sources
        print("\n4️⃣ Analyzing Match Quality...")
        self.analyze_confidence_and_sources(temples)
        
        self.conn.close()
        return self.analysis
    
    def generate_report(self):
        """Generate comprehensive data quality report"""
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE DATA QUALITY REPORT")
        print("=" * 80)
        
        print(f"**Total Temples Analyzed**: {self.analysis['total_temples']}")
        
        # Field completeness summary
        print(f"\n📋 **FIELD COMPLETENESS SUMMARY**")
        print("-" * 50)
        
        # Group by completeness level
        excellent = []  # 90-100%
        good = []       # 70-89%
        moderate = []   # 50-69%
        poor = []       # <50%
        
        all_fields = {}
        all_fields.update(self.analysis['hrce_fields'])
        all_fields.update(self.analysis['enhanced_fields'])
        all_fields.update(self.analysis['json_fields'])
        
        for field_name, data in all_fields.items():
            completeness = data['completeness_percentage']
            field_info = f"{field_name} ({data['source']}): {completeness}%"
            
            if completeness >= 90:
                excellent.append(field_info)
            elif completeness >= 70:
                good.append(field_info)
            elif completeness >= 50:
                moderate.append(field_info)
            else:
                poor.append(field_info)
        
        print(f"\n🟢 **EXCELLENT (90-100% complete)**: {len(excellent)} fields")
        for field in excellent:
            print(f"   ✅ {field}")
        
        print(f"\n🟡 **GOOD (70-89% complete)**: {len(good)} fields")
        for field in good:
            print(f"   ✅ {field}")
        
        print(f"\n🟠 **MODERATE (50-69% complete)**: {len(moderate)} fields")
        for field in moderate:
            print(f"   ⚠️ {field}")
        
        print(f"\n🔴 **NEEDS IMPROVEMENT (<50% complete)**: {len(poor)} fields")
        for field in poor:
            print(f"   ❌ {field}")
        
        # Match quality breakdown
        print(f"\n🎯 **MATCH QUALITY BREAKDOWN**")
        print("-" * 50)
        for confidence, data in self.analysis['confidence_breakdown'].items():
            print(f"   {confidence.upper()}: {data['count']} temples ({data['percentage']}%)")
        
        print(f"\n📂 **DATA SOURCE BREAKDOWN**")
        print("-" * 50)
        for source, data in self.analysis['source_breakdown'].items():
            print(f"   {source.upper()}: {data['count']} temples ({data['percentage']}%)")
        
        # Recommendations
        print(f"\n💡 **RECOMMENDATIONS FOR DATA ENRICHMENT**")
        print("-" * 50)
        
        # Find fields with low completeness that could be improved
        low_completeness = [(name, data) for name, data in all_fields.items() 
                           if data['completeness_percentage'] < 70]
        low_completeness.sort(key=lambda x: x[1]['completeness_percentage'])
        
        for field_name, data in low_completeness[:5]:
            print(f"   🔧 **{field_name}**: {data['completeness_percentage']}% complete")
            if data['sample_values']:
                print(f"      Sample: {data['sample_values'][0]}")
        
        # Save detailed analysis
        with open('temple_data_quality_report.json', 'w') as f:
            json.dump(self.analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 **Detailed analysis saved to**: temple_data_quality_report.json")

if __name__ == "__main__":
    analyzer = TempleDataQualityAnalyzer()
    analyzer.run_complete_analysis()
    analyzer.generate_report()