CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    birthday DATE NOT NULL,
    sex VARCHAR(10) NOT NULL,
    room_id INTEGER NOT NULL,
    CONSTRAINT fk_students_room
        FOREIGN KEY (room_id)
        REFERENCES rooms(id)
);