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
