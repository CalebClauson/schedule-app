import sqlite3

# ============================
# TABLE CREATION (ONE TIME USE)
# ============================

def create_db():
    connection = sqlite3.connect("schedule_app.db")
    connection.execute("PRAGMA foreign_keys = ON")  # enable FK constraints
    cursor = connection.cursor()

    # user_id, username, password_hash, email, role, is_active, created_date
    # is_active, 1=active | 0=inactive
    create_users_table = """CREATE TABLE IF NOT EXISTS
    users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, email TEXT UNIQUE, role TEXT DEFAULT 'teacher', is_active INTEGER DEFAULT 1, created_date TEXT DEFAULT CURRENT_TIMESTAMP)"""

    # user_id, first_name, last_name, phone, max_students, notes
    create_teachers_table = """CREATE TABLE IF NOT EXISTS
    teachers(user_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, phone TEXT, max_students INTEGER DEFAULT 4, notes TEXT, FOREIGN KEY(user_id) REFERENCES users(user_id))"""

    # student_id, first_name, last_name, phone, parent_first_name, parent_last_name, parent_phone, age, notes
    create_students_table = """CREATE TABLE IF NOT EXISTS
    students(student_id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT, last_name TEXT, parent_first_name TEXT, parent_last_name TEXT, parent_phone TEXT, age INTEGER, notes TEXT)"""

    # lesson_id, teacher_id, student_id, lesson_date, start_time, end_time, status, location, notes, recurring_id, created_at, updated_at
    #recurring id for potential lessons that happen weekly; implementation unknown but there for the future
    create_lesson_table = """CREATE TABLE IF NOT EXISTS
    lessons(lesson_id INTEGER PRIMARY KEY AUTOINCREMENT, teacher_id INTEGER NOT NULL, student_id INTEGER NOT NULL, lesson_date text NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL, status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled','completed','canceled')), location TEXT DEFAULT 'Teaching Center', notes TEXT, recurring_id INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT, FOREIGN KEY(teacher_id) REFERENCES teachers(user_id) ON DELETE CASCADE, FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE)"""

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

def create_user(username, password_hash, email, role='teacher', is_active=1):
    connection, cursor = create_connection()
    cursor.execute("""INSERT INTO users(username, password_hash, email, role, is_active) VALUES (?, ?, ?, ?, ?)""", (username, password_hash, email, role, is_active))
    user_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return user_id

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
    cursor.execute("""SELECT user_id, username, email, role, is_active FROM users WHERE user_id=?""", (user_id,))
    user = cursor.fetchone()
    connection.close()
    return user

def get_user_by_username(username):
    connection, cursor = create_connection()
    cursor.execute("""SELECT user_id, username, email, role, is_active FROM users WHERE username=?""", (username,))
    user = cursor.fetchone()
    connection.close()
    return user


# ============================
# TEACHERS TABLE
# ============================

# create user first | create_user
# create teacher profile using the user_id returned from create_user
def create_teacher(user_id, first_name, last_name, phone=None, max_students=4, notes=None):
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
    cursor.execute("""UPDATE teachers SET first_name=?, last_name=?, phone=?, max_students=?, notes=? WHERE user_id = ?""", (first_name, last_name, phone, max_students, notes, user_id))
    #tells if row was affected | if any at all for debug purpose/QOL
    updated = cursor.rowcount
    connection.commit()
    connection.close()
    #returns True or False | use later to tell if anything was changed
    return updated > 0

def get_teacher_by_id(user_id):
    connection, cursor = create_connection()
    cursor.execute("""SELECT user_id, first_name, last_name, phone, max_students, notes FROM teachers WHERE user_id=?""", (user_id,))
    teacher = cursor.fetchone()
    connection.close()
    return teacher

def get_teacher_by_name(first_name=None, last_name=None):
    connection, cursor = create_connection()
    if first_name and last_name:
        cursor.execute("""SELECT user_id, first_name, last_name, phone, max_students, notes FROM teachers WHERE first_name=? AND last_name=? """, (first_name, last_name))
    elif first_name:
        cursor.execute("""SELECT user_id, first_name, last_name, phone, max_students, notes FROM teachers WHERE first_name=?""", (first_name,))
    elif last_name:
        cursor.execute("""SELECT user_id, first_name, last_name, phone, max_students, notes FROM teachers WHERE last_name=? """, (last_name,))
    else:
        connection.close()
        return []

    teacher = cursor.fetchall()
    connection.close()
    return teacher

# ============================
# STUDENTS TABLE
# ============================

def create_student(first_name, last_name, parent_first_name, parent_last_name, parent_email, age, parent_phone, notes=None):
    return

def delete_student(student_id):
    return

def edit_student(first_name=None, last_name=None, parent_first_name=None, parent_last_name=None, parent_email=None, age=None, parent_phone=None, notes=None):
    return
    
def get_student_by_id(student_id):
    return

def get_student_by_name(first_name=None,last_name=None):
    return

def update_student_age(student_id, age):
    return


# ============================
# LESSONS TABLE
# ============================

def create_lesson(teacher_id, student_id, lesson_date, start_time, end_time, status, notes=None):
    return

def delete_lesson(lesson_id):
    return

def edit_lesson(teacher_id=None, student_id=None, lesson_date=None, start_time=None, end_time=None, status=None, notes=None):
    return

def get_lesson_by_id(lesson_id):
    return

def get_lesson_by_teacher(teacher_id):
    return

def get_lesson_by_student(student_id):
    return

def update_lesson_status(lesson_id, status):
    return

def update_lesson_notes(lesson_id, notes):
    return

def update_lesson_time(lesson_id, start_time, end_time):
    return

def update_lesson_teacher(lesson_id, teacher_id):
    return

def update_lesson_student(lesson_id, student_id):
    return