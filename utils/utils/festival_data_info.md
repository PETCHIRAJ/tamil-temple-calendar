# Festival Data Information

## Complete Festival Data Available

We have recovered comprehensive festival data from the previous version with **88 total festivals** for 2025:

### Festival Categories:
1. **Major Annual Festivals** (15) - Pongal, Deepavali, Tamil New Year, etc.
2. **Pradosham** (24) - Shiva worship on 13th lunar day (twice monthly)
3. **Ekadashi** (25) - Vishnu worship on 11th lunar day (twice monthly)  
4. **Pournami** (12) - Full moon observances (monthly)
5. **Amavasya** (12) - New moon observances (monthly)

### Data Location:
- **Recovered JSON**: `recovered_festivals_2025.json`
- **Original location**: `festivals/universal_festivals_2025.json` (in git history)
- **Commit**: 497fc78

### Data Quality:
- ✅ Validated against 2025 Tamil calendar
- ✅ Includes Tamil month names (Thai, Masi, Panguni, etc.)
- ✅ Tamil names for all festivals
- ✅ Special types identified (Shani Pradosham, Soma Pradosham, etc.)

### Festival Generation Script:
The original data was generated using astronomical calculations via Swiss Ephemeris library to ensure accuracy based on lunar positions. The generation script (`generate_universal_festivals.py`) calculates:
- Tithi (lunar day) based festivals
- Nakshatra (star) based observances
- Tamil calendar correlations

For future years, the generation script would need to be run again with the appropriate year parameter.

## How to Use:
1. The JSON file contains all festival data structured by type
2. Each festival has date, Tamil name, Tamil month, and type
3. Can be integrated into any calendar application
4. Suitable for temple-specific filtering (Shiva temples for Pradosham, Vishnu for Ekadashi)