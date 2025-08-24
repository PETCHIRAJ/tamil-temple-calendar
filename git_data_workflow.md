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
# See all changes to the database
git log --oneline data/temples.db

# See all changes to the JSON backup
git log --oneline data/temples.json

# See what changed between commits
git diff HEAD~1 HEAD data/temples.json
```

### Making Changes
```bash
# 1. Make your data changes (run enrichment scripts, etc.)
python3 enrich_more_temples.py

# 2. Regenerate SQLite database
python3 migrate_to_sqlite.py

# 3. Check what changed
git status
git diff data/temples.json

# 4. Commit both JSON and SQLite
git add data/temples.json data/temples.db
git commit -m "feat: Add coordinates for 50 more temples"
```

### Rollback Changes
```bash
# Undo uncommitted changes
git checkout -- data/temples.json data/temples.db

# Revert to specific commit
git checkout <commit-hash> -- data/temples.json data/temples.db
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
data/
├── temples.db                  # Primary SQLite database (Git tracked)
├── temples.json                # JSON backup (Git tracked)
├── enrichments.json            # Geocoding metadata (Git tracked)
├── festivals_2025.json         # Festival dates (Git tracked)
└── sample_queries.sql          # SQL examples

samples/
├── temples_sample_20.json      # Test dataset
└── major_temples_578.json      # High-income temples

reference/
├── deity_patterns.json         # Deity identification
└── income_categories.json      # Temple classifications
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
   git tag -a v1.2 -m "SQLite database with 88 festival dates"
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

### New Way (Git + SQLite):
```
temples.db                     # 64MB (indexed, queryable)
temples.json                   # 50MB (backup)
.git/                          # ~20MB compressed history
Total: ~134MB with full history + database
```

## Migration Complete ✅

Successfully migrated from file versioning to Git + SQLite:
```bash
# Removed 94 duplicate files
# Cleaned 7 empty directories
# Reduced repo from 300MB to 115MB
# All history preserved in Git
```

### Current Workflow
1. Edit data using Python scripts
2. Update both JSON and SQLite
3. Commit both files together
4. Use SQLite for app, JSON for backup