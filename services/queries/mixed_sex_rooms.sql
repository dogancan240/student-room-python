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
