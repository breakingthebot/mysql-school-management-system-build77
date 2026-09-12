# tests/test_schema.py
# Unit Tests for Schema Migrations, DDL, and Table Inventories

import os
import pytest
from school_db.db import DatabaseManager
from school_db.schema import SchemaManager


@pytest.fixture
def db_and_schema():
    # Provide initialized in-memory database and schema manager
    db = DatabaseManager(in_memory=True)
    schema = SchemaManager(db=db, sql_dir="sql")
    return db, schema


def test_sql_files_exist():
    # Verify all expected SQL files exist on disk
    expected_files = [
        "sql/01_schema.sql",
        "sql/02_procedures_triggers.sql",
        "sql/03_views.sql",
        "sql/04_seed.sql",
    ]
    for ef in expected_files:
        assert os.path.exists(ef), f"Expected SQL file missing: {ef}"


def test_schema_migration_tables(db_and_schema):
    # Verify schema migration creates all expected tables
    db, schema = db_and_schema
    schema.migrate()
    verification = schema.verify()

    assert verification["status"] == "PASS"
    assert len(verification["tables_found"]) == 12
    assert len(verification["tables_missing"]) == 0


def test_schema_migration_views(db_and_schema):
    # Verify schema migration creates all analytical views
    db, schema = db_and_schema
    schema.migrate()
    verification = schema.verify()

    assert len(verification["views_found"]) == 6
    assert len(verification["views_missing"]) == 0
    for v in ["vw_course_enrollment_stats", "vw_student_transcript", "vw_department_performance", "vw_honor_roll", "vw_course_prerequisites", "vw_degree_progress"]:
        assert v in verification["views_found"]


def test_table_row_counts_after_seed(db_and_schema):
    # Verify seed data inserts expected quantities
    db, schema = db_and_schema
    schema.migrate()
    schema.seed()

    counts = schema.get_table_counts()
    assert counts["departments"] == 5
    assert counts["professors"] == 6
    assert counts["students"] == 10
    assert counts["courses"] == 8
    assert counts["course_sections"] == 8
    assert counts["grade_scale"] == 9
    assert counts["enrollments"] == 20
    assert counts["course_prerequisites"] == 3
    assert counts["degree_programs"] == 2
    assert counts["degree_requirements"] == 8
    assert counts["student_degrees"] == 3


def test_export_sql(db_and_schema, tmp_path):
    # Verify consolidated SQL export generates readable non-empty file
    db, schema = db_and_schema
    output_file = str(tmp_path / "consolidated_school.sql")
    schema.export_sql(output_file)

    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "CREATE TABLE IF NOT EXISTS departments" in content
    assert "CREATE TABLE IF NOT EXISTS students" in content
    assert "vw_course_enrollment_stats" in content
