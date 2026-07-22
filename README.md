# Schedule App

This project is a completed MVP scheduling system with room for future improvements.

The app is a Flask and SQLite scheduling system built to manage teachers, students, lessons, notes, and admin-controlled accounts. It now has a working login system, password hashing, protected routes, teacher dashboards, admin management pages, create/edit flows, lesson status updates, and a forced password change system for new or reset teacher accounts.

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
- Teachers can mark lessons as completed
- Teachers can cancel scheduled lessons
- Admins can manage teachers, students, and lessons
- Admins can create teacher accounts instead of allowing public registration
- Admins can reset forgotten teacher passwords
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
- Large seed script for testing
- Login page
- Session-based login flow
- Protected dashboard, schedule, lesson detail, and admin routes
- Dashboard schedule view filtered by logged-in teacher
- Today’s schedule display
- Live JavaScript clock on the dashboard and admin page
- Lesson detail page
- Lesson information display
- Student information display
- Editable lesson notes
- Editable student notes
- Lesson completion and cancellation buttons
- Admin dashboard
- Admin lesson list
- Admin teacher list
- Admin student list
- Admin create student flow
- Admin create teacher flow
- Admin create lesson flow
- Admin edit teacher flow
- Admin edit student flow
- Admin edit lesson flow
- Admin deactivate teacher flow
- Admin deactivate student flow
- Admin password reset flow
- Forced password change for temporary passwords
- Basic HTML template structure
- Base template setup
- Shared CSS styling
- Argon2 password hashing

## Authentication and Security

The app now has functional password hashing using Argon2.

Accounts are not publicly registered. The admin creates teacher accounts manually. This is intentional because the app is meant for a controlled scheduling system, not a public sign-up website.

When an admin creates a teacher account, the teacher gets a temporary password. On first login, the teacher is forced to change that password before they can access the dashboard.

If a teacher forgets their password, the admin cannot view the old password. Instead, the admin resets the account to a new temporary password. The teacher then logs in and is forced to change it again.

Current security flow:

```text
Admin creates teacher account
Teacher logs in with temporary password
Teacher must change password
Teacher can then access dashboard

If password is forgotten:
Admin resets password
Teacher logs in with temporary password
Teacher must change password again
```

## Roles

The app currently has two main roles:

```text
admin
teacher
```

### Admin

Admins can:

- View the admin dashboard
- View all lessons
- View all teachers
- View all students
- Create teachers
- Create students
- Create lessons
- Edit teacher details
- Edit student details
- Edit lesson details
- Deactivate teachers
- Deactivate students
- Reset teacher passwords
- Access any lesson detail page

### Teacher

Teachers can:

- Log in
- Change their temporary password
- View their own dashboard
- View their assigned lessons
- Open their own lesson detail pages
- Update lesson notes
- Update student notes connected to their lessons
- Mark scheduled lessons as completed
- Cancel scheduled lessons

Teachers cannot access lessons that do not belong to them.

## Lesson Scheduling Logic

The app has scheduling checks built into the database helper functions.

Current lesson scheduling logic includes:

- Preventing overlapping lessons for the same teacher
- Adding buffer time between lessons
- Checking a teacher’s max students or max lessons for the day
- Preventing bad edits that would create scheduling conflicts
- Supporting lesson statuses

Lesson statuses:

```text
scheduled
completed
canceled
```

## Project Structure

```text
schedule-app/
├── static/
│   └── style.css
├── templates/
│   ├── admin.html
│   ├── admin_lesson_create.html
│   ├── admin_lessons.html
│   ├── admin_student_create.html
│   ├── admin_student_detail.html
│   ├── admin_students.html
│   ├── admin_teacher_create.html
│   ├── admin_teacher_detail.html
│   ├── admin_teachers.html
│   ├── base_template.html
│   ├── change_password.html
│   ├── dashboard.html
│   ├── lesson_detail.html
│   ├── login.html
│   ├── schedule.html
│   └── weekly_schedule.html
├── .gitignore
├── app.py
├── database.py
├── helpers.py
├── seed_large_test_data.py
├── README.md
└── requirements.txt
```

## Database Tables

### users

Stores account and login information.

Important fields:

- user_id
- username
- password_hash
- email
- role
- is_active
- must_change_password
- created_date

### teachers

Stores teacher profile information.

Important fields:

- user_id
- first_name
- last_name
- phone
- max_students
- notes

### students

Stores student and parent contact information.

Important fields:

- student_id
- first_name
- last_name
- parent_first_name
- parent_last_name
- parent_phone
- parent_email
- birth_date
- is_active
- notes

### lessons

Stores lesson schedule information.

Important fields:

- lesson_id
- teacher_id
- student_id
- lesson_date
- start_time
- end_time
- status
- location
- notes
- recurring_id
- created_at
- updated_at

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create and seed the database:

```bash
python -c python -c "from database import create_db; create_db()"
python seed_large_test_data.py
```

Run the Flask app:

```bash
python app.py
```

Open the app in the browser:

```text
http://127.0.0.1:5000/login
```

## Test Accounts

After seeding dummy data:

```text
Admin:
username: admin
password: test123

Teacher:
username: teacher1
password: test123

Teacher:
username: teacher2
password: test123
```

The seeded teacher accounts have `must_change_password = 1`, so they should be forced to change their temporary password after login.

The seeded admin account has `must_change_password = 0`, so it can log in normally.

## Test Data

This project includes a seed script for adding larger development data.

To run the test data script:

```bash
python seed_large_test_data.py
```

The seed script adds sample teachers, students, and lessons for testing the dashboard, admin pages, weekly schedule, and lesson navigation.

## Current Workflow

Admin flow:

```text
Login
Open admin dashboard
Create teachers, students, and lessons
Edit records as needed
Reset teacher passwords if needed
Deactivate records instead of deleting history
```

Teacher flow:

```text
Login
Change temporary password if required
View assigned lessons
Open lesson details
Update lesson notes
Update student notes
Mark lessons complete or canceled
```

## Current Limitations

This is still a development version. Some things are intentionally simple right now.

Current limitations:

- No production deployment setup yet
- Secret key is still hardcoded for development
- No email notifications yet
- No recurring lesson system yet
- No parent account system
- No search or filter tools yet
- No drag-and-drop calendar interface yet
- No advanced password strength rules yet
- No full audit log yet

## Future Improvements

Things I may add later:

- Recurring lesson support
- Teacher availability settings
- Better flash message categories
- Search and filter tools for lessons, teachers, and students
- Student lesson history pages
- Parent contact tools
- Email reminders
- Calendar-style schedule view
- Password strength requirements
- Environment variable for Flask secret key
- Deployment instructions
- More polished admin reports

## Notes

Right now, the goal is to get the main version working first before adding bigger features like reminders, filters, reports, and a real calendar view.

The app has moved past just being a database practice project and now works more like an actual small scheduling system.