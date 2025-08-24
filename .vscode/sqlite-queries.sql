-- Tamil Temple Calendar - Useful SQLite Queries
-- Use with SQLite extension in VSCode

-- ============================================
-- BASIC QUERIES
-- ============================================

-- 1. View first 10 temples
SELECT temple_id, name, district, income_category 
FROM temples 
LIMIT 10;

-- 2. Count temples by district
SELECT district, COUNT(*) as count 
FROM temples 
GROUP BY district 
ORDER BY count DESC;

-- 3. All major temples (income > 10 lakhs)
SELECT temple_id, name, district, latitude, longitude
FROM temples 
WHERE income_category = '46_iii'
ORDER BY name;

-- 4. Geocoded temples only
SELECT name, district, latitude, longitude 
FROM temples 
WHERE latitude IS NOT NULL 
AND longitude IS NOT NULL;

-- ============================================
-- SEARCH QUERIES
-- ============================================

-- 5. Search temple by name (change 'murugan' to your search)
SELECT * FROM temples 
WHERE LOWER(name) LIKE '%murugan%'
LIMIT 20;

-- 6. Find temples in specific district
SELECT temple_id, name, address 
FROM temples 
WHERE district = 'Thanjavur District';

-- 7. Temples near coordinates (10km radius from Madurai)
SELECT name, district,
       (6371 * acos(
           cos(radians(9.9252)) * cos(radians(latitude)) * 
           cos(radians(longitude) - radians(78.1198)) + 
           sin(radians(9.9252)) * sin(radians(latitude))
       )) AS distance_km
FROM temples
WHERE latitude IS NOT NULL
HAVING distance_km < 10
ORDER BY distance_km;

-- ============================================
-- STATISTICS
-- ============================================

-- 8. Summary statistics
SELECT 
    COUNT(*) as total_temples,
    COUNT(CASE WHEN income_category = '46_iii' THEN 1 END) as major_temples,
    COUNT(CASE WHEN latitude IS NOT NULL THEN 1 END) as geocoded,
    COUNT(CASE WHEN website IS NOT NULL AND website != '' THEN 1 END) as with_website
FROM temples;

-- 9. Income category distribution
SELECT 
    income_category,
    CASE income_category
        WHEN '46_iii' THEN '> 10 lakhs'
        WHEN '46_ii' THEN '5-10 lakhs'
        WHEN '46_i' THEN '< 5 lakhs'
        WHEN '49_i' THEN '< 10,000'
        ELSE 'Unknown'
    END as income_range,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM temples), 2) as percentage
FROM temples
GROUP BY income_category
ORDER BY count DESC;

-- 10. Districts with most temples
SELECT 
    district,
    COUNT(*) as total,
    COUNT(CASE WHEN income_category = '46_iii' THEN 1 END) as major_temples,
    COUNT(CASE WHEN latitude IS NOT NULL THEN 1 END) as geocoded
FROM temples
GROUP BY district
ORDER BY total DESC
LIMIT 10;

-- ============================================
-- EXPORT QUERIES
-- ============================================

-- 11. Export major temples as JSON (SQLite 3.33+)
SELECT json_object(
    'temple_id', temple_id,
    'name', name,
    'district', district,
    'coordinates', json_object(
        'latitude', latitude,
        'longitude', longitude
    )
) as json_data
FROM temples
WHERE income_category = '46_iii'
AND latitude IS NOT NULL;

-- 12. Export for maps (CSV format)
SELECT 
    name,
    latitude,
    longitude,
    district,
    income_category
FROM temples
WHERE latitude IS NOT NULL;

-- ============================================
-- FESTIVAL QUERIES
-- ============================================

-- 13. Upcoming festivals
SELECT * FROM festivals
WHERE date >= date('now')
ORDER BY date
LIMIT 20;

-- 14. Festivals by type
SELECT festival_type, COUNT(*) as count
FROM festivals
GROUP BY festival_type;

-- ============================================
-- DATA QUALITY CHECKS
-- ============================================

-- 15. Temples with missing data
SELECT 
    'Missing District' as issue,
    COUNT(*) as count
FROM temples WHERE district IS NULL OR district = ''
UNION ALL
SELECT 
    'Missing Address' as issue,
    COUNT(*) as count
FROM temples WHERE address IS NULL OR address = ''
UNION ALL
SELECT 
    'Missing Coordinates' as issue,
    COUNT(*) as count
FROM temples WHERE latitude IS NULL
UNION ALL
SELECT 
    'Has Coordinates' as issue,
    COUNT(*) as count
FROM temples WHERE latitude IS NOT NULL;

-- ============================================
-- ADVANCED QUERIES
-- ============================================

-- 16. Cluster analysis - temples per sq km by district
WITH district_stats AS (
    SELECT 
        district,
        COUNT(*) as temple_count,
        COUNT(CASE WHEN latitude IS NOT NULL THEN 1 END) as geocoded_count,
        AVG(latitude) as avg_lat,
        AVG(longitude) as avg_lon
    FROM temples
    WHERE district IS NOT NULL
    GROUP BY district
)
SELECT 
    district,
    temple_count,
    geocoded_count,
    ROUND(avg_lat, 4) as center_lat,
    ROUND(avg_lon, 4) as center_lon
FROM district_stats
WHERE geocoded_count > 0
ORDER BY temple_count DESC;

-- 17. Find duplicate temples (by name and district)
SELECT name, district, COUNT(*) as count
FROM temples
GROUP BY name, district
HAVING count > 1
ORDER BY count DESC;

-- 18. Random sample of temples
SELECT * FROM temples
ORDER BY RANDOM()
LIMIT 10;