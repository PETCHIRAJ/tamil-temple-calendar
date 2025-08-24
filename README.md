# 🛕 Tamil Temple Calendar

A comprehensive Tamil temple calendar application with data for 46,000+ temples across Tamil Nadu.

## 📱 Project Vision
Create a Tamil temple calendar app that provides accurate religious dates without expensive APIs or server costs, targeting the underserved Tamil-speaking audience who currently rely on ad-heavy apps.

## 🎯 Key Achievements
- **46,004 temples** data collected from TN HR&CE
- **428 major temples geocoded** (74% success rate)
- **70% of dates calculable** using astronomical algorithms  
- **₹82,000/year savings** vs API approach
- **95-100% accuracy** on festival dates

## 📂 Project Structure
```
tamil-temple-calendar/
├── integrated_data/
│   └── unified_temple_data.json       # Main dataset (46,004 temples)
├── enriched_data/
│   └── temple_enrichments.json        # Geocoding & enrichments
├── festivals/
│   ├── universal_festivals_2025.json  # Validated festival dates
│   └── deity_patterns.json            # Deity identification
├── data/
│   ├── temple_calendar_calculator.py  # Festival calculator
│   ├── enrich_578_temples_improved.py # Geocoding script
│   └── validate_and_integrate.py      # Data validation
└── validation/
    └── sankarankovil_temple_2025_calendar.json  # Validated calendar
```

## ✅ Validation Results

### Sankarankovil Temple 2025
- **176 events calculated** programmatically
- **100% match** on Pradosham dates
- **95% match** on Ekadashi dates
- **Major festivals** identified and verified

### Ready for Ground Validation
- Tamil WhatsApp format prepared
- Send to local priests/contacts
- Compare with physical panchangam

## 🚀 Next Steps

### Immediate (Week 1)
1. [ ] Send Tamil validation doc to Sankarankovil contact
2. [ ] Refine calculations based on feedback
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