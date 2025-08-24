# 📚 Temple Calendar Data Collection Guide
*Complete documentation of data sources and collection techniques*

## 🎯 Overview
This document captures all data sources, collection techniques, and validation methods discovered during the Sankarankovil Temple calendar research (December 2024).

## 📊 Data Categories & Coverage

### 1. Calculable Data (70% - No External Source Needed)
These can be generated programmatically using astronomical calculations:

| Data Type | Frequency | Calculation Method | Accuracy |
|-----------|-----------|-------------------|----------|
| **Pradosham** | 24/year | 13th tithi (Trayodashi) | 100% |
| **Ekadashi** | 24/year | 11th tithi | 95-100% |
| **Pournami** | 12-13/year | Full moon calculation | 100% |
| **Amavasya** | 12/year | New moon calculation | 100% |
| **Chaturthi** | 24/year | 4th tithi (Ganesha) | 100% |
| **Shashti** | 24/year | 6th tithi (Muruga) | 100% |
| **Ashtami** | 24/year | 8th tithi (Durga) | 100% |
| **Shivaratri** | 12/year | Krishna Chaturdashi | 100% |
| **Karthigai** | 12/year | Krittika nakshatra | 100% |
| **Rahu Kalam** | Daily | Weekday-based calculation | 100% |
| **Gulikai** | Daily | Weekday-based calculation | 100% |

### 2. Scrapable Data (20% - One-time Collection)
Available from websites but needs periodic updates:

| Data Type | Sources | Update Frequency |
|-----------|---------|------------------|
| **Major Festivals** | HR&CE website, Temple sites | Annual |
| **Temple Info** | Wikipedia, Official sites | Rarely |
| **Government Holidays** | Tenkasi district website | As declared |

### 3. Manual/Crowdsourced Data (10%)
Not available online, needs local sources:

| Data Type | Collection Method |
|-----------|------------------|
| **Local Festivals** | WhatsApp groups, Priests |
| **Special Poojas** | Temple notice boards |
| **Village Deity Events** | Local contacts |

## 🔍 Primary Data Sources

### Government Sources
1. **HR&CE Tamil Nadu Portal**
   - URL: `https://hrce.tn.gov.in/`
   - Coverage: 36,000+ temples
   - Data: Major festivals, timings
   - Reliability: HIGH but incomplete

2. **District Websites**
   - Example: `https://tenkasi.nic.in/`
   - Data: Local holiday declarations
   - Update: Real-time announcements

### Calendar Websites
1. **Tamil Daily Calendar**
   - URL: `https://www.tamildailycalendar.com/`
   - Best for: Pradosham, Ekadashi lists
   - Format: Clean, structured

2. **Drik Panchang**
   - URL: `https://www.drikpanchang.com/`
   - Best for: Location-specific timings
   - Accuracy: Very high

3. **Prokerala Tamil Calendar**
   - URL: `https://www.prokerala.com/general/calendar/tamilcalendar.php`
   - Best for: Monthly views
   - Has: API options (paid)

### Tamil News Sites
1. **Dinamalar Temple Section**
   - URL: `https://temple.dinamalar.com/`
   - Coverage: Major temples only
   - Updates: Sporadic

2. **Maalaimalar**
   - Religious section has festival info
   - Tamil content

### Hidden Gems
1. **Temple-specific Websites**
   - Example: `https://sankarankovilsankaranarayanar.hrce.tn.gov.in/`
   - Often outdated but has contact info

2. **Wikipedia Tamil**
   - Has 5000+ temple articles
   - Festival dates in Tamil

3. **Facebook Pages**
   - Most active source for updates
   - Real-time festival announcements

## 🛠️ Technical Implementation

### Swiss Ephemeris Approach
```python
# Core calculation logic
def calculate_tithi(date, latitude, longitude):
    """
    Calculate Hindu tithi based on sun-moon angle
    Each tithi = 12° angular distance
    """
    sun_longitude = calculate_sun_position(date)
    moon_longitude = calculate_moon_position(date)
    tithi = ((moon_longitude - sun_longitude) % 360) / 12
    return int(tithi)
```

### Key Libraries/Tools
1. **Python Libraries**
   - `pyswisseph` - Swiss Ephemeris Python wrapper
   - `astral` - Sunrise/sunset calculations
   - `ephem` - Alternative astronomical library

2. **Data Storage**
   - SQLite for offline storage
   - JSON for configuration
   - Pre-calculate 50 years of data

## 📱 Data Collection Workflow

### Phase 1: Setup (Day 1)
```bash
1. Install calculation libraries
2. Set up temple coordinates database
3. Create validation spreadsheet
```

### Phase 2: Calculate (Day 2-3)
```python
# Generate all calculable events
for temple in temples:
    for year in [2025, 2026]:
        calendar = calculate_full_calendar(
            temple.lat, 
            temple.lon, 
            year
        )
        save_to_database(calendar)
```

