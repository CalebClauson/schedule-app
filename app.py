from venv import create

from datetime import date
from flask import Flask, render_template, request, redirect, url_for, session
from database import create_connection, update_lesson_notes, edit_student_notes, verify_password
import sqlite3

# zed isnt understanding we HAVE Flask

app = Flask(__name__)
#secret key needs to be changed later | random secure value
app.secret_key = "dev-secret-key"

#login scheme with hashing
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("schedule_app.db")
        cursor = conn.cursor()

        cursor.execute("""SELECT user_id, username, password_hash, email, role, is_active FROM users WHERE username = ?""", (username,))

        user = cursor.fetchone()
        conn.close()

        if user is None:
            error = "Invalid username or password."
        elif user[5] != 1:
            error = "This account is inactive."
        elif not verify_password(user[2], password):
            error = "Invalid username or password."
        else:
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[4]
            if session["role"] == "admin":
                return redirect(url_for("admin"))
            
            return redirect(url_for("dashboard"))

    return render_template("login.html", error=error)

#helpers
def admin_required():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    return None

# Logout route
# Clears the current user session and sends them back to the login page.
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Dashboard page
# This is the main page users see after they log in successfully.
# If no user_id exists in the session, the user is not logged in,
# so we send them back to the login page.
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    today = date.today().isoformat()
    display_today = date.today().strftime("%B %d, %Y")

    connection, cursor = create_connection()

    cursor.execute("SELECT lessons.lesson_id, lessons.lesson_date, lessons.start_time, lessons.end_time, students.first_name, students.last_name, lessons.status, lessons.location, lessons.notes FROM lessons JOIN students ON lessons.student_id = students.student_id WHERE lessons.teacher_id = ? ORDER BY lessons.lesson_date, lessons.start_time", (session["user_id"],))
    lessons = cursor.fetchall()
    connection.close()

    return render_template("dashboard.html", username=session["username"], lessons=lessons, today=display_today)


# Lesson detail page
# This page will eventually show information for one specific lesson.
# Right now it just loads the lesson_detail.html template.
# Later, this route should probably use /lessons/<int:lesson_id>
# so clicking a lesson opens that lesson's specific details.
@app.route("/lessons/<int:lesson_id>")
def lesson_detail(lesson_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection, cursor = create_connection()

    cursor.execute("SELECT lessons.lesson_id, lessons.lesson_date, lessons.start_time, lessons.end_time, lessons.status, lessons.location, lessons.notes, students.student_id, students.first_name, students.last_name, students.parent_first_name, students.parent_last_name, students.parent_phone, students.parent_email, students.birth_date, students.notes FROM lessons JOIN students ON lessons.student_id = students.student_id WHERE lessons.lesson_id = ? AND lessons.teacher_id = ?", (lesson_id, session["user_id"]))

    lesson = cursor.fetchone()
    connection.close()

    if lesson is None:
        return "Lesson not found", 404

    return render_template("lesson_detail.html", lesson=lesson)

# POST ROUTE to UPDATE lesson notes
@app.route("/lessons/<int:lesson_id>/notes", methods=["POST"])
def update_notes(lesson_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    notes = request.form["notes"]

    updated = update_lesson_notes(lesson_id, notes)

    if not updated:
        return "Could not update lesson notes", 404

    return redirect(url_for("lesson_detail", lesson_id=lesson_id))

# POST ROUTE to UPDATE student notes
@app.route("/students/<int:student_id>/notes/<int:lesson_id>", methods=["POST"])
def update_student_notes_route(student_id, lesson_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    notes = request.form["student_notes"]

    updated = update_student_notes(student_id, notes)

    if not updated:
        return "Could not update student notes", 404

    return redirect(url_for("lesson_detail", lesson_id=lesson_id))

# Schedule page
# This page will show the teacher's lesson schedule.
# Later, this should pull lesson data from the database
# and pass it into schedule.html.
@app.route("/schedule")
def schedule():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("schedule.html")


# Admin page
# This page is for admin-related tools, such as managing users,
# teachers, students, or app settings.
@app.route("/admin")
def admin():
    blocked = admin_required()
    if blocked:
        return blocked

    connection, cursor = create_connection()

    cursor.execute("SELECT COUNT(*) FROM lessons")
    lesson_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teachers JOIN users ON teachers.user_id = users.user_id WHERE users.is_active = 1")
    teacher_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM students WHERE is_active = 1")
    student_count = cursor.fetchone()[0]

    cursor.execute("SELECT lessons.lesson_id, lessons.lesson_date, lessons.start_time, lessons.end_time, teachers.first_name, teachers.last_name, students.first_name, students.last_name, lessons.status, lessons.location FROM lessons JOIN teachers ON lessons.teacher_id = teachers.user_id JOIN students ON lessons.student_id = students.student_id ORDER BY lessons.lesson_date, lessons.start_time LIMIT 5")
    upcoming_lessons = cursor.fetchall()

    connection.close()

    today = date.today().isoformat()
    display_today = date.today().strftime("%B %d, %Y")

    return render_template(
        "admin.html", lesson_count=lesson_count, teacher_count=teacher_count, student_count=student_count, upcoming_lessons=upcoming_lessons, today = display_today)

@app.route("/admin/lessons")
def admin_lessons():
    blocked = admin_required()
    if blocked:
        return blocked

    connection, cursor = create_connection()

    cursor.execute("SELECT lessons.lesson_id, lessons.lesson_date, lessons.start_time, lessons.end_time, teachers.first_name, teachers.last_name, students.first_name, students.last_name, lessons.status, lessons.location, lessons.notes FROM lessons JOIN teachers ON lessons.teacher_id = teachers.user_id JOIN students ON lessons.student_id = students.student_id ORDER BY lessons.lesson_date, lessons.start_time")

    lessons = cursor.fetchall()
    connection.close()

    return render_template("admin_lessons.html", lessons=lessons)

@app.route("/admin/teachers")
def admin_teachers():
    blocked = admin_required()
    if blocked:
        return blocked

    connection, cursor = create_connection()

    cursor.execute("SELECT users.user_id, users.username, users.email, users.role, users.is_active, teachers.first_name, teachers.last_name, teachers.phone, teachers.max_students, teachers.notes FROM teachers JOIN users ON teachers.user_id = users.user_id ORDER BY users.is_active DESC, teachers.last_name")

    teachers = cursor.fetchall()
    connection.close()

    return render_template("admin_teachers.html", teachers=teachers)


@app.route("/admin/students")
def admin_students():
    blocked = admin_required()
    if blocked:
        return blocked

    connection, cursor = create_connection()

    cursor.execute("SELECT student_id, first_name, last_name, parent_first_name, parent_last_name, parent_phone, parent_email, birth_date, is_active, notes FROM students ORDER BY is_active DESC, last_name")

    students = cursor.fetchall()
    connection.close()

    return render_template("admin_students.html", students=students)

if __name__ == "__main__":
    app.run(debug=True)

