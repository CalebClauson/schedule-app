"""
Automated tests for schedule-app.

These tests use a brand-new temporary SQLite database for every test.
They do NOT touch the real schedule_app.db in the project folder.

Run from the schedule-app root folder:

    python -m pytest -v

Optional coverage report:

    python -m pytest --cov=database --cov=helpers --cov-report=term-missing
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

# Allows pytest to import database.py and helpers.py from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import database
from helpers import add_minutes


# ---------------------------------------------------------------------------
# Test setup
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def fresh_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Run every test inside its own temporary directory.

    database.py uses the relative filename "schedule_app.db", so changing the
    working directory makes the application create a disposable test database.
    """
    monkeypatch.chdir(tmp_path)
    database.create_db()

    yield

    # SQLite connections should already be closed by the application methods.
    # The temporary directory and database are removed automatically by pytest.


@pytest.fixture
def teacher() -> int:
    """Create and return one active teacher account."""
    user_id = database.create_user(
        username="teacher1",
        password="TestPassword123!",
        email="teacher1@example.com",
        role="teacher",
    )
    assert user_id is not None

    teacher_id = database.create_teacher(
        user_id=user_id,
        first_name="Alex",
        last_name="Morgan",
        phone="765-555-1000",
        max_students=4,
        notes="Test teacher",
    )
    assert teacher_id == user_id
    return teacher_id


@pytest.fixture
def second_teacher() -> int:
    """Create and return a second active teacher account."""
    user_id = database.create_user(
        username="teacher2",
        password="TestPassword456!",
        email="teacher2@example.com",
        role="teacher",
    )
    assert user_id is not None

    teacher_id = database.create_teacher(
        user_id=user_id,
        first_name="Jordan",
        last_name="Lee",
        phone="765-555-2000",
        max_students=4,
        notes="Second test teacher",
    )
    assert teacher_id == user_id
    return teacher_id


@pytest.fixture
def student() -> int:
    """Create and return one active student."""
    student_id = database.create_student(
        first_name="Sam",
        last_name="Taylor",
        parent_first_name="Jamie",
        parent_last_name="Taylor",
        parent_email="jamie.taylor@example.com",
        birth_date="2015-05-10",
        parent_phone="765-555-3000",
        notes="Test student",
    )
    assert student_id is not None
    return student_id


@pytest.fixture
def second_student() -> int:
    """Create and return a second active student."""
    student_id = database.create_student(
        first_name="Riley",
        last_name="Brown",
        parent_first_name="Casey",
        parent_last_name="Brown",
        parent_email="casey.brown@example.com",
        birth_date="2014-08-21",
        parent_phone="765-555-4000",
        notes="Second test student",
    )
    assert student_id is not None
    return student_id


@pytest.fixture
def lesson(teacher: int, student: int) -> int:
    """Create and return one scheduled lesson."""
    lesson_id = database.create_lesson(
        teacher_id=teacher,
        student_id=student,
        lesson_date="2030-07-18",
        start_time="10:00",
        end_time="11:00",
        status="scheduled",
        location="Teaching Center",
        notes="Initial lesson note",
    )
    assert lesson_id is not None
    return lesson_id


# ---------------------------------------------------------------------------
# Password tests
# ---------------------------------------------------------------------------

def test_hash_password_does_not_store_plain_text():
    password = "SecurePassword123!"
    password_hash = database.hash_password(password)

    assert password_hash != password
    assert password_hash.startswith("$argon2")


def test_verify_password_accepts_correct_password():
    password = "SecurePassword123!"
    password_hash = database.hash_password(password)

    assert database.verify_password(password_hash, password) is True


def test_verify_password_rejects_incorrect_password():
    password_hash = database.hash_password("CorrectPassword123!")

    assert database.verify_password(password_hash, "WrongPassword") is False


def test_verify_password_rejects_invalid_hash():
    assert database.verify_password("not-a-real-hash", "password") is False


