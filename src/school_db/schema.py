# src/school_db/schema.py
# Schema Migration Runner and Verification Engine

import os
from typing import Dict, List, Any
from .db import DatabaseManager


class SchemaManager:
    """Manages execution of DDL migrations, views, procedures, and schema verification."""

    EXPECTED_TABLES = [
        "departments",
        "professors",
        "students",
        "courses",
        "course_sections",
        "grade_scale",
        "enrollments",
        "academic_audit_log",
    ]

    EXPECTED_VIEWS = [
        "vw_course_enrollment_stats",
        "vw_student_transcript",
        "vw_department_performance",
        "vw_honor_roll",
    ]

    def __init__(self, db: DatabaseManager, sql_dir: str = "sql"):
        # Initialize schema manager with database instance and SQL directory path
        self.db = db
        self.sql_dir = sql_dir

    def _read_sql_file(self, filename: str) -> str:
        # Load SQL script file contents
        filepath = os.path.join(self.sql_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"SQL file not found at: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def migrate(self):
        # Execute schema DDL, stored procedures/triggers, and views
        schema_sql = self._read_sql_file("01_schema.sql")
        self.db.execute_script(schema_sql)

        # Stored procedures and triggers with MySQL DELIMITER syntax are executed on live MySQL
        if self.db.mode == "mysql":
            procedures_sql = self._read_sql_file("02_procedures_triggers.sql")
            self.db.execute_script(procedures_sql)

        views_sql = self._read_sql_file("03_views.sql")
        self.db.execute_script(views_sql)

    def seed(self):
        # Execute curated seed dataset
        seed_sql = self._read_sql_file("04_seed.sql")
        self.db.execute_script(seed_sql)

    def verify(self) -> Dict[str, Any]:
        # Verify that all expected tables and views exist in the database
        results = {
            "tables_found": [],
            "tables_missing": [],
            "views_found": [],
            "views_missing": [],
            "status": "PASS",
        }

        # Check tables
        for table in self.EXPECTED_TABLES:
            try:
                self.db.fetch_one(f"SELECT 1 FROM {table} LIMIT 1")
                results["tables_found"].append(table)
            except Exception:
                results["tables_missing"].append(table)
                results["status"] = "FAIL"

        # Check views
        for view in self.EXPECTED_VIEWS:
            try:
                self.db.fetch_one(f"SELECT 1 FROM {view} LIMIT 1")
                results["views_found"].append(view)
            except Exception:
                results["views_missing"].append(view)
                results["status"] = "FAIL"

        return results

    def get_table_counts(self) -> Dict[str, int]:
        # Retrieve row counts for all core tables
        counts = {}
        for table in self.EXPECTED_TABLES:
            try:
                row = self.db.fetch_one(f"SELECT COUNT(*) as cnt FROM {table}")
                counts[table] = row["cnt"] if row else 0
            except Exception:
                counts[table] = 0
        return counts

    def export_sql(self, output_path: str):
        # Concatenate and export consolidated deployment SQL script
        files = [
            "01_schema.sql",
            "02_procedures_triggers.sql",
            "03_views.sql",
            "04_seed.sql",
        ]
        consolidated = []
        for fn in files:
            content = self._read_sql_file(fn)
            consolidated.append(f"-- =============================================\n-- FILE: {fn}\n-- =============================================\n\n{content}\n")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(consolidated))
