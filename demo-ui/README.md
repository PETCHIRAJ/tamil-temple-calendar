# 🛕 Tamil Temple Guide - Demo UI

## Overview
This is the demo/prototype UI for the Tamil Temple Guide mobile application. It's a web-based version used for UI/UX iteration and stakeholder feedback before actual mobile app development.

## Project Structure
```
demo-ui/
├── v1-original/         # Original demo files (DO NOT MODIFY)
├── v2-current/          # Current working version (EDIT THIS)
├── data/                # Enhanced temple data
├── docs/                # Design documentation
├── serve.py             # Development server
└── iterations.log       # Version history
```

## Quick Start

### 1. Start Development Server
```bash
cd demo-ui
python3 serve.py
```
Then open: http://localhost:8080

### 2. Making Changes
- Always work in `v2-current/` directory
- Original files preserved in `v1-original/`
- Document changes in `iterations.log`

## Features

### Current Implementation (v1)
- ✅ Bilingual UI (Tamil/English)
- ✅ Temple search by name
- ✅ Filter by deity type
- ✅ Temple details view
- ✅ Responsive design
- ✅ Location-based features

### Data Structure
```json
{
  "temple_id": "TM001",
  "name": "Temple Name",
  "tamil_name": "கோயில் பெயர்",
  "district": "District",
  "deity_type": "Shiva|Vishnu|Murugan|Amman",
  "main_deity": "Main Deity Name",
  "goddess": "Goddess Name",
  "timings": "Temple Timings",
  "festivals": ["Festival1", "Festival2"],
  "holy_water": "Theertham names",
  "sacred_tree": "Tree name",
  "special_features": ["Feature1", "Feature2"],
  "latitude": 0.0,
  "longitude": 0.0,
  "data_completeness": 90
}
```

## UI Components

### Home Screen
- Search bar with Tamil/English placeholder
- Quick filter chips for deity types
- Popular temples grid
- Nearby temples button

### Temple Details Screen
- Header with temple name (bilingual)
- Photo gallery placeholder
- Information tabs:
  - Overview (தகவல்)
  - Timings (நேரம்)
  - Festivals (திருவிழாக்கள்)
  - Location (இடம்)

### Filter Screen
- Deity type selection
- District dropdown
- Distance slider
- Festival calendar

## Design Guidelines

### Colors
- Primary: Saffron `#FF6B35`
- Secondary: Blue `#2E86AB`
- Background: `#FFF5E6`
- Text: `#333333`

### Typography
- Tamil: Noto Sans Tamil
- English: System fonts
- Headers: Bold, 24px
- Body: Regular, 16px

### Icons
- Use cultural symbols
- Temple silhouettes
- Traditional patterns

## Development Notes

### To Add New Features
1. Edit files in `v2-current/`
2. Test using development server
3. Document changes in `iterations.log`
4. Create new version folder if major changes

### Data Updates
- Temple data: `data/enhanced_temple_data.json`
- Contains 30 sample temples
- Full dataset: 284 temples available

### Browser Testing
- Chrome (recommended)
- Safari
- Firefox
- Mobile responsive view

## Iteration Process

### Version Control
1. **v1-original**: Baseline demo (preserved)
2. **v2-current**: Active development
3. **v3-next**: (Create when v2 is stable)

### Change Log Format
```
Date: YYYY-MM-DD
Version: vX.Y
Changes:
- Change description 1
- Change description 2
Testing Notes:
- Test result 1
```

## Resources
- Design Doc: `docs/app-flow-design-doc.md`
- Temple Data: `data/enhanced_temple_data.json`
- Icons: Using Unicode temple symbols (🛕, 🕉️, ☪️)

## Next Steps
1. [ ] Implement map view
2. [ ] Add festival calendar
3. [ ] Enhance search filters
4. [ ] Add favorites functionality
5. [ ] Implement offline mode indicators

## Contact
For feedback and suggestions, document in `iterations.log` or create issues in the main project repository.

---
*Last Updated: 2025-08-25*