# ---------------------------------------------------------------------------
# User tests
# ---------------------------------------------------------------------------

def test_create_and_get_user():
    user_id = database.create_user(
        "caleb",
        "Password123!",
        "caleb@example.com",
        role="admin",
    )

    user = database.get_user_by_id(user_id)

    assert user is not None
    assert user[0] == user_id
    assert user[1] == "caleb"
    assert user[2] == "caleb@example.com"
    assert user[3] == "admin"
    assert user[4] == 1
    assert user[5] == 0


def test_get_user_by_username_includes_password_hash():
    user_id = database.create_user(
        "lookup_user",
        "Password123!",
        "lookup@example.com",
    )

    user = database.get_user_by_username("lookup_user")

    assert user is not None
    assert user[0] == user_id
    assert user[1] == "lookup_user"
    assert database.verify_password(user[2], "Password123!") is True


def test_duplicate_username_is_rejected():
    first_id = database.create_user(
        "duplicate",
        "Password123!",
        "first@example.com",
    )
    second_id = database.create_user(
        "duplicate",
        "DifferentPassword123!",
        "second@example.com",
    )

    assert first_id is not None
    assert second_id is None


def test_duplicate_email_is_rejected():
    first_id = database.create_user(
        "first_user",
        "Password123!",
        "same@example.com",
    )
    second_id = database.create_user(
        "second_user",
        "Password123!",
        "same@example.com",
    )

    assert first_id is not None
    assert second_id is None


def test_deactivate_user():
    user_id = database.create_user(
        "deactivate_me",
        "Password123!",
        "deactivate@example.com",
    )

    assert database.deactivate_user(user_id) is True
    assert database.get_user_by_id(user_id)[4] == 0


def test_deactivate_missing_user_returns_false():
    assert database.deactivate_user(999999) is False


def test_update_user_role_accepts_valid_role():
    user_id = database.create_user(
        "role_user",
        "Password123!",
        "role@example.com",
    )

    assert database.update_user_role(user_id, "admin") is True
    assert database.get_user_by_id(user_id)[3] == "admin"


def test_update_user_role_rejects_invalid_role():
    user_id = database.create_user(
        "invalid_role_user",
        "Password123!",
        "invalid-role@example.com",
    )

    assert database.update_user_role(user_id, "superhero") is False
    assert database.get_user_by_id(user_id)[3] == "teacher"


def test_update_user_password():
    user_id = database.create_user(
        "password_user",
        "OldPassword123!",
        "password@example.com",
        must_change_password=1,
    )

    assert database.update_user_password(
        user_id,
        "NewPassword123!",
        must_change_password=0,
    ) is True

    user = database.get_user_by_username("password_user")
    assert database.verify_password(user[2], "OldPassword123!") is False
    assert database.verify_password(user[2], "NewPassword123!") is True
    assert user[6] == 0


def test_update_must_change_password():
    user_id = database.create_user(
        "temp_password_user",
        "Password123!",
        "temp@example.com",
    )

    assert database.update_must_change_password(user_id, 1) is True
    assert database.get_user_by_id(user_id)[5] == 1


# ---------------------------------------------------------------------------
# Teacher tests
# ---------------------------------------------------------------------------

def test_create_and_get_teacher(teacher: int):
    result = database.get_teacher_by_id(teacher)

    assert result is not None
    assert result[0] == teacher
    assert result[1] == "Alex"
    assert result[2] == "Morgan"
    assert result[4] == 4
    assert result[6] == "teacher"


def test_create_teacher_requires_existing_user():
    teacher_id = database.create_teacher(
        user_id=999999,
        first_name="Missing",
        last_name="User",
    )

    assert teacher_id is None


def test_get_teacher_by_name(teacher: int):
    matches = database.get_teacher_by_name(
        first_name="Alex",
        last_name="Morgan",
    )

    assert len(matches) == 1
    assert matches[0][0] == teacher


