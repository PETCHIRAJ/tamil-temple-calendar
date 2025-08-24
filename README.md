# 🛕 Tamil Temple Calendar

A comprehensive Tamil temple calendar application with data for 46,000+ temples across Tamil Nadu.

## 📱 Project Vision
Create a Tamil temple calendar app that provides accurate religious dates without expensive APIs or server costs, targeting the underserved Tamil-speaking audience who currently rely on ad-heavy apps.

## 🎯 Key Achievements
- **46,004 temples** data collected from TN HR&CE
- **428 major temples geocoded** (74% of 578 high-income temples)
- **88 festival dates** for 2025 calculated and validated
- **64MB SQLite database** optimized for mobile apps
- **115MB clean repository** (reduced from 300MB)
- **95-100% accuracy** on festival dates

## 📂 Project Structure
```
tamil-temple-calendar/
├── data/
│   ├── temples.db                     # SQLite database (PRIMARY - 64MB)
│   ├── temples.json                   # JSON backup (50MB)
│   ├── enrichments.json               # Geocoding metadata
│   ├── festivals_2025.json            # 88 festival dates
│   └── sample_queries.sql             # SQL query examples
├── samples/
│   ├── temples_sample_20.json         # Testing dataset
│   └── major_temples_578.json         # High-income temples
├── reference/
│   ├── deity_patterns.json            # Deity identification
│   └── income_categories.json         # Temple classifications
└── docs/
    ├── data_collection_guide.md        # Collection methodology
    └── enhanced_data_strategy.md       # App development strategy
```

## ✅ Validation Results

### Database Features
- **Indexed queries** on district, income, coordinates
- **Full-text search** on temple names (Tamil/English)
- **Views** for major temples, geocoded temples
- **88 festival dates** imported and validated
- **VSCode integration** with SQLite extensions

### Data Quality
- **428 temples geocoded** using OpenStreetMap
- **578 major temples** identified (income > ₹10L/year)
- **Universal festivals** calculated astronomically
- **Git versioning** for all data changes

## 🚀 Quick Start

### Using the Database
```sql
-- Find temples in Chennai
SELECT name, address, latitude, longitude 
FROM temples 
WHERE district = 'Chennai District' 
AND latitude IS NOT NULL;

-- Get 2025 festivals
SELECT * FROM festivals WHERE year = 2025;

-- Major temples with coordinates
SELECT * FROM major_temples;
```

### VSCode Setup
1. Install SQLite extension: `SQLite Viewer` or `SQLite`
2. Open `data/temples.db`
3. Use `.vscode/sqlite-queries.sql` for common queries

## 🌟 Next Steps

### Development Ready
1. [ ] Start Flutter/React Native app with SQLite
2. [ ] Implement offline-first architecture
3. [ ] Add Tamil language support
3. [ ] Start Flutter app skeleton

### Short-term (Month 1)
1. [ ] Add 10 major temples (Madurai, Rameswaram, etc.)
2. [ ] Build basic Flutter UI
3. [ ] Implement notification system
4. [ ] Create home screen widget

### Medium-term (Month 2-3)
1. [ ] Scale to 100 temples
2. [ ] Add Tamil/English toggle
3. [ ] Implement offline panchangam
4. [ ] Launch beta version

## 💡 Unique Selling Points
1. **NASA-grade accuracy** using Swiss Ephemeris
2. **Completely offline** after initial download
3. **No ads** in premium version (₹99 one-time)
4. **Location-specific** calculations
5. **Daily widget** with Rahu Kalam

## 🛠️ Tech Stack
- **Calculations**: Python with Swiss Ephemeris
- **App**: Flutter (cross-platform)
- **Database**: SQLite (offline storage)
- **Languages**: Tamil + English

## 📊 Market Opportunity
- **10M+** downloads for competitor (Nithra)
- **Major complaint**: Too many ads
- **Gap**: Professional features, accuracy
- **Revenue**: ₹99 premium + minimal ads

## 📝 Important Learnings
1. Don't rely solely on web scraping (only 20% available)
2. Astronomical calculations are incredibly accurate
3. Tamil Facebook pages more updated than official sites
4. Local validation is crucial for temple-specific events

## 🔗 Resources
- [Swiss Ephemeris](https://www.astro.com/swisseph/)
- [Tamil Daily Calendar](https://www.tamildailycalendar.com/)
- [Drik Panchang](https://www.drikpanchang.com/)
- [HR&CE Tamil Nadu](https://hrce.tn.gov.in/)

## 📞 Validation Contacts
- Temple offices directly
- Local Tamil WhatsApp groups
- Tamil panchangam publishers

---

## 🔒 Repository Info

- **Repository**: [github.com/PETCHIRAJ/tamil-temple-calendar](https://github.com/PETCHIRAJ/tamil-temple-calendar)
- **Visibility**: Private (Protected from LLM training)
- **Data Safety**: Full dataset included (not crawled/scraped)

**Project Status**: Data enrichment complete. 428 major temples geocoded. Ready for app development.

**Created**: December 2024  
**Data Last Updated**: August 24, 2025