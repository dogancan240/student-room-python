SELECT
    r.id AS room_id,
    r.name AS room_name,
    ROUND(AVG((CURRENT_DATE - s.birthday) / 365.25)::numeric, 2)::float AS average_age
FROM rooms r
JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
ORDER BY average_age ASC, r.id
LIMIT 5;
