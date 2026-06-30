-- room_student_counts
SELECT
    r.id AS room_id,
    r.name AS room_name,
    COUNT(s.id) AS student_count
FROM rooms r
LEFT JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
ORDER BY r.id;

-- smallest_average_age
SELECT
    r.id AS room_id,
    r.name AS room_name,
    ROUND(AVG((CURRENT_DATE - s.birthday) / 365.25)::numeric, 2)::float AS average_age
FROM rooms r
JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
ORDER BY average_age ASC, r.id
LIMIT 5;

-- largest_age_difference
SELECT
    r.id AS room_id,
    r.name AS room_name,
    ROUND(
        ((MAX(CURRENT_DATE - s.birthday) - MIN(CURRENT_DATE - s.birthday)) / 365.25)::numeric,
        2
    )::float AS age_difference
FROM rooms r
JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
HAVING COUNT(s.id) > 1
ORDER BY age_difference DESC, r.id
LIMIT 5;

-- mixed_sex_rooms
SELECT
    r.id AS room_id,
    r.name AS room_name,
    COUNT(s.id) AS student_count,
    COUNT(DISTINCT s.sex) AS sex_count
FROM rooms r
JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
HAVING COUNT(DISTINCT s.sex) > 1
ORDER BY r.id;
