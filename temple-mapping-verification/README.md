# 🔍 Temple Mapping & Verification

## Overview
This folder contains all files related to mapping FindMyTemple scraped data (284 temples) to the existing HRCE database (46,004 temples).

## Status: 🟡 VERIFICATION IN PROGRESS

## Files

### Mapping Scripts
- **`match_temples.py`** - Main temple matching script with confidence scoring
- **`create_verification_file.py`** - Generates verification files for manual/LLM review
- **`temple_analysis_robust.py`** - Data quality analysis script

### Generated Outputs
- **`temple_id_mapping.json`** - Automated mapping results (183 matches found)
- **`temple_verification_manual.json`** - Full details for manual verification
- **`temple_verification_simple.csv`** - Simplified CSV for quick review
- **`matching_validation_report.md`** - Human-readable validation report
- **`comprehensive_temple_analysis.json`** - Complete data analysis

## Current Statistics

### Matching Results
- **Total Temples**: 284 from FindMyTemple
- **Matched**: 183 temples (64.4%)
  - Possible matches (70-79%): 14
  - Weak matches (50-69%): 169
  - No matches: 101

### Data Quality
- **No duplicates** found in scraped data
- **Average completeness**: 73.5%
- **District inconsistency**: Tanjore vs Thanjavur

## Verification Process

### Step 1: Review Matches
Open `temple_verification_simple.csv` in Excel:
- Check if temple names match
- Verify districts align
- Confirm deity information

### Step 2: Manual Verification
For each temple in `temple_verification_manual.json`:
1. Review `findmytemple_data`
2. Check `potential_db_matches`
3. Select best match or mark as "new_temple"
4. Add notes for questionable matches

### Step 3: LLM Assistance
Use this prompt with the JSON file:
```
Review the temple matching data in this JSON. 
For each temple, determine if the best potential match is correct based on:
- Name similarity (consider variations)
- Location (district, city)
- Main deity
- Other identifying features

Mark confidence as:
- "verified" if match score >70 and details align
- "needs_review" if uncertain
- "new_temple" if no good match exists
```

## Decision Matrix

| Confidence | Action | Count |
|------------|--------|-------|
| 70%+ | Review & likely accept | 14 |
| 60-69% | Manual verification needed | ~100 |
| 50-59% | Careful review required | ~70 |
| <50% | Likely new temples | 101 |

## Next Steps

1. **Complete verification** of matches
2. **Decide on unmatched temples**: Add as new or find manual matches
3. **Run migration** after verification complete

## Important Notes

⚠️ **DO NOT MODIFY DATABASE** until verification is complete
⚠️ **PRESERVE ORIGINAL DATA** - all changes should be reversible
⚠️ **DOCUMENT DECISIONS** - note why matches were accepted/rejected

## Commands

### Re-run matching
```bash
python3 temple-mapping-verification/match_temples.py
```

### Generate new verification files
```bash
python3 temple-mapping-verification/create_verification_file.py
```

### Analyze data quality
```bash
python3 temple-mapping-verification/temple_analysis_robust.py
```

---
*Last Updated: 2025-08-25*
*Status: Verification in Progress*