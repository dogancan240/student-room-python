SELECT
    r.id AS room_id,
    r.name AS room_name,
    COUNT(s.id) AS student_count
FROM rooms r
LEFT JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
ORDER BY r.id;
