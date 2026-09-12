# tests/test_procedures_triggers.py
# Unit Tests for Academic Procedures, Triggers, and GPA Calculations

import pytest
from school_db.db import DatabaseManager
from school_db.schema import SchemaManager
from school_db.service import AcademicService


@pytest.fixture
def service():
    # Setup populated database with academic service instance
    db = DatabaseManager(in_memory=True)
    schema = SchemaManager(db=db, sql_dir="sql")
    schema.migrate()
    schema.seed()
    return AcademicService(db=db)


def test_enroll_student_success(service):
    # Verify active student can enroll in a section with available capacity
    # Student 4 in Section 2 (CS-201, Fall 2026)
    res = service.enroll_student(student_id=4, section_id=2)

    assert res["status"] == "SUCCESS"
    assert res["enrollment_id"] is not None

    # Check that enrolled_count was incremented
    sec = service.db.fetch_one("SELECT enrolled_count FROM course_sections WHERE section_id = 2")
    assert sec["enrolled_count"] == 4


def test_enroll_student_duplicate_fails(service):
    # Verify duplicate enrollment in same section raises ValueError
    # Student 1 is already enrolled in section 1
    with pytest.raises(ValueError, match="already enrolled"):
        service.enroll_student(student_id=1, section_id=1)


def test_enroll_student_inactive_status_fails(service):
    # Verify student on probation or suspended cannot enroll
    # Student 9 status is 'probation'
    with pytest.raises(ValueError, match="Must be active"):
        service.enroll_student(student_id=9, section_id=1)


def test_enroll_student_capacity_exceeded_fails(service):
    # Verify section capacity limit blocks enrollment when full
    # Set capacity of section 1 course to equal enrolled count
    service.db.execute("UPDATE courses SET max_capacity = 4 WHERE course_id = 1")
    service.db.execute("UPDATE course_sections SET enrolled_count = 4 WHERE section_id = 1")

    # Try enrolling student 5 in section 1
    with pytest.raises(ValueError, match="maximum student capacity"):
        service.enroll_student(student_id=5, section_id=1)


def test_grade_assignment_and_scale_resolution(service):
    # Verify score is resolved to correct letter grade and grade points
    # Enroll student 4 in section 6 (EE-110)
    enroll_res = service.enroll_student(student_id=4, section_id=6)
    eid = enroll_res["enrollment_id"]

    # Assign score 91.5 (A- / 3.70)
    grade_res = service.assign_grade(enrollment_id=eid, score=91.5)

    assert grade_res["letter_grade"] == "A-"
    assert grade_res["grade_points"] == 3.70
    assert grade_res["score"] == 91.5


def test_grade_assignment_updates_audit_log(service):
    # Verify grade modifications create audit log entries
    # Enroll student 4 in section 6 (EE-110)
    enroll_res = service.enroll_student(student_id=4, section_id=6)
    eid = enroll_res["enrollment_id"]

    # First grade assignment
    service.assign_grade(enrollment_id=eid, score=85.0)  # B / 3.00

    # Modify grade to 94.0 (A / 4.00)
    service.assign_grade(enrollment_id=eid, score=94.0)

    # Check audit log
    logs = service.db.fetch_all(
        "SELECT * FROM academic_audit_log WHERE record_id = ? AND table_name = 'enrollments'",
        (eid,)
    )
    assert len(logs) >= 1
    latest_log = logs[-1]
    assert latest_log["field_name"] == "grade_letter"
    assert latest_log["old_value"] == "B"
    assert latest_log["new_value"] == "A"


def test_student_cumulative_gpa_recalculation(service):
    # Verify cumulative GPA is weighted by course credit hours
    # Student 3 has:
    # Section 1 (CS-101, 4 credits): A (4.00) -> 16.0 points
    # Section 2 (CS-201, 4 credits): A (4.00) -> 16.0 points
    # Total points = 32.0, total credits = 8 -> GPA = 4.00
    gpa = service.recalculate_student_gpa(student_id=3)
    assert gpa == 4.00
