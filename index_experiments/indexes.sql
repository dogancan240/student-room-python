-- Recommended indexes for the required room/student analytics queries.

CREATE INDEX IF NOT EXISTS idx_students_room_id
ON students(room_id);

CREATE INDEX IF NOT EXISTS idx_students_room_id_birthday
ON students(room_id, birthday);

CREATE INDEX IF NOT EXISTS idx_students_room_id_sex
ON students(room_id, sex);
