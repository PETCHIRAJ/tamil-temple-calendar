#!/bin/bash

# Setup script for separating code and data for privacy

echo "🔐 Setting up data privacy for temple-calendar-app"

# 1. Create sample data for public repo
echo "Creating sample dataset for public repo..."
python3 - <<EOF
import json
import random

# Load full data
with open('integrated_data/unified_temple_data.json', 'r') as f:
    full_data = json.load(f)

# Select 20 random temples as sample
temple_ids = list(full_data.keys())
sample_ids = random.sample(temple_ids, min(20, len(temple_ids)))
sample_data = {tid: full_data[tid] for tid in sample_ids}

# Save sample
with open('sample_data/temples_sample.json', 'w') as f:
    json.dump(sample_data, f, ensure_ascii=False, indent=2)

print(f"✅ Created sample with {len(sample_data)} temples")
EOF

# 2. Update .gitignore for public repo
echo "Updating .gitignore..."
cat >> .gitignore <<'GITIGNORE'

# Private Data (DO NOT COMMIT)
/integrated_data/unified_temple_data.json
/enriched_data/temple_enrichments.json
/enriched_data/*_final.json
/data/raw_data/
/data/major_temples_data/
/data/wikipedia_data/
/data/dinamalar_data/

# Keep only samples and documentation
!/sample_data/
!/integrated_data/README.md
!/data/*.py

# Credentials
.env
config/secrets.json
*_api_keys.json
GITIGNORE

# 3. Create private data directory structure
echo "Setting up private data storage..."
PRIVATE_DATA_DIR="$HOME/TempleDataPrivate"
mkdir -p "$PRIVATE_DATA_DIR"

# 4. Create sync script
cat > sync_private_data.sh <<'SYNC'
#!/bin/bash
# Sync private data to separate location

PRIVATE_DIR="$HOME/TempleDataPrivate"
PUBLIC_DIR="."

# Sync data files to private storage
rsync -av --progress \
  --include="integrated_data/unified_temple_data.json" \
  --include="enriched_data/*.json" \
  --exclude="sample_data/*" \
  "$PUBLIC_DIR/" "$PRIVATE_DIR/"

echo "✅ Private data synced to $PRIVATE_DIR"

# Optional: Encrypt sensitive data
# tar czf - "$PRIVATE_DIR" | openssl enc -aes-256-cbc -salt -out temple_data_backup.enc
SYNC

chmod +x sync_private_data.sh

# 5. Create README for data privacy
cat > DATA_PRIVACY.md <<'README'
# Data Privacy Policy

## Public Repository (GitHub)
This repository contains:
- ✅ Source code for temple calendar app
- ✅ Data collection scripts
- ✅ Sample dataset (20 temples)
- ✅ Documentation

## Private Data (Not on GitHub)
The following are stored privately:
- ❌ Full dataset (46,004 temples)
- ❌ Geocoding results for 428 temples
- ❌ Enrichment data
- ❌ API credentials

## Why This Approach?
1. **Protect Competitive Advantage**: Full dataset is valuable
2. **Prevent Unauthorized Use**: Avoid data scraping
3. **Maintain Control**: Can monetize or license data
4. **Open Source Code**: Community can contribute to code

## For Contributors
- Use `sample_data/temples_sample.json` for development
- Request access to full dataset if needed
- Never commit real data files to public repo

## Data Backup Strategy
1. Local Git for version control
2. Encrypted cloud backup (S3/Backblaze)
3. Physical backup on external drive
README

echo "
✅ Setup complete!

Next steps:
1. Run: ./sync_private_data.sh to backup private data
2. Review .gitignore before pushing to GitHub
3. Commit only code and sample data to public repo
4. Keep full dataset in ~/TempleDataPrivate/

Public repo will contain:
  - Code and scripts
  - Sample data (20 temples)
  - Documentation

Private storage will contain:
  - Full dataset (46,004 temples)
  - Enrichment data
  - API credentials
"