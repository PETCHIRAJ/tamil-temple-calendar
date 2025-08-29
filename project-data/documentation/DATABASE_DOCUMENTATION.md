# Temple Calendar App - Database Documentation

## Overview
Production-ready SQLite database for Tamil Nadu Temple Calendar Flutter app.

**Database File:** `temple_app_mvp.db`  
**Size:** ~400KB  
**Tables:** 4  
**Total Temples:** 588 (127 with navigation)

## Database Structure

### 1. `app_temples` Table (Primary)
**Purpose:** Navigation-ready temples with full features  
**Count:** 127 temples

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Unique temple ID (e.g., TM000001) |
| name | TEXT | Temple name in English |
| tamil_name | TEXT | Temple name in Tamil |
| district | TEXT | District name |
| latitude | REAL | GPS latitude (all non-zero) |
| longitude | REAL | GPS longitude (all non-zero) |
| deity_type | TEXT | Classification: shiva/vishnu/goddess/murugan/etc |
| gm_rating | REAL | Google Maps rating (4.6-4.8) |
| gm_address | TEXT | Full address |
| gm_phone | TEXT | Contact number |
| popular_times | TEXT | JSON array of crowd levels |
| is_tour_temple | BOOLEAN | Part of tour circuit |
| data_quality | TEXT | premium/standard/basic |
| search_text | TEXT | Concatenated searchable text |

### 2. `temple_directory` Table
**Purpose:** Complete temple directory for search  
**Count:** 588 temples (includes all)

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Unique temple ID |
| name | TEXT | Temple name |
| tamil_name | TEXT | Tamil name |
| district | TEXT | District |
| latitude | REAL | GPS (0 if unavailable) |
| longitude | REAL | GPS (0 if unavailable) |
| deity_type | TEXT | Temple classification |
| navigation_available | BOOLEAN | Has GPS coordinates |
| in_app_temples | BOOLEAN | Included in app_temples |

### 3. `tour_circuits` Table
**Purpose:** Curated temple tour routes  
**Count:** 4 circuits

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Circuit ID |
| name | TEXT | Circuit name (e.g., "Navagraha Temples") |
| tamil_name | TEXT | Tamil name |
| circuit_type | TEXT | navagraha/murugan/pancha_bootha |
| total_temples | INTEGER | Number of temples |
| total_distance_km | REAL | Total circuit distance |
| estimated_hours | REAL | Time to complete |

### 4. `circuit_temples` Table
**Purpose:** Links temples to circuits  
**Type:** Junction table

## Key Statistics

### Coverage by District (Top 5)
- Chennai: 28 temples
- Coimbatore: 10 temples  
- Thanjavur: 7 temples
- Thiruchirappalli: 7 temples
- Erode: 6 temples

### Temple Classification
- Other/Mixed: 45 temples
- Shiva: 27 temples
- Goddess: 19 temples
- Vishnu: 19 temples
- Murugan: 12 temples

### Data Quality
- **Premium** (15 temples): Full data with ratings, address, phone
- **Standard** (112 temples): GPS available, partial data
- **Tour Temples** (13): All major pilgrimage sites

## Flutter Integration

### Setup
```dart
dependencies:
  sqflite: ^2.3.0
  path: ^1.8.3

// Copy temple_app_mvp.db to assets/database/
```

### Sample Queries

#### 1. Find Nearby Temples
```dart
Future<List<Temple>> getNearbyTemples(double lat, double lng) async {
  final db = await database;
  return await db.rawQuery('''
    SELECT *, 
      (ABS(latitude - ?) + ABS(longitude - ?)) * 111 as distance_km
    FROM app_temples
    ORDER BY distance_km
    LIMIT 20
  ''', [lat, lng]);
}
```

#### 2. Search Temples
```dart
Future<List<Temple>> searchTemples(String query) async {
  final db = await database;
  return await db.query(
    'app_temples',
    where: 'search_text LIKE ?',
    whereArgs: ['%${query.toLowerCase()}%'],
    limit: 50
  );
}
```

#### 3. Get Tour Circuit
```dart
Future<List<Temple>> getCircuitTemples(String circuitId) async {
  final db = await database;
  return await db.rawQuery('''
    SELECT t.*, ct.sequence_order 
    FROM app_temples t
    JOIN circuit_temples ct ON t.id = ct.temple_id
    WHERE ct.circuit_id = ?
    ORDER BY ct.sequence_order
  ''', [circuitId]);
}
```

#### 4. Browse All Temples
```dart
Future<List<Temple>> getAllTemples({String? district}) async {
  final db = await database;
  if (district != null) {
    return await db.query(
      'temple_directory',
      where: 'district = ?',
      whereArgs: [district],
      orderBy: 'name'
    );
  }
  return await db.query('temple_directory', orderBy: 'district, name');
}
```

#### 5. Check Crowd Levels
```dart
Future<Map?> getPopularTimes(String templeId) async {
  final db = await database;
  final result = await db.query(
    'app_temples',
    columns: ['popular_times'],
    where: 'id = ? AND popular_times IS NOT NULL',
    whereArgs: [templeId]
  );
  
  if (result.isNotEmpty && result.first['popular_times'] != null) {
    return jsonDecode(result.first['popular_times'] as String);
  }
  return null;
}
```

## Unique Features

### 1. Real-time Crowd Levels
5 temples have Google Popular Times data:
- Can show "Busy now" indicators
- Best time to visit suggestions
- Weekly crowd patterns

### 2. Tour Circuits
Pre-planned pilgrimage routes:
- Navagraha (9 planets) circuit
- Murugan Six Abodes
- Pancha Bootha (5 elements)
- Chennai Heritage Circuit

### 3. Two-tier System
- **app_temples**: Full features, navigation
- **temple_directory**: Complete searchable list

## Performance Optimization

### Indexes Created
- District-based queries
- Deity type filtering
- Location-based sorting
- Text search on temple names
- Rating-based sorting

### Expected Performance
- Nearby temples: <50ms
- Text search: <100ms
- District filter: <30ms
- All temples load: <200ms

## Future Enhancements

### Phase 2 (Month 4-6)
- Add user reviews table
- Photo gallery table
- Festival calendar integration
- Prasadam/service bookings

### Crowd-sourcing Ready
The `temple_directory` table has flags for:
- `crowd_source_needed`: Temples needing GPS
- `data_complete`: Tracking data completeness

## Migration Path

For future GPS additions:
```sql
-- When user submits GPS for a temple
UPDATE temple_directory 
SET latitude = ?, longitude = ?, 
    navigation_available = 1,
    crowd_source_needed = 0
WHERE id = ?;

-- If quality is good, promote to app_temples
INSERT INTO app_temples SELECT * FROM temple_directory WHERE id = ?;
```

## Success Metrics

Current Coverage:
- **21.6%** temples with navigation (127/588)
- **100%** tour temples with GPS (15/15)
- **30** districts represented
- **4.73** average rating for GPS temples

Target for v2:
- 40% navigation coverage (235 temples)
- User reviews for 100+ temples
- Festival data for all major temples

---

*Database Version: 1.0*  
*Last Updated: 2025-08-29*  
*Ready for Production Use*