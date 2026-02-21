DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS fee_payments;

CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    room_number TEXT
);

CREATE TABLE teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject TEXT,
    phone TEXT
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_name TEXT,
    contact TEXT,
    class_id INTEGER NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes (id)
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (class_id) REFERENCES classes (id)
);

CREATE TABLE fee_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    amount_paid REAL NOT NULL,
    payment_date TEXT NOT NULL,
    payment_mode TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (id)
);

INSERT INTO classes (name, room_number) VALUES
('Grade 1', 'A-101'),
('Grade 2', 'A-102'),
('Grade 3', 'B-201');

INSERT INTO teachers (name, subject, phone) VALUES
('Anita Sharma', 'Mathematics', '9990001234'),
('Rahul Verma', 'Science', '9990005678');

INSERT INTO students (name, parent_name, contact, class_id) VALUES
('Aarav Singh', 'Suresh Singh', '9876543210', 1),
('Diya Kapoor', 'Nidhi Kapoor', '9876501234', 2);

INSERT INTO attendance (student_id, class_id, date, status) VALUES
(1, 1, '2026-02-20', 'Present'),
(2, 2, '2026-02-20', 'Absent');

INSERT INTO fee_payments (student_id, amount_paid, payment_date, payment_mode) VALUES
(1, 2500, '2026-02-10', 'UPI'),
(2, 2500, '2026-02-12', 'Cash');
