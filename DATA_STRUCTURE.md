# 📁 Tamil Temple Calendar - Data Structure Documentation

## Overview
Complete documentation of the data organization after consolidation and SQLite migration.

## 🗄️ Database Structure (PRIMARY)

### `data/temples.db` (64MB)
SQLite database with indexed tables for efficient queries.

#### Tables:
1. **temples** - Main temple data
   - 46,004 records
   - Indexed on: district, income_category, deity_type, coordinates
   - Full JSON stored in `raw_data` column for flexibility

2. **festivals** - Festival calendar
   - Universal festival dates for 2025
   - Linked to deity types

3. **enrichments** - Geocoding metadata
   - Source tracking for coordinates
   - Verification status

4. **metadata** - Database statistics

#### Views:
- `major_temples` - 578 temples with income > 10L
- `geocoded_temples` - 428 temples with coordinates
- `temple_stats` - Summary statistics

## 📂 JSON Files (BACKUP/EXCHANGE)

### Core Data (`data/`)
```
data/
├── temples.json (50MB)         # Full 46,004 temples dataset
├── temples.db (64MB)           # SQLite database (PRIMARY)
├── enrichments.json (118KB)    # Geocoding & websites
├── festivals_2025.json (13KB)  # 2025 festival calendar
├── metadata.json (1KB)         # Data lineage & stats
└── sample_queries.sql (2KB)    # Example SQL queries
```

### Reference Files (`reference/`)
```
reference/
├── deity_patterns.json         # Deity identification rules
├── coordinate_corrections.json # Manual geo corrections
└── income_categories.json      # Temple classifications
```

### Sample Data (`samples/`)
```
samples/
├── temples_sample_20.json      # 20 temples for testing
├── major_temples_578.json      # Just major temples
└── test_temple.json            # Single temple for unit tests
```

### Archived Data (`archive/`)
```
archive/2025-08-24/
├── old_versions/               # v2, v3, backup files
└── raw_scraping_data/          # Original scraping results
```

## 🔍 Which File to Use When

### For App Development:
- **Use:** `data/temples.db` (SQLite)
- **Why:** Fast queries, indexed, works offline, small memory footprint
- **Example:**
```sql
SELECT name, latitude, longitude 
FROM temples 
WHERE district = 'Chennai District' 
AND latitude IS NOT NULL;
```

### For Data Exchange/Backup:
- **Use:** `data/temples.json`
- **Why:** Universal format, human-readable, Git-friendly
- **Example:**
```python
import json
with open('data/temples.json') as f:
    temples = json.load(f)
```

### For Testing:
- **Use:** `samples/temples_sample_20.json`
- **Why:** Small dataset, quick loading, representative data

### For Major Temples Only:
- **Use:** `samples/major_temples_578.json`
- **Why:** Focused dataset, all geocoded, high-priority temples

## 📊 Data Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Temples | 46,004 | 100% |
| Major Temples (>10L income) | 578 | 1.3% |
| Geocoded Temples | 428 | 0.9% |
| Temples with Websites | 5 | 0.01% |
| Festival Dates (2025) | 88 | - |

## 🚀 Performance Comparison

| Operation | JSON | SQLite |
|-----------|------|--------|
| Load all temples | 2-3 seconds | < 1ms (lazy) |
| Find by district | O(n) scan | O(log n) indexed |
| Memory usage | 200MB+ | 5-10MB |
| Mobile app size | +50MB | +64MB |
| Partial loading | No | Yes |
| Complex queries | Difficult | Native SQL |

## 💾 Storage Optimization

### Before Consolidation:
- 250MB (5 copies of 50MB JSON)
- 54 scattered JSON files
- No indexing

### After Consolidation:
- 64MB SQLite + 50MB JSON backup = 114MB
- Organized structure
- Full indexing
- 54% storage reduction

## 🔐 Data Versioning

Using Git for version control:
```bash
# View history
git log --oneline data/temples.db

# Rollback if needed
git checkout <commit> -- data/temples.db
```

## 📱 Mobile App Integration

### Flutter/React Native:
```dart
// Flutter with sqflite
Database db = await openDatabase('temples.db');
List<Map> temples = await db.query(
  'temples',
  where: 'district = ?',
  whereArgs: ['Chennai District']
);
```

### Benefits:
- Ships with app (offline-first)
- Fast queries with indexes
- Minimal memory usage
- Supports complex filters

## 🔄 Update Workflow

1. **Enrich data** (geocoding, websites)
2. **Update JSON** first (data/temples.json)
3. **Regenerate SQLite** (migrate_to_sqlite.py)
4. **Commit both** to Git
5. **Tag release** for app updates

## 📝 Maintenance Scripts

- `consolidate_data.py` - Organize JSON files
- `migrate_to_sqlite.py` - Generate SQLite from JSON
- `enrich_578_temples_improved.py` - Geocoding
- `validate_and_integrate.py` - Data validation

## ⚠️ Important Notes

1. **Primary Data Source**: SQLite database (`temples.db`)
2. **Backup Format**: JSON files
3. **Git Tracking**: Both SQLite and JSON are tracked
4. **Mobile Priority**: SQLite for production apps
5. **Web Priority**: Can use either (SQLite via SQL.js)

---

*Last Updated: August 24, 2025*
*Data Version: 1.0.0*
*Total Temples: 46,004*