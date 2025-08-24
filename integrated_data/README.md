# Temple Calendar App - Data Structure

## Main Data Files (Git Tracked)

### `integrated_data/unified_temple_data.json`
The main dataset with all 46,004 temples. This is the single source of truth.
- Track changes with Git commits
- No more v2, v3 suffixes needed

### `enriched_data/temple_enrichments.json`
Consolidated enrichment data:
- Coordinates from OpenStreetMap
- Website URLs
- Manual corrections
- Metadata about sources

### `festivals/universal_festivals_2025.json`
Festival calendar data (kept separate for efficiency)

## Version History
Use `git log` to see the history of changes:
```bash
git log --oneline integrated_data/unified_temple_data.json
```

## Rollback to Previous Version
```bash
git checkout <commit-hash> -- integrated_data/unified_temple_data.json
```

## Data Statistics
- Total temples: 46,004
- Temples with coordinates: 440
- Major temples (income > 10L): 578
- Major temples with coordinates: 428 (74%)

Last enrichment: 2025-08-24
