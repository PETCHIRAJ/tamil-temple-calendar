# 📚 Temple Calendar App - Data Inventory

## 🎯 Master Dataset Status

### Primary Data Source
**Location:** `database/temples.db` (SQLite Database)
- **Total Temples:** 46,004
- **Size:** 64MB
- **Structure:** Indexed relational database
- **Backup:** `json_data/production/temples.json` (50MB)
- **Last Updated:** 2025-08-24

### Data Coverage Summary
| Data Type | Temples with Data | Percentage | Status |
|-----------|------------------|------------|---------|
| Basic Info (Name, Address) | 46,004 | 100% | ✅ Complete |
| District | 46,004 | 100% | ✅ Complete |
| Income Category | 46,004 | 100% | ✅ Complete |
| Coordinates | 428 | 0.9% | 🟡 Major temples done |
| Deities | 15 | 0.03% | ❌ Needs Work |
| Timings | 3 | 0.01% | ❌ Critical Gap |
| Festivals (Universal) | 88 dates | N/A | ✅ Complete for 2025 |
| Images | 7 | 0.02% | ❌ Needs Work |
| Contact Info | 5 | 0.01% | ❌ Critical Gap |
| Tamil Content | 5 | 0.01% | ❌ Needs Work |
| Website | 5 | 0.01% | ❌ Limited |

---

## 📁 Data Files Organization

### 1️⃣ **Core Temple Data**

#### `raw_data/tn_temples_full.json`
- **Source:** GitHub (vindicindic/tn-hindu-temples)
- **Records:** 46,004 temples
- **Content:** Basic temple information from HR&CE
- **Fields:** id, temple_name, address, district, pincode, income_category
- **Quality:** ✅ Government verified

#### `database/temples.db`
- **Purpose:** Primary data source (SQLite)
- **Records:** 46,004 temples
- **Content:** Indexed database with full JSON in raw_data column
- **Status:** Production database

#### `json_data/production/temples.json`
- **Purpose:** Backup/exchange format
- **Records:** 46,004 temples
- **Content:** Complete JSON backup
- **Status:** Git-tracked backup

---

### 2️⃣ **Festival Data**

#### `json_data/festivals/festivals_2025.json`
- **Content:** Calculated festival dates for 2025
- **Database:** All 88 dates imported to SQLite `festivals` table
- **Includes:** 
  - 24 Pradosham dates
  - 25 Ekadashi dates
  - 12 Pournami dates
  - 12 Amavasya dates
  - 15 Major annual festivals
- **Validation:** Cross-referenced with Tamil calendars

#### `json_data/reference/deity_patterns.json`
- **Content:** Deity identification patterns
- **Types:** SHIVA, MURUGAN, AMMAN, VISHNU, GANESHA
- **Purpose:** Infer deity from temple names

#### `validation/sankarankovil_temple_2025_calendar.json`
- **Content:** Test calculation for one temple
- **Events:** 176 calculated events for 2025
- **Purpose:** Validation against real calendar

---

### 3️⃣ **Enrichment Results**

#### Major Temples Geocoding
- **Target:** 578 temples with income > ₹10 lakh/year
- **Geocoded:** 428 temples (74%)
- **Method:** OpenStreetMap Nominatim API
- **Stored in:** `json_data/enrichments/` folder and database

#### Sample Files
- **`json_data/samples/temples_sample_20.json`:** 20 temples for testing
- **`json_data/samples/major_temples_578.json`:** All major temples
- **`json_data/samples/test_temple.json`:** Single temple for unit tests

---

### 4️⃣ **Reference Data**

#### `json_data/reference/`
- **deity_patterns.json:** Deity identification rules
- **income_categories.json:** Temple classifications

#### `json_data/enrichments/`
- **coordinate_corrections.json:** Manual geo corrections
- **enrichments.json:** Consolidated geocoding data
- **578_temples_*.json:** Major temple enrichments

---

## 📊 Income Distribution

| Category | Income Range | Count | Percentage |
|----------|-------------|-------|------------|
| 49_i | < ₹10,000/year | 34,987 | 76.1% |
| 46_i | ₹10k - ₹2 lakh/year | 3,779 | 8.2% |
| 46_ii | ₹2 - ₹10 lakh/year | 6,660 | 14.5% |
| 46_iii | > ₹10 lakh/year | 578 | 1.3% |

---

## 🔄 Data Sources Integration

### Successfully Integrated
1. **HR&CE Basic Data** ✅
   - 46,004 temples with basic info
   - Source: GitHub dataset

2. **Wikipedia/Wikidata** ✅
   - 20 temples enriched
   - Added: Coordinates, deities, festivals

3. **HR&CE Subdomains** ✅
   - 2 temples with full data
   - Added: Tamil content, images

4. **TempleKB** ✅
   - 6 temples with legends
   - Added: Historical information

### Failed/Limited Success
1. **HR&CE Website Scraping** ❌
   - Session/token issues
   - No temple data returned

2. **Dinamalar Portal** ❌
   - Site structure changed
   - Got navigation links only

3. **Tamil Nadu Data Portal** ❌
   - Returns CSS instead of data
   - API endpoints not working

---

## 🎯 Next Steps Priority

### Critical Gaps to Fill
1. **Coordinates** (0.03% → 100%)
   - Use OpenStreetMap Nominatim (free)
   - Need for navigation feature

2. **Temple Timings** (0.01% → 10%)
   - Google Places API for major temples
   - Crowd-source for others

3. **Official Websites** (0% → 5%)
   - Pattern-based URL checking
   - DuckDuckGo search (free)

4. **Contact Info** (0% → 10%)
   - Google Places API
   - Official websites

### Data We Can Generate
- ✅ Universal festivals (already done)
- ✅ Deity inference from names (patterns ready)
- ⏳ District-specific patterns (can add)

---

## 💾 Storage Summary

| Directory | Size | Purpose |
|-----------|------|---------|
| `database/` | 64 MB | SQLite database + queries |
| `json_data/production/` | 50 MB | JSON backup |
| `json_data/enrichments/` | < 5 MB | Geocoding data |
| `json_data/samples/` | < 5 MB | Sample datasets |
| `json_data/reference/` | < 1 MB | Reference data |
| `scripts/` | < 1 MB | Processing scripts |
| **Total** | ~125 MB | All data |

---

## 🚀 Ready for App Development

### What We Have ✅
- Complete temple directory (46,004 temples)
- Universal festival calculator
- Deity pattern matching
- Basic data structure

### What We Need ❌
- Coordinates for navigation
- Temple timings
- Contact information
- Photos

### Recommendation
**Ready for app development!** Current state:
- ✅ SQLite database optimized for mobile (64MB)
- ✅ 428 major temples geocoded (74% of high-priority temples)
- ✅ 88 universal festival dates for 2025
- ✅ Clean repository structure
- ✅ SQL queries for common operations

Next priorities:
1. Continue geocoding remaining temples
2. Add temple timings for major temples
3. Collect contact information progressively