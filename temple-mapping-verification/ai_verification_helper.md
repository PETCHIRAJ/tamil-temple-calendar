# AI-Assisted Temple Verification Guide

## 🤖 Using AI to Help Verify Temples

Since manual verification of 284 temples is tedious, here's how to use AI (Claude, ChatGPT, etc.) to help:

### Option 1: Batch Verification with AI

1. **Export a subset of data** (10-20 temples at a time)
2. **Create a prompt template**:

```
I need help verifying temple matches. For each temple below, tell me if the match seems correct based on:
- Name similarity (considering Tamil transliterations)
- Location match (district, city)
- Deity match
- Any red flags

Temple 1:
FindMyTemple: [Name, Location, Deity, Festivals]
HRCE Match: [Name, Location, Deity, Type]
Confidence Score: XX%

Please respond with: CORRECT, WRONG, or UNSURE (with reason)
```

### Option 2: Focus on Problem Cases

Instead of reviewing all 284 temples, focus on:

1. **Skip High Confidence (>80%)** - Usually correct
2. **Review Medium (60-80%)** - 34 temples only
3. **Mark Low (<60%) as NEW** - 210 temples likely wrong

This reduces your review from 284 to just 34 temples!

### Option 3: Pattern-Based Auto-Verification

Common patterns that indicate CORRECT matches:
- ✅ Same district + Similar name = Usually correct
- ✅ Same deity type + Same location = Usually correct
- ✅ Temple ID patterns match (TM + district code)

Common patterns that indicate WRONG matches:
- ❌ Shiva temple matched to Vishnu temple
- ❌ Different districts (unless boundary areas)
- ❌ Completely different deity names

### Option 4: Quick Verification Rules

**AUTO-APPROVE if ALL true:**
- Confidence > 85%
- Same district
- Name similarity > 80%
- Same deity type

**AUTO-REJECT if ANY true:**
- Confidence < 50%
- Different deity types (Shiva vs Vishnu)
- Different districts (not neighboring)

**MANUAL REVIEW if:**
- Confidence 50-85%
- Neighboring districts
- Name variations but same deity

## 🎯 Recommended Workflow

### Step 1: Auto-Process Safe Matches
```python
# Run this to separate safe/unsafe matches
python3 safe_verification_process.py
```

### Step 2: Review the Report
Open `verification_safety_report.md` to see:
- Safe matches (can auto-approve)
- Suspicious matches (need review)
- Wrong matches (mark as new)

### Step 3: Quick Manual Review
Only review the "NEEDS REVIEW" section (34 temples)

### Step 4: Use This Decision Tree

```
Is confidence > 80%?
  YES → Is deity type same?
    YES → ✅ APPROVE
    NO → ⚠️ REVIEW
  NO → Is confidence > 60%?
    YES → Check location match
      Same district → ⚠️ REVIEW
      Different → ❌ REJECT
    NO → ❌ REJECT (mark as NEW)
```

## 💡 Time-Saving Tips

1. **Bulk Actions in UI**
   - Select all low confidence (<60%) 
   - Mark as "New Temple" in bulk
   - Only manually review medium confidence

2. **Use Search/Filter**
   - Filter by confidence level
   - Process in batches
   - Start with highest confidence

3. **Focus on Value**
   - 80% accuracy is better than 0% (no mapping)
   - Can always refine later
   - New temples can be added separately

## 🔒 Safety Measures

The system includes:
- **Backup before changes**
- **Undo script** to rollback
- **SQL preview** before execution
- **Confidence thresholds** to prevent bad matches
- **Suspicious pattern detection**

## 📊 Expected Results

Based on current data:
- **0 High confidence** matches (>80%) - Auto-approve
- **34 Medium confidence** (60-80%) - Quick review
- **210 Low confidence** (<60%) - Mark as new
- **40 No matches** - Already marked as new

**Total effort: Review only 34 temples instead of 284!**

## 🚀 Quick Start Commands

```bash
# 1. Export your verifications from UI
# Save as: temple_verifications_[date].json

# 2. Run safety analysis
python3 safe_verification_process.py

# 3. Review the report
open verification_safety_report.md

# 4. Apply safe updates only
sqlite3 ../database/temples.db < safe_update_[timestamp].sql

# 5. If something goes wrong, undo
python3 undo_mappings.py
```

## 📝 Notes for Special Cases

### Temples with Multiple Names
- Check if HRCE uses official name vs local name
- Example: "Kapaleeswarar" vs "Kapali Temple"

### Border Districts
- Temples near district borders may be listed differently
- Check neighboring districts if close match not found

### Historical Name Changes
- Some temples renamed over time
- Check historical_info field for old names

### Deity Name Variations
- Shiva: Sivan, Easwaran, Lingam, Nathar
- Vishnu: Perumal, Narayanan, Rama, Krishna
- Amman: Ambal, Devi, Shakti

Remember: **It's better to mark uncertain matches as "NEW" than to create wrong associations!**