# Schedule App

This project is still under active development.
The database helper layer is mostly built, and the Flask app now has a working login flow, protected routes, a dashboard schedule view, lesson detail pages, and editable lesson/student notes.

## Project Idea

This project is a web-based scheduling app inspired by my fiance’s job. Her company manages teacher schedules through a Google Sheet. The sheet includes different teachers, time slots, students, and locations. Some teachers work at a center, while others travel to teach at a parent’s house.

I decided to use that situation as the idea for this project because it is a real scheduling problem that could be improved with a cleaner system.

The goal is to create a schedule app where teachers can view their schedules from a browser without needing to download anything or rely directly on a crowded spreadsheet.

## Why I Decided to Make This

I wanted to make a project that solves a real problem instead of building something random. My fiance’s job gave me a good example of a system that works, but could probably be easier to use.

Using a Google Sheet is simple, but it can become messy when there are a lot of teachers, students, schedule changes, and different teaching locations. Since some lessons happen at a center and others happen at parent homes, it would be useful to have a system that can organize schedules clearly and eventually check for conflicts.

This project gives me a chance to practice building a real client/server style application with Python, Flask, SQLite, HTML, CSS, and JavaScript while making something that is based on an actual workplace situation.

## Main Goal

Create a simple client/server scheduling system where:

- Teachers can log in
- Teachers can view their own schedules
- Teachers can open lesson detail pages
- Teachers can update lesson notes
- Teachers can update student notes
- Admins can eventually view and manage all schedules
- Schedule data is stored in a database
- Teachers only need a web browser to use it
- The app stores schedule data in a database instead of relying directly on a spreadsheet

## Current Progress

Current features and structure include:

- Flask app setup
- SQLite database schema setup
- Users table
- Teachers table
- Students table
- Lessons table
- Database connection helper
- User create, edit, deactivate, delete, and lookup functions
- Student create, edit, search, soft delete, and hard delete functions
- Teacher create, edit, search, and active-user filtering
- Lesson create, edit, delete, lookup, and update functions
- Lesson booking validation
- Schedule conflict checking
- Buffer time between lessons
- Conflict checks for lesson edits, time changes, and teacher reassignment
- Dummy seed data for testing
- Login page
- Basic session-based login flow
- Protected dashboard, schedule, lesson detail, and admin routes
- Dashboard schedule view filtered by logged-in teacher
- Today’s schedule display
- Live JavaScript clock on the dashboard
- Lesson detail page
- Lesson information display
- Student information display
- Editable lesson notes
- Editable student notes
- Basic HTML template structure
- Base template setup
- Initial CSS styling
- Argon2 password hashing dependency installed for future login work

## Current Login Note

The app currently uses plain text passwords for early development testing.

Example test accounts:

```text
admin / test123
teacher1 / test123
teacher2 / test123

## Project Structure

```text
schedule-app/
├── static/
│   └── style.css
├── templates/
│   ├── base_template.html
│   ├── admin.html
│   ├── dashboard.html
│   ├── login.html
│   └── schedule.html
├── .gitignore
├── app.py
├── database.py
├── helpers.py
├── README.md
└── requirements.txt