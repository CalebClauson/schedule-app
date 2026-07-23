import sqlite3
from datetime import date, timedelta
from helpers import add_minutes
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


# ============================
# Password Work 
# ============================
# Password Hashing 
password_hasher = PasswordHasher()

def hash_password(password):
    # Turns a plain password into a secure Argon2 password hash
    return password_hasher.hash(password)


def verify_password(stored_password_hash, password):
    # Checks if the typed password matches the stored password hash
    try:
        return password_hasher.verify(stored_password_hash, password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False

# ============================
# TABLE CREATION (ONE TIME USE)
# ============================

#created db already | do not recreate unless you want to lose data
def create_db():
    connection = sqlite3.connect("schedule_app.db")
    connection.execute("PRAGMA foreign_keys = ON")  # enable FK constraints
    cursor = connection.cursor()

    # user_id, username, password_hash, email, role, is_active, created_date
    # is_active, 1=active | 0=inactive
    create_users_table = """CREATE TABLE IF NOT EXISTS
    users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, email TEXT UNIQUE, role TEXT DEFAULT 'teacher', is_active INTEGER DEFAULT 1, must_change_password INTEGER DEFAULT 0, created_date TEXT DEFAULT CURRENT_TIMESTAMP)"""
    
    # user_id, first_name, last_name, phone, max_students, notes
    create_teachers_table = """CREATE TABLE IF NOT EXISTS
    teachers(user_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, phone TEXT, max_students INTEGER DEFAULT 10, notes TEXT, FOREIGN KEY(user_id) REFERENCES users(user_id))"""

    # student_id, first_name, last_name, parent_first_name, parent_last_name, parent_phone, parent_email, birth_date, is_active, notes
    create_students_table = """CREATE TABLE IF NOT EXISTS
    students(student_id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT, last_name TEXT, parent_first_name TEXT, parent_last_name TEXT, parent_phone TEXT, parent_email TEXT, birth_date TEXT NOT NULL, is_active INTEGER DEFAULT 1, notes TEXT)"""

    # lesson_id, teacher_id, student_id, lesson_date, start_time, end_time, status, location, notes, recurring_id, created_at, updated_at
    #recurring id for potential lessons that happen weekly; implementation unknown but there for the future
    create_lesson_table = """CREATE TABLE IF NOT EXISTS
    lessons(lesson_id INTEGER PRIMARY KEY AUTOINCREMENT, teacher_id INTEGER NOT NULL, student_id INTEGER NOT NULL, lesson_date TEXT NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL, status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled','completed','canceled')), location TEXT DEFAULT 'Teaching Center', notes TEXT, recurring_id INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT, FOREIGN KEY(teacher_id) REFERENCES teachers(user_id) ON DELETE CASCADE, FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE)"""

    cursor.execute(create_users_table)
    cursor.execute(create_teachers_table)
    cursor.execute(create_students_table)
    cursor.execute(create_lesson_table)
    connection.commit()
    connection.close()

# ============================
# CONNECTION - connection, cursor = create_connection()
# ============================

def create_connection():
    connection = sqlite3.connect("schedule_app.db")
    # personal note: FK constraints enabled to keep lesson relationships valid, especially if recurring lessons are added later
    connection.execute("PRAGMA foreign_keys = ON")  # enable FK constraints
    cursor = connection.cursor()
    return connection, cursor

# ============================
# USERS TABLE
# ============================

def create_user(username, password, email, role='teacher', is_active=1, must_change_password=0):
    connection, cursor = create_connection()
    password_hash = hash_password(password)

    try:
        cursor.execute("INSERT INTO users(username, password_hash, email, role, is_active, must_change_password) VALUES (?, ?, ?, ?, ?, ?)", (username, password_hash, email, role, is_active, must_change_password))
        user_id = cursor.lastrowid
        connection.commit()
        return user_id
    except sqlite3.IntegrityError as e:
        connection.rollback()
        print("Error creating user:", e)
        return None
    finally:
        connection.close()

#soft deletion
def deactivate_user(user_id):
    connection, cursor = create_connection()
    cursor.execute("""UPDATE users SET is_active = 0 WHERE user_id = ?""", (user_id,))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def delete_user(user_id):
    connection, cursor = create_connection()
    cursor.execute("""DELETE FROM users WHERE user_id = ?""", (user_id,))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def edit_user(user_id, username, password_hash, email, role, is_active):
    connection, cursor = create_connection()
    cursor.execute("""UPDATE users SET username=?, password_hash=?, email=?, role=?, is_active=? WHERE user_id = ?""", (username, password_hash, email, role, is_active, user_id))
    #tells how many rows were affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def get_user_by_id(user_id):
    connection, cursor = create_connection()
    cursor.execute("SELECT user_id, username, email, role, is_active, must_change_password FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    connection.close()
    return user

def get_user_by_username(username):
    connection, cursor = create_connection()
    cursor.execute("SELECT user_id, username, password_hash, email, role, is_active, must_change_password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    connection.close()
    return user

def return_all_users():
    connection, cursor = create_connection()
    cursor.execute("SELECT user_id, username, email, role, is_active, must_change_password FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"ID: {user[0]}")
        print(f"Username: {user[1]}")
        print(f"Email: {user[2]}")
        print(f"Role: {user[3]}")
        print(f"Active: {user[4]}")
        print(f"Must Change Password: {user[5]}")
        print("-" * 30)
    connection.close()

def update_user_role(user_id, role):
    if role not in ["teacher", "admin"]:
        return False

    connection, cursor = create_connection()

    cursor.execute("UPDATE users SET role = ? WHERE user_id = ?", (role, user_id))

    updated = cursor.rowcount
    connection.commit()
    connection.close()

    return updated > 0

def update_user_password(user_id, password, must_change_password=0):
    connection, cursor = create_connection()
    password_hash = hash_password(password)
    cursor.execute("UPDATE users SET password_hash = ?, must_change_password = ? WHERE user_id = ?", (password_hash, must_change_password, user_id))
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    return updated > 0

def update_must_change_password(user_id, must_change_password):
    connection, cursor = create_connection()
    cursor.execute("UPDATE users SET must_change_password = ? WHERE user_id = ?", (must_change_password, user_id))
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    return updated > 0

# ============================
# TEACHERS TABLE
# ============================

# create user first | create_user
# create teacher profile using the user_id returned from create_user
def create_teacher(user_id, first_name, last_name, phone=None, max_students=10, notes=None):
    connection, cursor = create_connection()
    try:
        cursor.execute("""INSERT INTO teachers(user_id, first_name, last_name, phone, max_students, notes) VALUES (?, ?, ?, ?, ?, ?)""", (user_id, first_name, last_name, phone, max_students, notes))
        connection.commit()
        return user_id
    except sqlite3.IntegrityError as e:
        connection.rollback()
        print("Error creating teacher:", e)
        return None
    finally:
        connection.close()

# delete_teacher removed | teacher deletion is handled through delete_user

def edit_teacher(user_id, first_name, last_name, phone, max_students, notes):
    connection, cursor = create_connection()
    cursor.execute("""UPDATE teachers SET first_name=?, last_name=?, phone=?, max_students=?, notes=? WHERE user_id = ? AND user_id IN (SELECT user_id FROM users WHERE is_active = 1)""", (first_name, last_name, phone, max_students, notes, user_id))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def get_all_teachers():
    connection, cursor = create_connection()
    cursor.execute("""SELECT teachers.user_id, teachers.first_name, teachers.last_name, teachers.phone, teachers.max_students, teachers.notes FROM teachers JOIN users ON teachers.user_id = users.user_id WHERE users.is_active = 1 ORDER BY  teachers.last_name ASC,
    teachers.first_name ASC,
    teachers.user_id ASC""")
    teachers = cursor.fetchall()
    connection.close()
    return teachers

def get_teacher_by_id(user_id):
    connection, cursor = create_connection()
    cursor.execute("""SELECT teachers.user_id, teachers.first_name, teachers.last_name, teachers.phone, teachers.max_students, teachers.notes, users.role FROM teachers JOIN users ON teachers.user_id = users.user_id WHERE teachers.user_id = ? AND users.is_active = 1""", (user_id,))
    teacher = cursor.fetchone()
    connection.close()

    return teacher

def get_teacher_by_name(first_name=None, last_name=None):
    connection, cursor = create_connection()
    if first_name and last_name:
        cursor.execute("""SELECT teachers.user_id, teachers.first_name, teachers.last_name, teachers.phone, teachers.max_students, teachers.notes FROM teachers JOIN users ON teachers.user_id = users.user_id WHERE teachers.first_name = ? AND teachers.last_name = ? AND users.is_active = 1""", (first_name, last_name))
    elif first_name:
        cursor.execute("""SELECT teachers.user_id, teachers.first_name, teachers.last_name, teachers.phone, teachers.max_students, teachers.notes FROM teachers JOIN users ON teachers.user_id = users.user_id WHERE teachers.first_name = ? AND users.is_active = 1""", (first_name,))
    elif last_name:
        cursor.execute("""SELECT teachers.user_id, teachers.first_name, teachers.last_name, teachers.phone, teachers.max_students, teachers.notes FROM teachers JOIN users ON teachers.user_id = users.user_id WHERE teachers.last_name = ? AND users.is_active = 1""", (last_name,))
    else:
        connection.close()
        return []

    teacher = cursor.fetchall()
    connection.close()
    return teacher

# ============================
# STUDENTS TABLE
# ============================

def create_student(first_name, last_name, parent_first_name, parent_last_name, parent_email, birth_date, parent_phone, notes=None):
    connection, cursor = create_connection()
    try:
        cursor.execute("""INSERT INTO students(first_name, last_name, parent_first_name, parent_last_name, parent_email, birth_date, parent_phone, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (first_name, last_name, parent_first_name, parent_last_name, parent_email, birth_date, parent_phone, notes))
        student_id = cursor.lastrowid
        connection.commit()
        return student_id
    except sqlite3.IntegrityError as e:
        connection.rollback()
        print("Error creating student:", e)
        return None
    finally:
        connection.close()

#soft deletion
def deactivate_student(student_id):
    connection, cursor = create_connection()
    cursor.execute("""UPDATE students SET is_active = 0 WHERE student_id = ?""", (student_id,))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def delete_student(student_id):
    connection, cursor = create_connection()
    cursor.execute("""DELETE FROM students WHERE student_id = ?""", (student_id,))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def edit_student(student_id, first_name, last_name, parent_first_name, parent_last_name, parent_email, birth_date, parent_phone, notes):
    connection, cursor = create_connection()
    cursor.execute("""UPDATE students SET first_name = ?, last_name = ?, parent_first_name = ?, parent_last_name = ?, parent_email = ?, birth_date = ?, parent_phone = ?, notes = ? WHERE student_id = ? AND is_active = 1""", (first_name, last_name, parent_first_name, parent_last_name, parent_email, birth_date, parent_phone, notes, student_id))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def edit_student_notes(student_id, notes):
    connection, cursor = create_connection()

    cursor.execute("UPDATE students SET notes = ? WHERE student_id = ? AND is_active = 1", (notes, student_id))

    updated = cursor.rowcount
    connection.commit()
    connection.close()

    return updated > 0

def get_all_students():
    connection, cursor = create_connection()
    cursor.execute("""SELECT student_id, first_name, last_name, parent_first_name, parent_last_name, parent_email, birth_date, parent_phone, notes FROM students WHERE is_active = 1""")
    students = cursor.fetchall()
    connection.close()
    return students

def get_student_by_id(student_id):
    connection, cursor = create_connection()
    cursor.execute("""SELECT student_id, first_name, last_name, parent_first_name, parent_last_name, parent_email, birth_date, parent_phone, notes FROM students WHERE student_id = ? AND is_active = 1""",(student_id,))
    student = cursor.fetchone()
    connection.close()
    return student

def get_student_by_name(first_name=None,last_name=None):
    connection, cursor = create_connection()
    if first_name and last_name:
        cursor.execute("""SELECT student_id, first_name, last_name, parent_first_name, parent_last_name, parent_email, birth_date, parent_phone, notes FROM students WHERE first_name=? AND last_name=? AND is_active = 1""", (first_name, last_name))
    elif first_name:
        cursor.execute("""SELECT student_id, first_name, last_name, parent_first_name, parent_last_name, parent_email, birth_date, parent_phone, notes FROM students WHERE first_name=? AND is_active = 1""", (first_name,))
    elif last_name:
        cursor.execute("""SELECT student_id, first_name, last_name, parent_first_name, parent_last_name, parent_email, birth_date, parent_phone, notes FROM students WHERE last_name=? AND is_active = 1 """, (last_name,))
    else:
        connection.close()
        return []
    student = cursor.fetchall()
    connection.close()
    return student

# ============================
# LESSONS TABLE
# ============================

def can_book_lesson(teacher_id, lesson_date, start_time, end_time, exclude_lesson_id=None):
    connection, cursor = create_connection()
    # buffer time in minutes between lessons
    buffer_minutes = 20
    # check if teacher exists and is active, then get max_students
    cursor.execute("""SELECT teachers.max_students FROM teachers JOIN users ON teachers.user_id = users.user_id WHERE teachers.user_id = ? AND users.is_active = 1""", (teacher_id,))
    result = cursor.fetchone()
    if result is None:
        connection.close()
        return False
    max_students = result[0]
    # check if teacher already has a lesson overlapping this time | including a buffer time
    buffered_start_time = add_minutes(start_time, -buffer_minutes)
    buffered_end_time = add_minutes(end_time, buffer_minutes)
    if exclude_lesson_id is None:
        cursor.execute("""SELECT COUNT(*) FROM lessons WHERE teacher_id = ? AND lesson_date = ? AND start_time < ? AND end_time > ?""", (teacher_id, lesson_date, buffered_end_time, buffered_start_time))
    else:
        cursor.execute("""SELECT COUNT(*) FROM lessons WHERE teacher_id = ? AND lesson_date = ? AND start_time < ? AND end_time > ? AND lesson_id != ?""", (teacher_id, lesson_date, buffered_end_time, buffered_start_time, exclude_lesson_id))
    overlapping_lessons = cursor.fetchone()[0]
    if overlapping_lessons > 0:
        connection.close()
        return False
    # check how many lessons teacher has that day
    cursor.execute("""SELECT COUNT(*) FROM lessons WHERE teacher_id = ? AND lesson_date = ?""", (teacher_id, lesson_date))
    lessons_that_day = cursor.fetchone()[0]
    connection.close()
    if lessons_that_day >= max_students:
        return False
    return True

def create_lesson(teacher_id, student_id, lesson_date, start_time, end_time, status="scheduled", location="Teaching Center", notes=None):
    if not can_book_lesson(teacher_id, lesson_date, start_time, end_time):
        print("Teacher is already booked or at max lessons for the day.")
        return None
    connection, cursor = create_connection()
    try:
        cursor.execute("""INSERT INTO lessons (teacher_id, student_id, lesson_date, start_time, end_time, status, location, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (teacher_id, student_id, lesson_date, start_time, end_time, status, location, notes))
        lesson_id = cursor.lastrowid
        connection.commit()
        return lesson_id
    except sqlite3.IntegrityError as e:
        connection.rollback()
        print("Error creating lesson:", e)
        return None
    finally:
        connection.close()

def delete_lesson(lesson_id):
    connection, cursor = create_connection()
    cursor.execute("""DELETE FROM lessons WHERE lesson_id = ?""", (lesson_id,))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0


def edit_lesson(lesson_id, teacher_id, student_id, lesson_date, start_time, end_time, status, location, notes):
    if not can_book_lesson(teacher_id, lesson_date, start_time, end_time, exclude_lesson_id=lesson_id):
        print("Teacher is already booked or at max lessons for the day.")
        return False

    connection, cursor = create_connection()

    cursor.execute(
        """UPDATE lessons SET teacher_id = ?, student_id = ?, lesson_date = ?, start_time = ?, end_time = ?, status = ?, location = ?, notes = ? WHERE lesson_id = ?""",(teacher_id, student_id, lesson_date, start_time, end_time, status,location, notes, lesson_id))

    updated = cursor.rowcount
    connection.commit()
    connection.close()
    return updated > 0

def get_lesson_by_id(lesson_id):
    connection, cursor = create_connection()
    cursor.execute("""SELECT lesson_id, teacher_id, student_id, lesson_date, start_time, end_time, status, location, notes FROM lessons WHERE lesson_id = ?""", (lesson_id,))
    lesson = cursor.fetchone()
    connection.close()
    return lesson

def get_lessons_by_teacher(teacher_id):
    connection, cursor = create_connection()
    cursor.execute("""SELECT lesson_id, teacher_id, student_id, lesson_date, start_time, end_time, status, location, notes FROM lessons WHERE teacher_id = ?""", (teacher_id,))
    lessons = cursor.fetchall()
    connection.close()
    return lessons

def get_lessons_by_student(student_id):
    connection, cursor = create_connection()
    cursor.execute("""SELECT lesson_id, teacher_id, student_id, lesson_date, start_time, end_time, status, location, notes FROM lessons WHERE student_id = ?""", (student_id,))
    lessons = cursor.fetchall()
    connection.close()
    return lessons

def update_lesson_status(lesson_id, status):
    connection, cursor = create_connection()
    cursor.execute("""UPDATE lessons SET status = ? WHERE lesson_id = ?""", (status, lesson_id))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def update_lesson_notes(lesson_id, notes):
    connection, cursor = create_connection()
    cursor.execute("""UPDATE lessons SET notes = ? WHERE lesson_id = ?""", (notes, lesson_id))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def update_lesson_time(lesson_id, start_time, end_time):
    connection, cursor = create_connection()
    cursor.execute("""SELECT teacher_id, lesson_date FROM lessons WHERE lesson_id = ?""", (lesson_id,))
    lesson = cursor.fetchone()
    if lesson is None:
        connection.close()
        return False
    teacher_id, lesson_date = lesson
    if not can_book_lesson(teacher_id, lesson_date, start_time, end_time, exclude_lesson_id=lesson_id):
        connection.close()
        print("Teacher is already booked or at max lessons for the day.")
        return False
    cursor.execute("""UPDATE lessons SET start_time = ?, end_time = ? WHERE lesson_id = ?""", (start_time, end_time, lesson_id))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def update_lesson_teacher(lesson_id, teacher_id):
    connection, cursor = create_connection()
    cursor.execute("""SELECT lesson_date, start_time, end_time FROM lessons WHERE lesson_id = ?""", (lesson_id,))
    lesson = cursor.fetchone()
    if lesson is None:
        connection.close()
        return False
    lesson_date, start_time, end_time = lesson
    if not can_book_lesson(teacher_id, lesson_date, start_time, end_time, exclude_lesson_id=lesson_id):
        connection.close()
        print("Teacher is already booked or at max lessons for the day.")
        return False
    cursor.execute("""UPDATE lessons SET teacher_id = ? WHERE lesson_id = ?""", (teacher_id, lesson_id))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def update_lesson_student(lesson_id, student_id):
    connection, cursor = create_connection()
    cursor.execute("""UPDATE lessons SET student_id = ? WHERE lesson_id = ?""", (student_id, lesson_id))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0
