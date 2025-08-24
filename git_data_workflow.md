# Git-Based Data Versioning Workflow

## Why Git Instead of v2/v3 Files?

1. **No Duplicate Files**: Single source of truth
2. **Full History**: Every change is tracked
3. **Easy Rollback**: Revert to any previous state
4. **Diffs**: See exactly what changed between versions
5. **Branching**: Experiment without affecting main data

## Common Commands

### View History
```bash
# See all changes to the main dataset
git log --oneline integrated_data/unified_temple_data.json

# See detailed changes in last commit
git show HEAD integrated_data/unified_temple_data.json

# See what changed between commits
git diff HEAD~1 HEAD integrated_data/unified_temple_data.json
```

### Making Changes
```bash
# 1. Make your data changes (run enrichment scripts, etc.)
python3 data/enrich_more_temples.py

# 2. Check what changed
git status
git diff integrated_data/unified_temple_data.json

# 3. Commit the changes
git add integrated_data/unified_temple_data.json
git commit -m "feat: Add coordinates for 50 more temples"
```

### Rollback Changes
```bash
# Undo uncommitted changes
git checkout -- integrated_data/unified_temple_data.json

# Revert to specific commit
git checkout <commit-hash> -- integrated_data/unified_temple_data.json
git commit -m "revert: Roll back to previous dataset"
```

### Branching for Experiments
```bash
# Create branch for experimental enrichment
git checkout -b experiment/alternate-geocoding

# Make changes...
python3 experimental_enrichment.py

# If successful, merge back
git checkout main
git merge experiment/alternate-geocoding

# If unsuccessful, just delete branch
git checkout main
git branch -D experiment/alternate-geocoding
```

## Data File Structure

```
integrated_data/
├── unified_temple_data.json    # Main dataset (Git tracked)
├── README.md                    # Documentation
└── [old v2/v3 files]           # Can be deleted

enriched_data/
├── temple_enrichments.json     # Consolidated enrichments (Git tracked)
├── coordinate_corrections.json # Manual corrections
└── [temporary files]           # Not tracked

festivals/
├── universal_festivals_2025.json # Festival calendar (Git tracked)
└── deity_patterns.json          # Deity identification patterns
```

## Best Practices

1. **Commit After Each Enrichment**
   ```bash
   git commit -m "feat: Add geocoding for Thanjavur district temples"
   ```

2. **Use Meaningful Commit Messages**
   - `feat:` New data or features
   - `fix:` Corrections to existing data
   - `docs:` Documentation updates
   - `refactor:` Restructuring without changing data

3. **Tag Important Milestones**
   ```bash
   git tag -a v1.0 -m "Initial 46,004 temples dataset"
   git tag -a v1.1 -m "Added coordinates for 428 major temples"
   ```

4. **Check File Size**
   - If files get > 100MB, consider Git LFS
   - Or split into smaller logical chunks

## Advantages Over File Versioning

### Old Way (File Versions):
```
unified_temple_data_v1.json    # 50MB
unified_temple_data_v2.json    # 50MB  
unified_temple_data_v3.json    # 50MB
unified_temple_data_backup.json # 50MB
Total: 200MB of mostly duplicate data
```

### New Way (Git):
```
unified_temple_data.json       # 50MB
.git/                          # ~10MB compressed diffs
Total: ~60MB with full history
```

## Migration Cleanup

Once comfortable with Git versioning, remove old files:
```bash
rm integrated_data/*_v2*.json
rm integrated_data/*_v3*.json
rm integrated_data/*backup*.json
git add -u
git commit -m "chore: Remove old versioned files after Git migration"
```