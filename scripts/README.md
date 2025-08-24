# Scripts Directory

## Active Scripts

### `migrate_to_sqlite.py`
- **Purpose:** Converts JSON data to SQLite database
- **Usage:** `python3 migrate_to_sqlite.py`
- **Input:** `json_data/production/temples.json`
- **Output:** `database/temples.db`

## Legacy Scripts (Historical Reference)

The following scripts were used during the data collection and enrichment phase. They reference old directory structures and are kept for historical reference only:

### `enrich_578_temples_improved.py`
- Used to geocode 428 major temples
- References old `integrated_data/` structure

### `validate_and_integrate.py`
- Used to merge and validate enrichment data
- References old v2/v3 file structure

### `temple_calendar_calculator.py`
- Festival calculation logic
- Can be adapted for future use

### `hrce_subdomain_scraper.py`
- Attempted to scrape HR&CE subdomains
- Limited success (2 temples)

### `consolidate_data.py`
- Used to consolidate initial data files
- No longer needed with SQLite

## Note
If you need to run any legacy scripts, you'll need to update the file paths to match the new structure:
- `integrated_data/` → `json_data/production/`
- `enriched_data/` → `json_data/enrichments/`
- `festivals/` → `json_data/festivals/`
- `data/` → `database/`