def test_edit_teacher(teacher: int):
    updated = database.edit_teacher(
        user_id=teacher,
        first_name="Alexander",
        last_name="Morgan",
        phone="765-555-9999",
        max_students=6,
        notes="Updated teacher",
    )

    result = database.get_teacher_by_id(teacher)

    assert updated is True
    assert result[1] == "Alexander"
    assert result[3] == "765-555-9999"
    assert result[4] == 6
    assert result[5] == "Updated teacher"


def test_inactive_teacher_is_hidden(teacher: int):
    assert database.deactivate_user(teacher) is True

    assert database.get_teacher_by_id(teacher) is None
    assert database.get_all_teachers() == []


# ---------------------------------------------------------------------------
# Student tests
# ---------------------------------------------------------------------------

def test_create_and_get_student(student: int):
    result = database.get_student_by_id(student)

    assert result is not None
    assert result[0] == student
    assert result[1] == "Sam"
    assert result[2] == "Taylor"
    assert result[5] == "jamie.taylor@example.com"
    assert result[6] == "2015-05-10"


def test_get_student_by_name(student: int):
    matches = database.get_student_by_name(
        first_name="Sam",
        last_name="Taylor",
    )

    assert len(matches) == 1
    assert matches[0][0] == student


def test_edit_student(student: int):
    updated = database.edit_student(
        student_id=student,
        first_name="Samuel",
        last_name="Taylor",
        parent_first_name="Jamie",
        parent_last_name="Taylor",
        parent_email="updated.parent@example.com",
        birth_date="2015-05-10",
        parent_phone="765-555-8888",
        notes="Updated student",
    )

    result = database.get_student_by_id(student)

    assert updated is True
    assert result[1] == "Samuel"
    assert result[5] == "updated.parent@example.com"
    assert result[7] == "765-555-8888"
    assert result[8] == "Updated student"


def test_edit_student_notes(student: int):
    assert database.edit_student_notes(student, "New student note") is True
    assert database.get_student_by_id(student)[8] == "New student note"


def test_deactivate_student_hides_student(student: int):
    assert database.deactivate_student(student) is True
    assert database.get_student_by_id(student) is None
    assert database.get_all_students() == []


def test_edit_inactive_student_is_rejected(student: int):
    database.deactivate_student(student)

    result = database.edit_student(
        student,
        "Hidden",
        "Student",
        "Parent",
        "Student",
        "parent@example.com",
        "2015-05-10",
        "765-555-0000",
        "Should not update",
    )

    assert result is False


# ---------------------------------------------------------------------------
# Lesson creation and scheduling-rule tests
# ---------------------------------------------------------------------------

def test_create_and_get_lesson(lesson: int):
    result = database.get_lesson_by_id(lesson)

    assert result is not None
    assert result[0] == lesson
    assert result[3] == "2030-07-18"
    assert result[4] == "10:00"
    assert result[5] == "11:00"
    assert result[6] == "scheduled"
    assert result[7] == "Teaching Center"


def test_overlapping_lesson_is_rejected(
    lesson: int,
    teacher: int,
    second_student: int,
):
    overlapping_id = database.create_lesson(
        teacher_id=teacher,
        student_id=second_student,
        lesson_date="2030-07-18",
        start_time="10:30",
        end_time="11:30",
    )

    assert overlapping_id is None


@pytest.mark.parametrize(
    ("start_time", "end_time"),
    [
        ("09:41", "09:55"),  # Enters the 20-minute buffer before 10:00.
        ("11:05", "11:30"),  # Enters the 20-minute buffer after 11:00.
        ("09:50", "10:00"),  # Touches the existing lesson start.
        ("11:00", "11:10"),  # Touches the existing lesson end.
    ],
)
def test_buffer_conflicts_are_rejected(
    lesson: int,
    teacher: int,
    second_student: int,
    start_time: str,
    end_time: str,
):
    result = database.create_lesson(
        teacher_id=teacher,
        student_id=second_student,
        lesson_date="2030-07-18",
        start_time=start_time,
        end_time=end_time,
    )

    assert result is None


