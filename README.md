# Schedule App

This project is still under active development.
The database helper layer is mostly completed, but it has not been fully activated or tested through the Flask app yet.

## Project Idea

This project is a web-based scheduling app inspired by my fiance’s job. Her company manages teacher schedules through a Google Sheet. The sheet includes different teachers, time slots, students, and locations. Some teachers work at a center, while others travel to teach at a parent’s house.

I decided to use that situation as the idea for this project because it is a real scheduling problem that could be improved with a cleaner system.

The goal is to create a schedule app where teachers can view their schedules from a browser without needing to download anything or rely directly on a crowded spreadsheet.

## Why I Decided to Make This

I wanted to make a project that solves a real problem instead of building something random. My fiance’s job gave me a good example of a system that works, but could probably be easier to use.

Using a Google Sheet is simple, but it can become messy when there are a lot of teachers, students, schedule changes, and different teaching locations. Since some lessons happen at a center and others happen at parent homes, it would be useful to have a system that can organize schedules clearly and eventually check for conflicts.

This project gives me a chance to practice building a real client/server style application with Python, Flask, SQLite, HTML, and CSS while making something that is based on an actual workplace situation.

## Main Goal

Create a simple client/server scheduling system where:

- Teachers can view their own schedules
- Admins can view and manage all schedules
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
- Student create, edit, search, soft delete, and hard delete functions
- Teacher create, edit, search, and active-user filtering
- Lesson create, edit, delete, lookup, and update functions
- Lesson booking validation
- Schedule conflict checking
- Buffer time between lessons
- Conflict checks for lesson edits, time changes, and teacher reassignment
- Basic HTML template structure
- Base template setup
- Initial dashboard page
- Initial CSS styling
- Argon2 password hashing dependency installed for future login work

## Google Sheet Note

This project is inspired by a real scheduling system that currently uses Google Sheets. However, the first version of this app will not directly import from the Google Sheet.

Because the schedules are manually created, the sheet format may not always be consistent. Building a reliable importer would require extra cleanup rules and could become a separate project by itself.

Instead, this app will focus on creating a cleaner scheduling system from the ground up using a database. Schedule entries can be added directly into the app, and Google Sheets importing may be considered later as an optional feature.

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- Argon2 password hashing through `argon2-cffi`

Possible later additions:

- JavaScript
- Hosted database
- Google Sheets importing if the format becomes consistent enough

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