from dataclasses import dataclass

# classes for db


@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    role: str
    is_active: int = 1


@dataclass
class Teacher:
    id: int
    user_id: int
    first_name: str
    last_name: str
    phone: str | None = None
    max_students: int | None = None
    notes: str | None = None


@dataclass
class Student:
    id: int
    first_name: str
    last_name: str
    parent_name: str | None = None
    parent_email: str | None = None
    parent_phone: str | None = None
    notes: str | None = None
    is_active: int = 1


@dataclass
class Lesson:
    id: int
    teacher_id: int
    student_id: int
    lesson_date: str
    start_time: str
    end_time: str
    status: str = "scheduled"
    notes: str | None = None
