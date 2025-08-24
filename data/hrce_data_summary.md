# HR&CE Temple Data Discovery Summary

## What Information Can Be Scraped from HR&CE Website

### 1. Basic Temple Information (Already Have - 46,004 temples)
✅ **From GitHub Dataset:**
- Temple ID (TM format)
- Temple Name
- Address
- District
- Pincode
- Income Category
- Temple Type

### 2. Detailed Information from Temple Subdomains

Major temples have dedicated subdomains (e.g., `sankarankovilsankaranarayanar.hrce.tn.gov.in`)

✅ **Successfully Extracted:**

#### Temple Details
- Main deity name
- Other deities in the temple
- Full temple title with location

#### Temple Timings
- Opening hours (e.g., 05:00 AM - 12:30 PM)
- Closing hours (e.g., 12:30 PM - 04:00 PM)
- Special day timings (Friday, Sunday)
- Tamil descriptions of timings

#### Contact Information
- Pincode verification
- Location details

#### Images
- Temple photos (multiple views)
- Deity images
- Gallery images
- URLs to actual image files on HR&CE servers

#### Tamil Content
- Tamil names and terms
- Tamil descriptions
- Festival names in Tamil

### 3. Content That Appears Available (in JavaScript/Dynamic)

The HTML source shows forms and JavaScript for:
- **Festival Details** (`festival_details`, `festival_from_date`, `festival_to_date`)
- **Tamil Calendar Info** (`tamil_month`, `tamil_year`, `tamil_date`)
- **Nakshatra Details** (`nakshatra_details`)
- **Thithi Information** (`thithi_type`, `thithi`)
- **Pooja Details** (`onetime_pooja`, special poojas)
- **Special Functions** (`splfunctions`)

### 4. Temple Subdomain Pattern

Major temples follow this pattern:
```
https://[templename].hrce.tn.gov.in/
```

Examples found:
- `sankarankovilsankaranarayanar.hrce.tn.gov.in` (TM037875)
- `maduraimeenakshi.hrce.tn.gov.in` (TM031962)
- `parthasarathy.hrce.tn.gov.in` (TM000005)

### 5. Data Availability by Temple Category

| Income Category | Temple Count | Likely Has Subdomain | Rich Data Available |
|----------------|--------------|---------------------|-------------------|
| >₹10 lakh (46_iii) | 578 | Yes (most) | Yes |
| ₹2-10 lakh (46_ii) | 6,660 | Some | Limited |
| ₹10k-2 lakh (46_i) | 3,779 | Few | Basic |
| <₹10k (49_i) | 34,987 | No | Minimal |

### 6. Recommended Scraping Strategy

1. **Use existing GitHub dataset** for basic info (46,004 temples) ✅
2. **Identify temples with subdomains** (likely 500-1000 major temples)
3. **Scrape subdomain content** for rich details:
   - Temple images
   - Timings
   - Contact info
   - Basic festival/pooja mentions
4. **Use Selenium if needed** for JavaScript-rendered content
5. **Store enhanced data** combining basic + detailed info

### 7. Limitations Discovered

- Direct temple URLs (`index_temple.php?tid=`) return 404 errors
- Main HR&CE site has date synchronization requirements
- Festival/Pooja details are in JavaScript forms (harder to extract)
- Not all temples have subdomains (only major ones)

### 8. Next Steps for App Development

With the data we can access:

1. **Temple Directory** - Complete list of 46,004 temples ✅
2. **Temple Profiles** - Rich profiles for ~500-1000 major temples
3. **Temple Images** - Photo galleries for major temples
4. **Timing Information** - Open/close times, special days
5. **Basic Festival Info** - Names and general dates
6. **Search & Filter** - By district, income category, deity
7. **Tamil Support** - Tamil names and descriptions available

## Files Generated

- `raw_data/tn_temples_full.json` - All 46,004 temples
- `raw_data/major_temples_test.json` - 10 major temples for testing
- `raw_data/temple_subdomain_data.json` - Detailed data from 3 temples
- `raw_data/temple_details/*.html` - Full HTML pages for analysis

## Conclusion

We have sufficient data to build a comprehensive Tamil temple calendar app:
- Basic info for ALL temples in Tamil Nadu
- Rich details for major temples
- Temple timings and images
- Foundation for festival calendar features