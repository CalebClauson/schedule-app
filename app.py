from venv import create

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

# zed isnt understanding we HAVE Flask

app = Flask(__name__)
#secret key needs to be changed later | random secure value
app.secret_key = "dev-secret-key"

#temporary login scheme before hashing 
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("schedule_app.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, username, password_hash, email, role, is_active
            FROM users
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()
        conn.close()

        if user is None:
            error = "Invalid username or password."
        elif user[5] != 1:
            error = "This account is inactive."
        elif user[2] != password:
            error = "Invalid username or password."
        else:
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[4]

            return redirect(url_for("dashboard"))

    return render_template("login.html", error=error)

# Dashboard page
# This is the main page users see after they log in successfully.
# If no user_id exists in the session, the user is not logged in,
# so we send them back to the login page.
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# Lesson detail page
# This page will eventually show information for one specific lesson.
# Right now it just loads the lesson_detail.html template.
# Later, this route should probably use /lessons/<int:lesson_id>
# so clicking a lesson opens that lesson's specific details.
@app.route("/lesson_detail")
def lesson_detail():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("lesson_detail.html")


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
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Prevent teachers from opening admin-only pages
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)

