# Tamil Nadu Temple Data Extraction Prompt - Optimized for Real Data Collection

## CORE EXTRACTION PROMPT

You are a temple data researcher tasked with collecting VERIFIED information about Tamil Nadu temples from reliable online sources. Extract only factual, verifiable data - never generate or guess information.

### PRIMARY DATA SOURCES (in priority order):
1. **Wikipedia** (Tamil & English pages)
2. **Google Maps** (business listings with reviews/photos)
3. **Official temple websites** (.org, .in domains)
4. **HRCE Tamil Nadu portal** (hrce.tn.gov.in)
5. **Government tourism sites** (tamilnadutourism.org)
6. **Verified temple directories** (templenet.com, etc.)

### EXTRACTION PROTOCOL

For each temple, extract the following JSON structure:

```json
{
  "temple_id": "unique_identifier",
  "basic_info": {
    "name_english": "verified_name",
    "name_tamil": "verified_tamil_name",
    "alternate_names": ["alt1", "alt2"],
    "primary_deity": "deity_name",
    "deity_tamil": "deity_tamil_name",
    "temple_type": "classification",
    "confidence_score": 0.95
  },
  "location": {
    "district": "district_name",
    "city": "city_name",
    "address": "full_verified_address",
    "pincode": "verified_pincode",
    "coordinates": {
      "latitude": 0.000000,
      "longitude": 0.000000,
      "coordinate_confidence": "high|medium|low",
      "coordinate_sources": ["google_maps", "wikipedia"]
    }
  },
  "historical_info": {
    "established_period": "period_if_known",
    "built_by": "builder_if_known",
    "architectural_style": "style_if_known",
    "inscriptions": "notable_inscriptions",
    "historical_significance": "brief_significance"
  },
  "temple_details": {
    "festivals": [
      {
        "name_english": "festival_name",
        "name_tamil": "tamil_name",
        "tamil_month": "tamil_month",
        "duration_days": 0,
        "significance": "brief_description"
      }
    ],
    "darshan_timings": {
      "morning": "time_range",
      "evening": "time_range",
      "special_days": "special_timings"
    },
    "special_features": ["feature1", "feature2"],
    "temple_tank": "tank_name_if_exists",
    "gopuram_count": 0,
    "total_area": "area_if_known"
  },
  "verification_data": {
    "sources_used": [
      {
        "source": "wikipedia",
        "url": "exact_url",
        "reliability": "high|medium|low",
        "last_accessed": "2024-date"
      }
    ],
    "data_completeness": 0.85,
    "needs_verification": ["field1", "field2"],
    "extraction_date": "2024-date",
    "extractor_notes": "any_important_notes"
  }
}
```

### EXTRACTION RULES

#### 1. SOURCE VERIFICATION
- **ONLY** extract data that has clear source attribution
- Cross-verify coordinates using minimum 2 sources
- Mark confidence levels: high (3+ sources), medium (2 sources), low (1 source)
- Prefer government/official sources over user-generated content

#### 2. TAMIL TEXT HANDLING
- Extract Tamil names exactly as they appear in sources
- Use Unicode Tamil characters (not romanized)
- Verify Tamil spellings against multiple sources
- Include both traditional and modern spellings if different

#### 3. COORDINATE VALIDATION
```
COORDINATE CHECK PROTOCOL:
1. Extract from Google Maps first (most reliable)
2. Cross-check with Wikipedia coordinates
3. Verify location makes geographical sense
4. Flag if coordinates differ by >1km between sources
5. Mark confidence: high (<100m diff), medium (<500m), low (>500m)
```

#### 4. DATA QUALITY GATES
- **Temple Name**: Must have English + Tamil from reliable source
- **Location**: District and city must be verifiable
- **Deity**: Must be clearly stated in source
- **Coordinates**: Must pass validation protocol
- **Sources**: Minimum 2 sources for core data

### PRIORITY TEMPLE GROUPS (Target: 250 temples)

#### Tier 1: High-Priority Groups (150 temples)
1. **Divya Desams** (108 temples) - Excellent Wikipedia coverage
2. **Paadal Petra Sthalams** (275 total, extract top 42)

#### Tier 2: Major Regional Temples (100 temples)
3. **District Headquarters Temples** (32 major temples)
4. **Navagraha Temples** (9 temples)
5. **Pancha Bhoota Sthalams** (5 temples)
6. **Saptha Vidangam** (7 temples)
7. **Major Amman Temples** (47 selected temples)

### BATCH PROCESSING STRATEGY

#### Phase 1: High-Data-Availability Temples
Target temples with:
- Dedicated Wikipedia pages
- Google Maps business listings
- Official websites
- Government recognition

#### Phase 2: Documentation-Rich Temples
Target temples with:
- HRCE registration
- Tourism department listings
- Academic research papers
- Archaeological survey records

### EXTRACTION WORKFLOW

1. **Pre-Search**: Verify temple exists in target sources
2. **Data Collection**: Extract from all available sources
3. **Cross-Verification**: Compare data across sources
4. **Quality Check**: Apply validation rules
5. **Gap Analysis**: Identify missing critical data
6. **Source Documentation**: Record all source URLs and access dates

### FALLBACK STRATEGIES

#### For Missing Data:
- Mark field as `"needs_verification": true`
- Note in `extractor_notes` what sources were checked
- Assign low confidence score
- Prioritize for manual verification later

#### For Conflicting Data:
- Include all variants with source attribution
- Mark as `"conflicting_data": true`
- Note discrepancies in `extractor_notes`
- Flag for expert review

### QUALITY ASSURANCE CHECKLIST

Before finalizing each temple record:
- [ ] Temple name verified in Tamil and English
- [ ] Coordinates validated against 2+ sources
- [ ] Primary deity clearly identified
- [ ] District and city confirmed
- [ ] Minimum 2 reliable sources documented
- [ ] Tamil text properly encoded in Unicode
- [ ] Confidence scores assigned to uncertain data
- [ ] Missing data marked for verification

### OUTPUT FORMAT

Generate one JSON file per temple with filename: `temple_[district]_[temple_name_english].json`

Include a summary report:
```json
{
  "extraction_summary": {
    "total_temples_processed": 0,
    "successful_extractions": 0,
    "incomplete_records": 0,
    "average_data_completeness": 0.0,
    "high_confidence_records": 0,
    "needs_manual_verification": 0
  }
}
```

### BATCH EXECUTION COMMAND

For web scraping tools or AI assistants:

"Extract verified temple data for [temple_name] following the Tamil Nadu Temple Extraction Protocol. Use Wikipedia, Google Maps, and official sources only. Return JSON with source verification and confidence scores. Mark any uncertain data for manual verification."

---

## USAGE EXAMPLES

### For AI Assistant:
"Using the Tamil Nadu Temple Extraction Protocol, collect verified data for Brihadeeswarar Temple, Thanjavur. Cross-verify coordinates, extract Tamil names, and document all sources."

### For Web Scraper:
"Target: Meenakshi Amman Temple, Madurai. Apply extraction protocol, validate coordinates against Google Maps + Wikipedia, ensure Tamil Unicode compliance."

### For Batch Processing:
"Process Divya Desam temples 1-20 using extraction protocol. Prioritize high-confidence data, mark incomplete records for verification."