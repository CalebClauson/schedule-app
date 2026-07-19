import sqlite3
from datetime import date, timedelta
from database import hash_password


DB_NAME = "schedule_app.db"


TEACHERS = [
    ("seed_teacher_01", "test123", "seed_teacher_01@example.com", "teacher", "Avery", "Stone", "555-200-0001", 6, "Seed teacher for testing."),
    ("seed_teacher_02", "test123", "seed_teacher_02@example.com", "teacher", "Morgan", "Reed", "555-200-0002", 6, "Seed teacher for testing."),
    ("seed_teacher_03", "test123", "seed_teacher_03@example.com", "teacher", "Riley", "Brooks", "555-200-0003", 6, "Seed teacher for testing."),
    ("seed_teacher_04", "test123", "seed_teacher_04@example.com", "teacher", "Jordan", "Hayes", "555-200-0004", 6, "Seed teacher for testing."),
    ("seed_teacher_05", "test123", "seed_teacher_05@example.com", "teacher", "Taylor", "Lane", "555-200-0005", 6, "Seed teacher for testing."),
]


STUDENTS = [
    ("Liam", "Johnson", "Mark", "Johnson", "555-300-0001", "parent01@example.com", "2014-02-11", "[SEED] Multiplication and reading support."),
    ("Emma", "Williams", "Sarah", "Williams", "555-300-0002", "parent02@example.com", "2015-06-21", "[SEED] Needs help staying focused."),
    ("Noah", "Brown", "David", "Brown", "555-300-0003", "parent03@example.com", "2013-09-05", "[SEED] Strong math student."),
    ("Olivia", "Davis", "Emily", "Davis", "555-300-0004", "parent04@example.com", "2016-01-14", "[SEED] Reading comprehension practice."),
    ("Ethan", "Miller", "Jason", "Miller", "555-300-0005", "parent05@example.com", "2012-11-30", "[SEED] Preparing for tests."),
    ("Sophia", "Wilson", "Rachel", "Wilson", "555-300-0006", "parent06@example.com", "2015-03-19", "[SEED] Writing and grammar."),
    ("Mason", "Moore", "Kevin", "Moore", "555-300-0007", "parent07@example.com", "2014-07-07", "[SEED] Fractions and decimals."),
    ("Isabella", "Taylor", "Laura", "Taylor", "555-300-0008", "parent08@example.com", "2016-04-23", "[SEED] Beginner reading support."),
    ("Lucas", "Anderson", "Brian", "Anderson", "555-300-0009", "parent09@example.com", "2013-12-02", "[SEED] Homework support."),
    ("Mia", "Thomas", "Ashley", "Thomas", "555-300-0010", "parent10@example.com", "2015-08-16", "[SEED] Vocabulary practice."),
    ("Logan", "Jackson", "Chris", "Jackson", "555-300-0011", "parent11@example.com", "2012-10-12", "[SEED] Algebra readiness."),
    ("Amelia", "White", "Nicole", "White", "555-300-0012", "parent12@example.com", "2016-05-03", "[SEED] Spelling support."),
    ("James", "Harris", "Mike", "Harris", "555-300-0013", "parent13@example.com", "2014-09-28", "[SEED] Math review."),
    ("Charlotte", "Martin", "Anna", "Martin", "555-300-0014", "parent14@example.com", "2013-01-25", "[SEED] Reading fluency."),
    ("Benjamin", "Thompson", "Eric", "Thompson", "555-300-0015", "parent15@example.com", "2015-12-09", "[SEED] Needs confidence building."),
    ("Harper", "Garcia", "Maria", "Garcia", "555-300-0016", "parent16@example.com", "2016-07-18", "[SEED] Early math skills."),
    ("Henry", "Martinez", "Luis", "Martinez", "555-300-0017", "parent17@example.com", "2014-11-04", "[SEED] Word problems."),
    ("Evelyn", "Robinson", "Grace", "Robinson", "555-300-0018", "parent18@example.com", "2013-06-13", "[SEED] Essay structure."),
    ("Alexander", "Clark", "Ryan", "Clark", "555-300-0019", "parent19@example.com", "2012-03-17", "[SEED] Pre-algebra."),
    ("Abigail", "Rodriguez", "Sofia", "Rodriguez", "555-300-0020", "parent20@example.com", "2015-10-22", "[SEED] Reading practice."),
]


