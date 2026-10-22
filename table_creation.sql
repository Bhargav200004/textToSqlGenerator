-- 1. Base Setup & Role Tables
CREATE TABLE academic_years (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    is_active INTEGER DEFAULT 1 -- SQLite uses 0/1 for BOOLEAN
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT
);

-- 2. Dependencies on Base Tables
CREATE TABLE sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    name TEXT NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- 3. Dependencies on Users
CREATE TABLE parents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    father_name TEXT,
    mother_name TEXT,
    phone TEXT,
    address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    employee_id TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    designation TEXT,
    department TEXT,
    joining_date DATE,
    salary REAL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 4. Dependencies on Users, Parents, and Sections
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    admission_no TEXT UNIQUE NOT NULL,
    roll_no TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gender TEXT, -- ENUM handled via TEXT in SQLite
    dob DATE,
    section_id INTEGER,
    parent_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (section_id) REFERENCES sections(id),
    FOREIGN KEY (parent_id) REFERENCES parents(id)
);

-- 5. Mapping & Transactional Tables
CREATE TABLE class_subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    subject_id INTEGER,
    teacher_id INTEGER,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (teacher_id) REFERENCES staff(id)
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    class_id INTEGER,
    date DATE,
    status TEXT, -- 'Present', 'Absent', 'Late', 'Excused'
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    academic_year_id INTEGER,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (academic_year_id) REFERENCES academic_years(id)
);

CREATE TABLE exam_marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER,
    student_id INTEGER,
    subject_id INTEGER,
    marks_obtained REAL,
    max_marks REAL,
    grade TEXT,
    FOREIGN KEY (exam_id) REFERENCES exams(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE fee_structures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    fee_type TEXT,
    amount REAL,
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE TABLE fee_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    amount_paid REAL,
    payment_date DATE,
    payment_mode TEXT, -- 'Cash', 'Online', 'Cheque'
    status TEXT, -- 'Paid', 'Pending', 'Overdue'
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE timetables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER,
    subject_id INTEGER,
    teacher_id INTEGER,
    day_of_week TEXT,
    start_time TIME,
    end_time TIME,
    room_no TEXT,
    FOREIGN KEY (section_id) REFERENCES sections(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (teacher_id) REFERENCES staff(id)
);