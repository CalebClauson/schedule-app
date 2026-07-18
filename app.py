from venv import create

from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import create_connection, update_lesson_notes, verify_password, edit_lesson, get_lesson_by_id, get_all_teachers, get_all_students, edit_teacher, get_teacher_by_id, deactivate_user, edit_student, get_student_by_id, deactivate_student, update_user_role, create_user, create_teacher, create_student, create_lesson, get_user_by_username, update_lesson_status
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

def user_can_access_lesson(lesson_id):
    if session.get("role") == "admin":
        return True

    connection, cursor = create_connection()

    cursor.execute("SELECT lesson_id FROM lessons WHERE lesson_id = ? AND teacher_id = ?", (lesson_id, session["user_id"]))

    lesson = cursor.fetchone()
    connection.close()

    return lesson is not None

@app.template_filter("format_date")
def format_date(value):
    if not value:
        return ""

    date_object = datetime.strptime(value, "%Y-%m-%d")
    return date_object.strftime("%B %d, %Y").replace(" 0", " ")


@app.template_filter("format_time")
def format_time(value):
    if not value:
        return ""

    time_object = datetime.strptime(value, "%H:%M")
    return time_object.strftime("%I:%M %p").lstrip("0")

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
@app.route("/lessons/<int:lesson_id>", methods=["GET", "POST"])
def lesson_detail(lesson_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if not user_can_access_lesson(lesson_id):
        return "Not authorized", 403

    edit_mode = request.args.get("edit") == "1" and session.get("role") == "admin"

    if request.method == "POST":
        if session.get("role") != "admin":
            return "Not authorized", 403

        teacher_id = request.form["teacher_id"]
        student_id = request.form["student_id"]
        lesson_date = request.form["lesson_date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        status = request.form["status"]
        location = request.form["location"]
        notes = request.form["notes"]

        updated = edit_lesson(
            lesson_id,
            teacher_id,
            student_id,
            lesson_date,
            start_time,
            end_time,
            status,
            location,
            notes
        )

        if not updated:
            return "Could not update lesson. Teacher may be booked or at max lessons for the day.", 400

        return redirect(url_for("lesson_detail", lesson_id=lesson_id))

    connection, cursor = create_connection()

    cursor.execute("SELECT lessons.lesson_id, lessons.lesson_date, lessons.start_time, lessons.end_time, lessons.status, lessons.location, lessons.notes, students.student_id, students.first_name, students.last_name, students.parent_first_name, students.parent_last_name, students.parent_phone, students.parent_email, students.birth_date, students.notes FROM lessons JOIN students ON lessons.student_id = students.student_id WHERE lessons.lesson_id = ?", (lesson_id,))

    lesson = cursor.fetchone()
    connection.close()

    if lesson is None:
        return "Lesson not found", 404

    raw_lesson = None
    teachers = []
    students = []

    if session.get("role") == "admin":
        raw_lesson = get_lesson_by_id(lesson_id)
        teachers = get_all_teachers()
        students = get_all_students()

    return render_template(
        "lesson_detail.html",
        lesson=lesson,
        raw_lesson=raw_lesson,
        teachers=teachers,
        students=students,
        edit_mode=edit_mode
    )

#Update Lesson Status
@app.route("/lessons/<int:lesson_id>/status", methods=["POST"])
def update_lesson_status_route(lesson_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if not user_can_access_lesson(lesson_id):
        return "Not authorized", 403

    status = request.form["status"]

    if status not in ["scheduled", "completed", "canceled"]:
        return "Invalid status", 400

    updated = update_lesson_status(lesson_id, status)

    if not updated:
        flash("Could not update lesson status.")
        return redirect(url_for("lesson_detail", lesson_id=lesson_id))

    flash("Lesson status updated.")
    return redirect(url_for("lesson_detail", lesson_id=lesson_id))

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

@app.route("/admin/teachers/<int:user_id>", methods=["GET", "POST"])
def admin_teacher_detail(user_id):
    blocked = admin_required()
    if blocked:
        return blocked

    edit_mode = request.args.get("edit") == "1"

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone = request.form["phone"]
        max_students = request.form["max_students"]
        notes = request.form["notes"]
        role = request.form["role"]
        if user_id == session["user_id"] and role != "admin":
            flash("You cannot remove your own admin role.")
            return redirect(url_for("admin_teacher_detail", user_id=user_id, edit=1))
    
        updated_teacher = edit_teacher(user_id, first_name, last_name, phone, max_students, notes)
        updated_role = update_user_role(user_id, role)
    
        if not updated_teacher or not updated_role:
            return "Could not update teacher.", 400
    
        return redirect(url_for("admin_teacher_detail", user_id=user_id))

    teacher = get_teacher_by_id(user_id)

    if teacher is None:
        return "Teacher not found", 404

    return render_template(
        "admin_teacher_detail.html",
        teacher=teacher,
        edit_mode=edit_mode
    )


@app.route("/admin/teachers/<int:user_id>/deactivate", methods=["POST"])
def admin_deactivate_teacher(user_id):
    blocked = admin_required()
    if blocked:
        return blocked

    if user_id == session["user_id"]:
        return "You cannot deactivate your own admin account.", 400

    deactivated = deactivate_user(user_id)

    if not deactivated:
        return "Could not deactivate teacher.", 400

    return redirect(url_for("admin_teachers"))


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

@app.route("/admin/students/<int:student_id>", methods=["GET", "POST"])
def admin_student_detail(student_id):
    blocked = admin_required()
    if blocked:
        return blocked

    edit_mode = request.args.get("edit") == "1"

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        parent_first_name = request.form["parent_first_name"]
        parent_last_name = request.form["parent_last_name"]
        parent_email = request.form["parent_email"]
        birth_date = request.form["birth_date"]
        parent_phone = request.form["parent_phone"]
        notes = request.form["notes"]

        updated = edit_student(
            student_id,
            first_name,
            last_name,
            parent_first_name,
            parent_last_name,
            parent_email,
            birth_date,
            parent_phone,
            notes
        )

        if not updated:
            return "Could not update student.", 400

        return redirect(url_for("admin_student_detail", student_id=student_id))

    student = get_student_by_id(student_id)

    if student is None:
        return "Student not found", 404

    return render_template(
        "admin_student_detail.html",
        student=student,
        edit_mode=edit_mode
    )


@app.route("/admin/students/<int:student_id>/deactivate", methods=["POST"])
def admin_deactivate_student(student_id):
    blocked = admin_required()
    if blocked:
        return blocked

    deactivated = deactivate_student(student_id)

    if not deactivated:
        return "Could not deactivate student.", 400

    return redirect(url_for("admin_students"))

@app.route("/admin/students/new", methods=["GET", "POST"])
def admin_create_student():
    blocked = admin_required()
    if blocked:
        return blocked

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        parent_first_name = request.form["parent_first_name"]
        parent_last_name = request.form["parent_last_name"]
        parent_email = request.form["parent_email"]
        birth_date = request.form["birth_date"]
        parent_phone = request.form["parent_phone"]
        notes = request.form["notes"]

        created_student = create_student(
            first_name,
            last_name,
            parent_first_name,
            parent_last_name,
            parent_email,
            birth_date,
            parent_phone,
            notes
        )

        if not created_student:
            flash("Could not create student.")
            return redirect(url_for("admin_create_student"))

        flash("Student created successfully.")

        if type(created_student) is int:
            return redirect(url_for("admin_student_detail", student_id=created_student))

        return redirect(url_for("admin_students"))

    return render_template("admin_student_create.html")

@app.route("/admin/teachers/new", methods=["GET", "POST"])
def admin_create_teacher():
    blocked = admin_required()
    if blocked:
        return blocked

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        role = request.form["role"]

        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone = request.form["phone"]
        max_students = request.form["max_students"]
        notes = request.form["notes"]

        created_user = create_user(username, password, email, role)

        if type(created_user) is int:
            user_id = created_user
        else:
            user = get_user_by_username(username)
            user_id = user[0] if user else None

        if not user_id:
            flash("Could not create teacher user account.")
            return redirect(url_for("admin_create_teacher"))

        created_teacher = create_teacher(
            user_id,
            first_name,
            last_name,
            phone,
            max_students,
            notes
        )

        if not created_teacher:
            flash("User was created, but teacher profile could not be created.")
            return redirect(url_for("admin_teachers"))

        flash("Teacher created successfully.")
        return redirect(url_for("admin_teacher_detail", user_id=user_id))

    return render_template("admin_teacher_create.html")

@app.route("/admin/lessons/new", methods=["GET", "POST"])
def admin_create_lesson():
    blocked = admin_required()
    if blocked:
        return blocked

    teachers = get_all_teachers()
    students = get_all_students()

    if request.method == "POST":
        teacher_id = request.form["teacher_id"]
        student_id = request.form["student_id"]
        lesson_date = request.form["lesson_date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        status = request.form["status"]
        location = request.form["location"]
        notes = request.form["notes"]

        created_lesson = create_lesson(
            teacher_id,
            student_id,
            lesson_date,
            start_time,
            end_time,
            status,
            location,
            notes
        )

        if not created_lesson:
            flash("Could not create lesson. Teacher may already be booked or at max lessons for the day.")
            return redirect(url_for("admin_create_lesson"))

        flash("Lesson created successfully.")

        if type(created_lesson) is int:
            return redirect(url_for("lesson_detail", lesson_id=created_lesson))

        return redirect(url_for("admin_lessons"))

    return render_template(
        "admin_lesson_create.html",
        teachers=teachers,
        students=students
    )



if __name__ == "__main__":
    app.run(debug=True)