### Phase 3: Scrape (Day 4-5)
```python
# One-time scraping
sources = [
    'hrce.tn.gov.in',
    'wikipedia.org',
    'temple_websites'
]
for source in sources:
    festivals = scrape_major_festivals(source)
    validate_and_store(festivals)
```

### Phase 4: Validate (Day 6-7)
- Send WhatsApp to local contacts
- Compare with printed panchangams
- Cross-check with multiple sources

## 🔐 Data Validation Techniques

### Multi-Source Verification
```python
def validate_date(event_date, event_type):
    sources = []
    sources.append(calculate_astronomically(event_date))
    sources.append(scrape_tamil_calendar(event_date))
    sources.append(check_drik_panchang(event_date))
    
    if agreement_percentage(sources) > 80:
        return "VALIDATED"
    return "NEEDS_MANUAL_CHECK"
```

### Accuracy Levels
- **Level 1**: 100% match across 3+ sources
- **Level 2**: Astronomical calculation + 1 source
- **Level 3**: Single source (mark as "unverified")

## 💡 Key Learnings

### What Works
1. ✅ Astronomical calculations are highly reliable
2. ✅ Government holiday declarations are authoritative
3. ✅ Tamil Daily Calendar for Pradosham/Ekadashi
4. ✅ Location-specific calculations matter

### What Doesn't Work
1. ❌ Relying on single sources
2. ❌ Expecting complete data from any one site
3. ❌ Temple websites (often outdated)
4. ❌ Automated translation of Tamil content

### Surprises
1. 🎯 Facebook pages more updated than official sites
2. 🎯 WhatsApp groups have exclusive information
3. 🎯 Priests willing to help if approached respectfully
4. 🎯 Swiss Ephemeris eliminates need for expensive APIs

## 📈 Scalability Strategy

### For 100 Temples
```python
# Batch processing approach
temples = load_temple_coordinates()  # CSV with lat/lon
calendars = {}

for temple in temples:
    # Calculate once, store forever
    calendars[temple.id] = generate_calendar(
        temple.lat,
        temple.lon,
        years=[2025, 2026, 2027]
    )

# One-time scraping for special festivals
special_festivals = batch_scrape_festivals(temples)

# Combine and store
combined_data = merge(calendars, special_festivals)
save_to_sqlite(combined_data)
```

### For 1000+ Temples
- Pre-calculate 10 years of data
- Use regional clustering (same sunrise zone)
- Implement caching for common queries
- Add user contribution system

## 🚀 Quick Start Commands

### Get Temple Coordinates
```python
# From Wikipedia
temples = scrape_wikipedia_temple_coords()

# From Google Maps API (if needed)
coords = geocode_temple_address(temple_name)
```

### Generate Calendar
```python
from temple_calendar import TempleCalendar

calendar = TempleCalendar(
    name="Meenakshi Temple",
    lat=9.9195,
    lon=78.1193,
    year=2025
)

full_calendar = calendar.generate_complete_calendar()
calendar.export_to_json("meenakshi_2025.json")
```

## 📞 Useful Contacts

### For Validation
- Tamil panchangam publishers
- Local temple priests
- Tamil astrology forums
- District administration (for holidays)

### Developer Resources
- Swiss Ephemeris documentation
- ISKCON calendar for Ekadashi
- Drik vs Vakya panchangam differences

## 🎯 Success Metrics

### MVP Success Criteria
- [ ] 100 temples with basic calendar
- [ ] 95% accuracy on Pradosham/Ekadashi
- [ ] Major festivals included
- [ ] Offline functionality

### Version 2.0 Goals
- [ ] 1000+ temples
- [ ] User corrections system
- [ ] Multi-language support
- [ ] Festival notifications

## 💾 Data Backup

### Storage Structure
```
temple-calendar-app/
├── data/
│   ├── calculated/
│   │   ├── 2025_tithis.json
│   │   ├── 2025_nakshatras.json
│   │   └── 2025_daily_timings.json
│   ├── scraped/
│   │   ├── major_festivals.json
│   │   └── temple_info.json
│   └── validated/
│       └── final_calendar_2025.json
├── docs/
│   └── data_collection_guide.md
└── validation/
    ├── whatsapp_responses.txt
    └── validation_report.md
```

## 🔄 Update Schedule

### Annual Updates Needed
- Major festival dates (might shift)
- Government holiday declarations
- Temple renovation schedules

### Never Needs Updates
- Astronomical calculations
- Tithi-based events
- Daily timing algorithms

---

## 📝 Notes for Future

1. **Start Small**: Begin with 10 temples, perfect the process
2. **Validate Early**: Send to local contacts before scaling
3. **Document Everything**: This guide should evolve
4. **Respect Sources**: Credit data sources in app
5. **Stay Offline-First**: Don't depend on APIs that might disappear

---

*Last Updated: December 2024*
*Next Review: Before 2026 calendar generation*