LESSON_NOTES = [
    "Work on multiplication review and focus exercises.",
    "Use visual flashcards and sentence matching.",
    "Practice reading fluency and short answer responses.",
    "Review fractions, decimals, and word problems.",
    "Homework support and confidence building.",
    "Spelling, vocabulary, and grammar review.",
]


def connect():
    connection = sqlite3.connect(DB_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def reset_seed_data(cursor):
    cursor.execute("DELETE FROM lessons WHERE notes LIKE '[SEED]%'")
    cursor.execute("DELETE FROM students WHERE notes LIKE '[SEED]%'")
    cursor.execute("DELETE FROM teachers WHERE notes LIKE '[SEED]%'")
    cursor.execute("DELETE FROM users WHERE username LIKE 'seed_teacher_%'")


def create_seed_teachers(cursor):
    teacher_ids = []

    for username, password, email, role, first_name, last_name, phone, max_students, notes in TEACHERS:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, email, role, is_active)
            VALUES (?, ?, ?, ?, 1)
            """,
            (username, hash_password(password), email, role)
        )

        user_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO teachers (user_id, first_name, last_name, phone, max_students, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, first_name, last_name, phone, max_students, "[SEED] " + notes)
        )

        teacher_ids.append(user_id)

    return teacher_ids


def create_seed_students(cursor):
    student_ids = []

    for student in STUDENTS:
        cursor.execute(
            """
            INSERT INTO students (
                first_name,
                last_name,
                parent_first_name,
                parent_last_name,
                parent_phone,
                parent_email,
                birth_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            student
        )

        student_ids.append(cursor.lastrowid)

    return student_ids


def create_seed_lessons(cursor, teacher_ids, student_ids):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())

    lesson_times = [
        ("09:00", "10:00"),
        ("10:30", "11:30"),
        ("13:00", "14:00"),
        ("15:00", "16:00"),
        ("17:00", "18:00"),
    ]

    statuses = ["scheduled", "scheduled", "scheduled", "completed", "canceled"]
    locations = ["Teaching Center", "Teaching Center", "Online"]

    lesson_count = 0

    for week in range(4):
        for weekday in range(5):
            lesson_date = start_of_week + timedelta(weeks=week, days=weekday)

            for slot_index, (start_time, end_time) in enumerate(lesson_times):
                teacher_id = teacher_ids[(weekday + slot_index + week) % len(teacher_ids)]
                student_id = student_ids[(lesson_count + slot_index) % len(student_ids)]
                status = statuses[(lesson_count + slot_index) % len(statuses)]
                location = locations[(lesson_count + weekday) % len(locations)]
                note = LESSON_NOTES[lesson_count % len(LESSON_NOTES)]

                cursor.execute(
                    """
                    INSERT INTO lessons (
                        teacher_id,
                        student_id,
                        lesson_date,
                        start_time,
                        end_time,
                        status,
                        location,
                        notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        teacher_id,
                        student_id,
                        lesson_date.strftime("%Y-%m-%d"),
                        start_time,
                        end_time,
                        status,
                        location,
                        "[SEED] " + note
                    )
                )

                lesson_count += 1

    return lesson_count


def main():
    connection = connect()
    cursor = connection.cursor()

    reset_seed_data(cursor)

    teacher_ids = create_seed_teachers(cursor)
    student_ids = create_seed_students(cursor)
    lesson_count = create_seed_lessons(cursor, teacher_ids, student_ids)

    connection.commit()
    connection.close()

    print("Seed data inserted successfully.")
    print(f"Teachers created: {len(teacher_ids)}")
    print(f"Students created: {len(student_ids)}")
    print(f"Lessons created: {lesson_count}")
    print("Seed teacher password: test123")


if __name__ == "__main__":
    main()