# src/school_db/service.py
# Academic Service Layer Emulating Stored Procedures and Triggers

from typing import Dict, Any, List, Optional
from .db import DatabaseManager


class AcademicService:
    """Provides high-level academic transactions enforcing capacity and grade logic."""

    def __init__(self, db: DatabaseManager):
        # Initialize service with active database manager
        self.db = db

    def enroll_student(self, student_id: int, section_id: int) -> Dict[str, Any]:
        # Enroll student in section with capacity and duplicate check
        # 1. Check student existence and status
        student = self.db.fetch_one(
            "SELECT student_id, status FROM students WHERE student_id = ?",
            (student_id,)
        )
        if not student:
            raise ValueError(f"Student with ID {student_id} not found.")

        if student["status"] != "active":
            raise ValueError(f"Student status is '{student['status']}'. Must be active to enroll.")

        # 2. Check for duplicate enrollment
        existing = self.db.fetch_one(
            "SELECT enrollment_id FROM enrollments WHERE student_id = ? AND section_id = ?",
            (student_id, section_id)
        )
        if existing:
            raise ValueError("Student is already enrolled in this section.")

        # 3. Check section capacity
        section_info = self.db.fetch_one(
            """
            SELECT cs.enrolled_count, c.max_capacity
            FROM course_sections cs
            JOIN courses c ON cs.course_id = c.course_id
            WHERE cs.section_id = ?
            """,
            (section_id,)
        )
        if not section_info:
            raise ValueError(f"Section with ID {section_id} not found.")

        if section_info["enrolled_count"] >= section_info["max_capacity"]:
            raise ValueError("Section has reached maximum student capacity.")

        # 4. Insert enrollment
        self.db.execute(
            """
            INSERT INTO enrollments (section_id, student_id, enrollment_date, status)
            VALUES (?, ?, DATE('now'), 'enrolled')
            """,
            (section_id, student_id)
        )

        # 5. Increment enrolled_count
        self.db.execute(
            "UPDATE course_sections SET enrolled_count = enrolled_count + 1 WHERE section_id = ?",
            (section_id,)
        )

        # 6. Fetch created enrollment
        row = self.db.fetch_one(
            "SELECT enrollment_id FROM enrollments WHERE student_id = ? AND section_id = ?",
            (student_id, section_id)
        )
        return {
            "status": "SUCCESS",
            "enrollment_id": row["enrollment_id"] if row else None,
            "message": "Student successfully enrolled in section."
        }

    def assign_grade(self, enrollment_id: int, score: float) -> Dict[str, Any]:
        # Assign numerical score, resolve letter grade, and recalculate GPA
        enrollment = self.db.fetch_one(
            "SELECT student_id, grade_letter FROM enrollments WHERE enrollment_id = ?",
            (enrollment_id,)
        )
        if not enrollment:
            raise ValueError(f"Enrollment with ID {enrollment_id} not found.")

        old_grade = enrollment["grade_letter"]
        student_id = enrollment["student_id"]

        # Resolve grade scale
        scale = self.db.fetch_one(
            "SELECT letter_grade, grade_points FROM grade_scale WHERE ? >= min_score AND ? <= max_score LIMIT 1",
            (score, score)
        )
        if not scale:
            raise ValueError(f"Score {score} is outside valid grade scale bounds.")

        letter_grade = scale["letter_grade"]
        grade_points = scale["grade_points"]

        # Update enrollment
        self.db.execute(
            """
            UPDATE enrollments
            SET score = ?, grade_letter = ?, grade_points = ?, status = 'completed'
            WHERE enrollment_id = ?
            """,
            (score, letter_grade, grade_points, enrollment_id)
        )

        # Record audit log if grade changed
        if old_grade != letter_grade:
            self.db.execute(
                """
                INSERT INTO academic_audit_log (
                    table_name, record_id, action, field_name, old_value, new_value, performed_by
                ) VALUES (?, ?, 'UPDATE', 'grade_letter', ?, ?, 'academic_service')
                """,
                ("enrollments", enrollment_id, str(old_grade), str(letter_grade))
            )

        # Recalculate cumulative GPA
        new_gpa = self.recalculate_student_gpa(student_id)

        return {
            "enrollment_id": enrollment_id,
            "student_id": student_id,
            "score": score,
            "letter_grade": letter_grade,
            "grade_points": grade_points,
            "cumulative_gpa": new_gpa
        }

    def recalculate_student_gpa(self, student_id: int) -> float:
        # Calculate weighted GPA based on course credits and grade points
        rows = self.db.fetch_all(
            """
            SELECT e.grade_points, c.credits
            FROM enrollments e
            JOIN course_sections cs ON e.section_id = cs.section_id
            JOIN courses c ON cs.course_id = c.course_id
            WHERE e.student_id = ? AND e.status = 'completed' AND e.grade_points IS NOT NULL
            """,
            (student_id,)
        )

        total_pts = sum(r["grade_points"] * r["credits"] for r in rows)
        total_creds = sum(r["credits"] for r in rows)

        gpa = round(total_pts / total_creds, 2) if total_creds > 0 else 0.00
        self.db.execute(
            "UPDATE students SET cumulative_gpa = ? WHERE student_id = ?",
            (gpa, student_id)
        )
        return gpa

    def get_student_transcript(self, student_id: int) -> List[Dict[str, Any]]:
        # Fetch complete student transcript records
        return self.db.fetch_all(
            "SELECT * FROM vw_student_transcript WHERE student_id = ?",
            (student_id,)
        )

    def get_honor_roll(self) -> List[Dict[str, Any]]:
        # Fetch active students on honor roll (GPA >= 3.50)
        return self.db.fetch_all("SELECT * FROM vw_honor_roll ORDER BY cumulative_gpa DESC")
