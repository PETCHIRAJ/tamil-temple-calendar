
# Website Validation Report
Date: 2025-08-24

## Summary
- Total URLs tested: 45
- Valid URLs: 5 (11.1%)
- Invalid URLs: 40 (88.9%)

## Valid Websites

### HR&CE Subdomains (3 valid)
1. **Bannari Mariamman Temple** (TM010245)
   - URL: https://bannarimariamman.hrce.tn.gov.in ✓

2. **Kapaleeswarar Temple, Mylapore** (TM000001)
   - URL: https://mylaikapaleeswarar.hrce.tn.gov.in ✓
   - Note: Subdomain is 'mylaikapaleeswarar' not 'kapaleeswarar'

3. **Parthasarathy Temple, Triplicane** (TM000005)
   - URL: https://parthasarathy.hrce.tn.gov.in ✓

### Custom Domains (2 valid but location mismatch)
4. **Pachaiamman Temple** (TM000338)
   - URL: https://www.pachaiamman.com ✓
   - Issue: Website is for Namakkal temple, not Chennai

5. **Agastheeswarar Temple** (TM037926)
   - URL: https://agastheeswarartemple.com ✓
   - Location: Ashok Nagar, Chennai

## Key Findings

1. **Automated discovery has very low accuracy (11.1%)**
   - Generic patterns like mariamman.in don't exist
   - Most temples don't have dedicated websites

2. **HR&CE subdomains more reliable (75% accuracy)**
   - But still need verification
   - Subdomain names may differ from temple names

3. **Location mismatches occur**
   - Some websites exist but for different temple locations
   - Database location data needs verification

## Recommendations

1. **Manual verification required** for all website discoveries
2. **Focus on HR&CE subdomains** as they're more reliable
3. **Wikipedia links** might be better alternative for temple information
4. **Consider removing** website field for temples without verified URLs
