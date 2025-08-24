-- Sample SQLite Queries for Temple Database

-- 1. Find all temples in a district
SELECT temple_id, name, address 
FROM temples 
WHERE district = 'Chennai District';

-- 2. Find major temples with coordinates
SELECT name, latitude, longitude 
FROM major_temples 
WHERE latitude IS NOT NULL;

-- 3. Search temples by name (fuzzy)
SELECT * FROM temples 
WHERE name LIKE '%murugan%' 
LIMIT 10;

-- 4. Find temples near a location (10km radius)
SELECT name, district, 
       (6371 * acos(cos(radians(11.0168)) * cos(radians(latitude)) * 
        cos(radians(longitude) - radians(76.9558)) + 
        sin(radians(11.0168)) * sin(radians(latitude)))) AS distance_km
FROM geocoded_temples
HAVING distance_km < 10
ORDER BY distance_km;

-- 5. Get temples by income category
SELECT income_category, COUNT(*) as count 
FROM temples 
GROUP BY income_category 
ORDER BY count DESC;

-- 6. Get upcoming festivals
SELECT date, festival_name, festival_type 
FROM festivals 
WHERE date >= date('now') 
ORDER BY date 
LIMIT 10;

-- 7. Temple statistics by district
SELECT district, 
       COUNT(*) as total,
       COUNT(CASE WHEN latitude IS NOT NULL THEN 1 END) as geocoded
FROM temples 
GROUP BY district 
ORDER BY total DESC;

-- 8. Export specific temple data as JSON
SELECT json_object(
    'id', temple_id,
    'name', name,
    'location', json_object('lat', latitude, 'lon', longitude)
) as json_data
FROM temples 
WHERE temple_id = 'TM018025';