def test_lesson_outside_buffer_is_allowed(
    lesson: int,
    teacher: int,
    second_student: int,
):
    result = database.create_lesson(
        teacher_id=teacher,
        student_id=second_student,
        lesson_date="2030-07-18",
        start_time="11:20",
        end_time="12:00",
    )

    assert result is not None


def test_same_time_is_allowed_for_different_teachers(
    lesson: int,
    second_teacher: int,
    second_student: int,
):
    result = database.create_lesson(
        teacher_id=second_teacher,
        student_id=second_student,
        lesson_date="2030-07-18",
        start_time="10:00",
        end_time="11:00",
    )

    assert result is not None


def test_inactive_teacher_cannot_receive_lesson(
    teacher: int,
    student: int,
):
    database.deactivate_user(teacher)

    result = database.create_lesson(
        teacher_id=teacher,
        student_id=student,
        lesson_date="2030-07-18",
        start_time="10:00",
        end_time="11:00",
    )

    assert result is None


def test_missing_teacher_cannot_receive_lesson(student: int):
    result = database.create_lesson(
        teacher_id=999999,
        student_id=student,
        lesson_date="2030-07-18",
        start_time="10:00",
        end_time="11:00",
    )

    assert result is None


def test_missing_student_is_rejected_by_foreign_key(teacher: int):
    result = database.create_lesson(
        teacher_id=teacher,
        student_id=999999,
        lesson_date="2030-07-18",
        start_time="10:00",
        end_time="11:00",
    )

    assert result is None


def test_teacher_daily_maximum_is_enforced(teacher: int):
    # Change this teacher's daily lesson limit to two.
    teacher_data = database.get_teacher_by_id(teacher)
    database.edit_teacher(
        teacher,
        teacher_data[1],
        teacher_data[2],
        teacher_data[3],
        2,
        teacher_data[5],
    )

    student_ids = [
        database.create_student(
            f"Student{i}",
            "Limit",
            "Parent",
            str(i),
            f"parent{i}@example.com",
            "2015-01-01",
            f"765-555-{5000 + i}",
        )
        for i in range(3)
    ]

    first = database.create_lesson(
        teacher, student_ids[0], "2030-08-01", "08:00", "08:30"
    )
    second = database.create_lesson(
        teacher, student_ids[1], "2030-08-01", "09:00", "09:30"
    )
    third = database.create_lesson(
        teacher, student_ids[2], "2030-08-01", "10:00", "10:30"
    )

    assert first is not None
    assert second is not None
    assert third is None


# ---------------------------------------------------------------------------
# Lesson update tests
# ---------------------------------------------------------------------------

def test_update_lesson_notes(lesson: int):
    assert database.update_lesson_notes(lesson, "Updated lesson note") is True
    assert database.get_lesson_by_id(lesson)[8] == "Updated lesson note"


def test_update_lesson_status(lesson: int):
    assert database.update_lesson_status(lesson, "completed") is True
    assert database.get_lesson_by_id(lesson)[6] == "completed"


def test_update_lesson_student(lesson: int, second_student: int):
    assert database.update_lesson_student(lesson, second_student) is True
    assert database.get_lesson_by_id(lesson)[2] == second_student


def test_update_lesson_time_when_no_conflict(lesson: int):
    assert database.update_lesson_time(lesson, "12:00", "13:00") is True

    result = database.get_lesson_by_id(lesson)
    assert result[4] == "12:00"
    assert result[5] == "13:00"


def test_update_lesson_time_rejects_conflict(
    lesson: int,
    teacher: int,
    second_student: int,
):
    second_lesson = database.create_lesson(
        teacher,
        second_student,
        "2030-07-18",
        "12:00",
        "13:00",
    )
    assert second_lesson is not None

    updated = database.update_lesson_time(
        second_lesson,
        "10:30",
        "11:30",
    )

    assert updated is False
    result = database.get_lesson_by_id(second_lesson)
    assert result[4] == "12:00"
    assert result[5] == "13:00"


