# 📚 Temple Calendar App - Data Inventory

## 🎯 Master Dataset Status

### Primary Data File
**Location:** `integrated_data/unified_temple_data_v2.json`
- **Total Temples:** 46,004
- **Structure:** Dictionary with temple IDs as keys
- **Last Updated:** 2025-08-24

### Data Coverage Summary
| Data Type | Temples with Data | Percentage | Status |
|-----------|------------------|------------|---------|
| Basic Info (Name, Address) | 46,004 | 100% | ✅ Complete |
| District | 46,004 | 100% | ✅ Complete |
| Income Category | 46,004 | 100% | ✅ Complete |
| Coordinates | 14 | 0.03% | ❌ Critical Gap |
| Deities | 15 | 0.03% | ❌ Needs Work |
| Timings | 3 | 0.01% | ❌ Critical Gap |
| Festivals | 11 | 0.02% | ❌ Needs Work |
| Images | 7 | 0.02% | ❌ Needs Work |
| Contact Info | 2 | 0.00% | ❌ Critical Gap |
| Tamil Content | 5 | 0.01% | ❌ Needs Work |
| Website | 0 | 0.00% | ❌ Not Started |

---

## 📁 Data Files Organization

### 1️⃣ **Core Temple Data**

#### `raw_data/tn_temples_full.json`
- **Source:** GitHub (vindicindic/tn-hindu-temples)
- **Records:** 46,004 temples
- **Content:** Basic temple information from HR&CE
- **Fields:** id, temple_name, address, district, pincode, income_category
- **Quality:** ✅ Government verified

#### `integrated_data/unified_temple_data_v2.json`
- **Purpose:** Master integrated dataset
- **Records:** 46,004 temples
- **Content:** Merged data from all sources
- **Status:** Current working file

---

### 2️⃣ **Festival Data**

#### `festivals/universal_festivals_2025.json`
- **Content:** Calculated festival dates for 2025
- **Includes:** 
  - 24 Pradosham dates
  - 25 Ekadashi dates
  - 12 Pournami dates
  - 12 Amavasya dates
  - 15 Major annual festivals
- **Validation:** Cross-referenced with Tamil calendars

#### `festivals/deity_patterns.json`
- **Content:** Deity identification patterns
- **Types:** SHIVA, MURUGAN, AMMAN, VISHNU, GANESHA
- **Purpose:** Infer deity from temple names

#### `validation/sankarankovil_temple_2025_calendar.json`
- **Content:** Test calculation for one temple
- **Events:** 176 calculated events for 2025
- **Purpose:** Validation against real calendar

---

### 3️⃣ **Scraping Attempts**

#### `data/major_temples_data/`
- **all_578_temples_final.json:** Attempted scrape of 578 major temples
- **successful_temples_final.json:** Only 2 temples had data
- **Success Rate:** 0.3% (2 out of 578)

#### `data/wikipedia_data/`
- **temple_details_final.json:** 43 Wikipedia temples
- **Success:** 20 matched with our dataset
- **Added:** Coordinates, deity info, some festivals

#### `data/dinamalar_data/`
- **temple_list.json:** Attempted Dinamalar scrape
- **Result:** Failed - got navigation links instead

---

### 4️⃣ **Sample/Test Data**

#### `raw_data/templekb_sample.json`
- **Source:** TempleKB research dataset
- **Temples:** 6 with legends/stories
- **Use:** Historical information

#### Various sample files
- `sample_10_temples.json`
- `sample_temples.json`
- `tn_temples_sample_100.json`
- **Purpose:** Testing and development

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
| `raw_data/` | ~15 MB | Original source data |
| `integrated_data/` | ~30 MB | Processed/merged data |
| `festivals/` | < 1 MB | Festival calculations |
| `data/` | ~5 MB | Scraping attempts |
| **Total** | ~50 MB | All data |

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
**Start app development with current data.** The directory + festival calculator provides immediate value. Add enrichments progressively through:
1. Free geocoding services
2. User contributions
3. Partnerships with temples