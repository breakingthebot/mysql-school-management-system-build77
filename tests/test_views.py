# tests/test_views.py
# Unit Tests for Analytical SQL Views

import pytest
from school_db.db import DatabaseManager
from school_db.schema import SchemaManager


@pytest.fixture
def populated_db():
    # Provide populated database for analytical queries
    db = DatabaseManager(in_memory=True)
    schema = SchemaManager(db=db, sql_dir="sql")
    schema.migrate()
    schema.seed()
    return db


def test_course_enrollment_stats_view(populated_db):
    # Verify course enrollment stats view provides capacity calculations
    rows = populated_db.fetch_all("SELECT * FROM vw_course_enrollment_stats")
    assert len(rows) == 8
    first = rows[0]
    assert "course_code" in first
    assert "enrolled_count" in first
    assert "capacity_utilization_pct" in first
    assert first["capacity_utilization_pct"] >= 0


def test_student_transcript_view(populated_db):
    # Verify student transcript view returns grades and credits
    rows = populated_db.fetch_all("SELECT * FROM vw_student_transcript WHERE student_id = 1")
    assert len(rows) >= 3  # Student 1 enrolled in 3 courses
    for r in rows:
        assert r["student_number"] == "STU-1001"
        assert r["grade_letter"] is not None
        assert r["grade_points"] is not None


def test_department_performance_view(populated_db):
    # Verify department performance view calculates aggregations
    rows = populated_db.fetch_all("SELECT * FROM vw_department_performance")
    assert len(rows) == 5
    cs_dept = next(r for r in rows if r["dept_code"] == "CS")
    assert cs_dept["total_professors"] == 2
    assert cs_dept["total_courses"] == 3
    assert cs_dept["total_enrollments"] >= 10


def test_honor_roll_view(populated_db):
    # Verify honor roll view only returns students with GPA >= 3.50
    rows = populated_db.fetch_all("SELECT * FROM vw_honor_roll")
    assert len(rows) > 0
    for r in rows:
        assert r["cumulative_gpa"] >= 3.50
        assert r["status"] == "active"