def test_update_lesson_teacher_when_no_conflict(
    lesson: int,
    second_teacher: int,
):
    assert database.update_lesson_teacher(lesson, second_teacher) is True
    assert database.get_lesson_by_id(lesson)[1] == second_teacher


def test_update_lesson_teacher_rejects_conflict(
    lesson: int,
    teacher: int,
    second_teacher: int,
    second_student: int,
):
    second_lesson = database.create_lesson(
        second_teacher,
        second_student,
        "2030-07-18",
        "10:00",
        "11:00",
    )
    assert second_lesson is not None

    updated = database.update_lesson_teacher(second_lesson, teacher)

    assert updated is False
    assert database.get_lesson_by_id(second_lesson)[1] == second_teacher


def test_edit_lesson(lesson: int, teacher: int, student: int):
    updated = database.edit_lesson(
        lesson_id=lesson,
        teacher_id=teacher,
        student_id=student,
        lesson_date="2030-07-19",
        start_time="14:00",
        end_time="15:00",
        status="completed",
        location="Online",
        notes="Edited lesson",
    )

    result = database.get_lesson_by_id(lesson)

    assert updated is True
    assert result[3] == "2030-07-19"
    assert result[4] == "14:00"
    assert result[6] == "completed"
    assert result[7] == "Online"
    assert result[8] == "Edited lesson"


def test_get_lessons_by_teacher(
    lesson: int,
    teacher: int,
    second_teacher: int,
    second_student: int,
):
    database.create_lesson(
        second_teacher,
        second_student,
        "2030-07-18",
        "10:00",
        "11:00",
    )

    lessons = database.get_lessons_by_teacher(teacher)

    assert len(lessons) == 1
    assert lessons[0][0] == lesson


def test_get_lessons_by_student(
    lesson: int,
    student: int,
    second_teacher: int,
):
    database.create_lesson(
        second_teacher,
        student,
        "2030-07-20",
        "10:00",
        "11:00",
    )

    lessons = database.get_lessons_by_student(student)

    assert len(lessons) == 2
    assert {item[0] for item in lessons} == {lesson, lessons[1][0]}


def test_delete_lesson(lesson: int):
    assert database.delete_lesson(lesson) is True
    assert database.get_lesson_by_id(lesson) is None


def test_delete_missing_lesson_returns_false():
    assert database.delete_lesson(999999) is False


def test_deleting_student_cascades_to_lessons(lesson: int, student: int):
    assert database.delete_student(student) is True
    assert database.get_lesson_by_id(lesson) is None


def test_teacher_with_lessons_should_be_deactivated_not_deleted(
    lesson: int,
    teacher: int,
):
    assert database.deactivate_user(teacher) is True

    user = database.get_user_by_id(teacher)
    saved_lesson = database.get_lesson_by_id(lesson)

    assert user[4] == 0
    assert saved_lesson is not None


# ---------------------------------------------------------------------------
# Helper and schema tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("original", "minutes", "expected"),
    [
        ("10:00", 20, "10:20"),
        ("10:00", -20, "09:40"),
        ("23:50", 20, "00:10"),
        ("00:10", -20, "23:50"),
    ],
)
def test_add_minutes(original: str, minutes: int, expected: str):
    assert add_minutes(original, minutes) == expected


def test_foreign_keys_are_enabled():
    connection, cursor = database.create_connection()
    cursor.execute("PRAGMA foreign_keys")
    enabled = cursor.fetchone()[0]
    connection.close()

    assert enabled == 1


def test_schema_rejects_invalid_lesson_status(teacher: int, student: int):
    connection, cursor = database.create_connection()

    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """
            INSERT INTO lessons (
                teacher_id,
                student_id,
                lesson_date,
                start_time,
                end_time,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                teacher,
                student,
                "2030-07-18",
                "15:00",
                "16:00",
                "invalid-status",
            ),
        )

    connection.rollback()
    connection.close()