# tests/test_prerequisites_degree.py
# Unit and Integration Tests for Prerequisite DAG and Degree Audit Engine

import sys
import pytest
from unittest.mock import patch
from school_db.db import DatabaseManager
from school_db.schema import SchemaManager
from school_db.service import AcademicService
from school_db.cli import main


@pytest.fixture
def service():
    # Provide initialized and seeded database with AcademicService
    db = DatabaseManager(in_memory=True)
    schema = SchemaManager(db=db, sql_dir="sql")
    schema.migrate()
    schema.seed()
    return AcademicService(db=db)


def test_prerequisite_catalog_loaded(service):
    # Verify prerequisite relationship records exist in database view
    catalog = service.get_course_prerequisites()
    assert len(catalog) == 3
    cs201 = next(item for item in catalog if item["course_code"] == "CS-201")
    assert cs201["prerequisite_code"] == "CS-101"
    assert cs201["min_grade_letter"] == "C"


def test_enrollment_blocked_when_missing_prerequisite(service):
    # Verify student without prerequisite is blocked from enrolling
    # Student 6 has not completed CS-101 (course 1). Section 2 is CS-201.
    with pytest.raises(ValueError, match="Missing required prerequisite"):
        service.enroll_student(student_id=6, section_id=2)


def test_enrollment_allowed_when_prerequisite_satisfied(service):
    # Verify student with passing prerequisite can enroll
    # Student 4 completed CS-101 with grade 'C' (2.00). Section 2 is CS-201.
    result = service.enroll_student(student_id=4, section_id=2)
    assert result["status"] == "SUCCESS"
    assert result["enrollment_id"] is not None


def test_enrollment_blocked_when_prerequisite_grade_too_low(service):
    # Verify student with grade below prerequisite threshold is blocked
    # Enroll student 7 in section 1 (CS-101) and assign grade 'D' (1.00)
    service.db.execute(
        """
        INSERT INTO enrollments (section_id, student_id, enrollment_date, status, score, grade_letter, grade_points)
        VALUES (1, 7, '2026-08-20', 'completed', 65.0, 'D', 1.00)
        """
    )
    # Attempt to enroll student 7 in section 2 (CS-201, requires C / 2.00)
    with pytest.raises(ValueError, match="Missing required prerequisite"):
        service.enroll_student(student_id=7, section_id=2)


def test_degree_audit_calculation(service):
    # Verify degree completion audit calculates satisfied courses and credits
    # Student 1 (Maya Lin) is declared in BS-CS
    audit = service.audit_degree(student_id=1)
    assert audit["student_number"] == "STU-1001"
    assert audit["degree_code"] == "BS-CS"
    assert audit["total_credits_required"] == 120
    assert audit["completed_credits"] >= 8
    assert audit["progress_pct"] > 0
    assert len(audit["satisfied_courses"]) >= 2
    assert audit["gpa_requirement_met"] is True
    assert audit["graduation_eligible"] is False  # Still needs 120 credits


def test_cli_prerequisites(capsys):
    # Verify CLI prerequisites subcommand
    with patch.object(sys, "argv", ["mysql-school", "--in-memory", "prerequisites"]):
        main()
    captured = capsys.readouterr()
    assert "COURSE PREREQUISITES CATALOG" in captured.out
    assert "CS-201" in captured.out
    assert "CS-101" in captured.out


def test_cli_degree_audit(capsys):
    # Verify CLI degree-audit subcommand
    with patch.object(sys, "argv", ["mysql-school", "--in-memory", "degree-audit", "--student", "1"]):
        main()
    captured = capsys.readouterr()
    assert "DEGREE COMPLETION AUDIT: Maya Lin" in captured.out
    assert "BS-CS" in captured.out
    assert "Credits Completed:" in captured.out
    assert "Graduation Status: PENDING" in captured.out
