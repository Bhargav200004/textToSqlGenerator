import sqlite3
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

DB_NAME = "school.db"

def seed_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Enable foreign key enforcement
    cursor.execute("PRAGMA foreign_keys = ON;")

    # ---------------------------------------------------------
    # 1. Setup & Academic Structure
    # ---------------------------------------------------------
    academic_years = [
        ("2024-2025", "2024-06-01", "2025-04-30", 0),
        ("2025-2026", "2025-06-01", "2026-04-30", 0),
        ("2026-2027", "2026-06-01", "2027-04-30", 1),
    ]
    cursor.executemany(
        "INSERT INTO academic_years (name, start_date, end_date, is_active) VALUES (?, ?, ?, ?)",
        academic_years
    )

    roles = [
        ("Super Admin",), ("Principal",), ("Teacher",),
        ("Student",), ("Parent",), ("Accountant",), ("Librarian",)
    ]
    cursor.executemany("INSERT INTO roles (name) VALUES (?)", roles)

    # Classes: Grade 1 to Grade 10
    classes = [(f"Grade {i}",) for i in range(1, 11)]
    cursor.executemany("INSERT INTO classes (name) VALUES (?)", classes)

    # Sections: A, B, C for each Grade (30 sections)
    sections = []
    for class_id in range(1, 11):
        for sec_name in ["Section A", "Section B", "Section C"]:
            sections.append((class_id, sec_name))
    cursor.executemany("INSERT INTO sections (class_id, name) VALUES (?, ?)", sections)

    # Standard Subjects
    subjects = [
        ("Mathematics", "MATH101"),
        ("English", "ENG101"),
        ("Science", "SCI101"),
        ("Social Studies", "SOC101"),
        ("Computer Science", "CS101"),
        ("Physical Education", "PE101"),
        ("Art", "ART101")
    ]
    cursor.executemany("INSERT INTO subjects (name, code) VALUES (?, ?)", subjects)

    # ---------------------------------------------------------
    # 2. Users: Staff (100)
    # ---------------------------------------------------------
    # Role IDs: 1=Super Admin, 2=Principal, 3=Teacher, 4=Student, 5=Parent, 6=Accountant, 7=Librarian
    staff_users = []
    staff_records = []
    user_id_counter = 1

    for i in range(1, 101):
        email = f"staff_{i}_{fake.unique.user_name()}@school.edu"
        role_id = 2 if i == 1 else (6 if i == 2 else (7 if i == 3 else 3)) # 1 Principal, 1 Accountant, 1 Librarian, rest Teachers
        staff_users.append((role_id, email, fake.sha256(), 1))

        designation = "Principal" if role_id == 2 else ("Accountant" if role_id == 6 else ("Librarian" if role_id == 7 else "Teacher"))
        dept = "Administration" if role_id in (2, 6) else ("Library" if role_id == 7 else "Academics")

        staff_records.append((
            user_id_counter,
            f"EMP{1000 + i}",
            fake.first_name(),
            fake.last_name(),
            designation,
            dept,
            fake.date_between(start_date="-8y", end_date="-1y").isoformat(),
            round(random.uniform(35000, 85000), 2)
        ))
        user_id_counter += 1

    cursor.executemany("INSERT INTO users (role_id, email, password_hash, is_active) VALUES (?, ?, ?, ?)", staff_users)
    cursor.executemany("INSERT INTO staff (user_id, employee_id, first_name, last_name, designation, department, joining_date, salary) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", staff_records)

    # Map Subjects to Classes & Assign Teachers
    class_subjects = []
    teacher_ids = list(range(4, 101))  # IDs of staff members who are teachers
    for class_id in range(1, 11):
        for subject_id in range(1, len(subjects) + 1):
            class_subjects.append((class_id, subject_id, random.choice(teacher_ids)))
    cursor.executemany("INSERT INTO class_subjects (class_id, subject_id, teacher_id) VALUES (?, ?, ?)", class_subjects)

    # ---------------------------------------------------------
    # 3. Users: Parents (1,000)
    # ---------------------------------------------------------
    parent_users = []
    parent_records = []
    for i in range(1, 1001):
        email = f"parent_{i}_{fake.unique.user_name()}@example.com"
        parent_users.append((5, email, fake.sha256(), 1)) # role_id=5 for Parent
        parent_records.append((
            user_id_counter,
            fake.name_male(),
            fake.name_female(),
            fake.phone_number()[:15],
            fake.address().replace("\n", ", ")
        ))
        user_id_counter += 1

    cursor.executemany("INSERT INTO users (role_id, email, password_hash, is_active) VALUES (?, ?, ?, ?)", parent_users)
    cursor.executemany("INSERT INTO parents (user_id, father_name, mother_name, phone, address) VALUES (?, ?, ?, ?, ?)", parent_records)

    # ---------------------------------------------------------
    # 4. Users: Students (1,500)
    # Total Users Seeded = 100 + 1000 + 1500 = 2600 Users
    # ---------------------------------------------------------
    student_users = []
    student_records = []
    num_students = 1500

    for i in range(1, num_students + 1):
        email = f"student_{i}_{fake.unique.user_name()}@school.edu"
        student_users.append((4, email, fake.sha256(), 1)) # role_id=4 for Student

        gender = random.choice(["Male", "Female"])
        first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
        last_name = fake.last_name()
        section_id = random.randint(1, 30) # 30 sections total
        parent_id = random.randint(1, 1000)

        student_records.append((
            user_id_counter,
            f"ADM2026{i:04d}",
            f"R-{random.randint(1, 50):02d}",
            first_name,
            last_name,
            gender,
            fake.date_of_birth(minimum_age=6, maximum_age=16).isoformat(),
            section_id,
            parent_id
        ))
        user_id_counter += 1

    cursor.executemany("INSERT INTO users (role_id, email, password_hash, is_active) VALUES (?, ?, ?, ?)", student_users)
    cursor.executemany("INSERT INTO students (user_id, admission_no, roll_no, first_name, last_name, gender, dob, section_id, parent_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", student_records)

    # ---------------------------------------------------------
    # 5. Fee Structures & Payments
    # ---------------------------------------------------------
    fee_structures = []
    for class_id in range(1, 11):
        fee_structures.extend([
            (class_id, "Tuition", 15000.00),
            (class_id, "Library", 1200.00),
            (class_id, "Transport", 4500.00),
        ])
    cursor.executemany("INSERT INTO fee_structures (class_id, fee_type, amount) VALUES (?, ?, ?)", fee_structures)

    fee_payments = []
    for student_id in range(1, num_students + 1):
        status = random.choices(["Paid", "Pending", "Overdue"], weights=[75, 15, 10])[0]
        amount = 15000.00 if status == "Paid" else (7500.00 if status == "Pending" else 0.00)
        fee_payments.append((
            student_id,
            amount,
            fake.date_between(start_date="-3m", end_date="today").isoformat(),
            random.choice(["Cash", "Online", "Cheque"]),
            status
        ))
    cursor.executemany("INSERT INTO fee_payments (student_id, amount_paid, payment_date, payment_mode, status) VALUES (?, ?, ?, ?, ?)", fee_payments)

    # ---------------------------------------------------------
    # 6. Exams & Marks
    # ---------------------------------------------------------
    exams = [
        ("Mid-Term Examination 2026", 3, "2026-09-10", "2026-09-22"),
        ("Final Examination 2027", 3, "2027-03-15", "2027-03-28")
    ]
    cursor.executemany("INSERT INTO exams (name, academic_year_id, start_date, end_date) VALUES (?, ?, ?, ?)", exams)

    exam_marks = []
    for student_id in range(1, num_students + 1):
        for subject_id in range(1, 4): # Sample marks for first 3 core subjects
            score = round(random.uniform(40, 99), 1)
            grade = "A" if score >= 85 else ("B" if score >= 70 else ("C" if score >= 50 else "D"))
            exam_marks.append((1, student_id, subject_id, score, 100.00, grade))
    cursor.executemany("INSERT INTO exam_marks (exam_id, student_id, subject_id, marks_obtained, max_marks, grade) VALUES (?, ?, ?, ?, ?, ?)", exam_marks)

    # ---------------------------------------------------------
    # 7. Attendance (Past 5 School Days)
    # ---------------------------------------------------------
    attendance = []
    today = date.today()
    for day_offset in range(1, 6):
        att_date = (today - timedelta(days=day_offset)).isoformat()
        for student_id in range(1, num_students + 1):
            status = random.choices(["Present", "Absent", "Late", "Excused"], weights=[85, 7, 5, 3])[0]
            attendance.append((student_id, random.randint(1, 10), att_date, status))
    cursor.executemany("INSERT INTO attendance (student_id, class_id, date, status) VALUES (?, ?, ?, ?)", attendance)

    # Commit all batch transactions
    conn.commit()
    conn.close()
    print("Database populated successfully with 2,600 users and operational records.")

if __name__ == "__main__":
    seed_database()