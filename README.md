# 🛕 Tamil Nadu Temple Calendar App

A comprehensive mobile app for discovering and navigating Tamil Nadu temples with real-time features.

## 📊 Project Status

**Phase:** MVP Prototype Ready for User Testing  
**Database:** 588 temples (127 with GPS navigation)  
**Prototype:** Working HTML demo with real data  
**Next Step:** User validation before Flutter development

## 🗂️ Project Structure

```
temple-calendar-app/
│
├── README.md              # Project overview (this file)
│
├── project-data/          # Core data and documentation
│   ├── database/         # SQLite databases
│   │   ├── temple_app_mvp.db      # Production DB (588 temples)
│   │   └── app_temples_unified.db # Development DB
│   │
│   └── documentation/    # Technical documentation
│       ├── DATABASE_DOCUMENTATION.md
│       └── DATA_ANALYSIS_SUMMARY.md
│
└── design/               # All design assets
    ├── wireframes/      # Text-based wireframes (11 files)
    └── mockups/         # Working HTML prototype
        ├── index.html
        ├── temple_data.json
        └── USER_TESTING_GUIDE.md
```

## 🚀 Quick Start

### Test the Prototype
```bash
cd design/mockups/demo-ui
python3 -m http.server 8000
# Open: http://localhost:8000
```

### Access Database
```python
import sqlite3
conn = sqlite3.connect('project-data/database/temple_app_mvp.db')
# 127 navigation-ready temples in 'app_temples' table
# 588 total temples in 'temple_directory' table
```

## 📱 Features

### Current (Prototype)
- ✅ **127 GPS-enabled temples** with navigation
- ✅ **588 searchable temples** across Tamil Nadu
- ✅ **4 tour circuits** (Navagraha, Murugan, etc.)
- ✅ **Real-time crowd levels** for 5 temples
- ✅ **Tamil/English** bilingual support
- ✅ **Interactive map** with temple locations
- ✅ **District/deity filtering**
- ✅ **Direct phone calls** to temples

### Planned (Flutter App)
- 🔄 User reviews and ratings
- 🔄 Festival notifications
- 🔄 Offline mode
- 🔄 Photo galleries
- 🔄 Prasadam booking

## 📊 Data Statistics

| Metric | Count | Coverage |
|--------|-------|----------|
| Total Temples | 588 | 100% |
| With GPS Navigation | 127 | 21.6% |
| Tour Circuit Temples | 15 | 100% GPS |
| Districts Covered | 30+ | All major |
| With Crowd Data | 5 | Premium |
| Average Rating | 4.73 | High quality |

## 🎯 Target Users

- Tamil families planning temple visits
- Elderly devotees (50+ age)
- Weekend pilgrimage planners
- Festival attendees
- Cultural tourists

## 🧪 User Testing

The HTML prototype is ready for user validation:

1. **Show to 5-10 potential users**
2. **Collect feedback using the testing guide**
3. **Success criteria:** 7/10 rating + download intent
4. **Decision:** Go/No-go for Flutter development

## 🛠️ Technology Stack

### Current Prototype
- HTML5 + CSS3 + JavaScript
- Leaflet.js for maps
- SQLite database
- Real temple data

### Planned App
- Flutter (iOS/Android)
- SQLite (sqflite package)
- Google Maps integration
- Firebase for analytics

## 📈 Success Metrics

### MVP Goals
- 50,000 downloads in year 1
- 4.5+ app store rating
- 20% monthly active users
- 2% premium conversion

### Unique Selling Points
- Real-time crowd levels (exclusive feature)
- Complete Tamil Nadu coverage
- Elder-friendly design
- Authentic Tamil experience

---

**Current Focus:** User testing and validation  
**Next Milestone:** Flutter development decision  
**Timeline:** Testing complete within 1 week