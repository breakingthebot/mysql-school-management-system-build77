# Changelog — Build 77: MySQL School Management System

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-12

### Added
- **Core MySQL 8.0 DDL Schema** (`sql/01_schema.sql`):
  - 8 normalized tables: `departments`, `professors`, `students`, `courses`, `course_sections`, `grade_scale`, `enrollments`, and `academic_audit_log`.
  - Referential integrity with foreign keys, cascading updates, and check constraints.
  - Performance indexes on student GPA, course department IDs, and section terms.
- **Triggers & Stored Procedures** (`sql/02_procedures_triggers.sql`):
  - `trg_check_section_capacity`: Before insert trigger blocking over-capacity enrollments.
  - `trg_increment_enrolled_count` & `trg_decrement_enrolled_count`: Synchronizes section headcount.
  - `trg_audit_grade_change`: Automatically tracks grade adjustments in `academic_audit_log`.
  - `sp_enroll_student`: Transactional student registration with status verification.
  - `sp_calculate_student_gpa`: Weighted cumulative GPA calculation.
  - `sp_assign_grade`: Automated score-to-letter grading with GPA recomputation.
- **Analytical Reporting Views** (`sql/03_views.sql`):
  - `vw_course_enrollment_stats`: Section capacity utilization and fill status.
  - `vw_student_transcript`: Denormalized academic transcript reports.
  - `vw_department_performance`: Aggregated department metrics and average GPA.
  - `vw_honor_roll`: Filtered reporting of active students with GPA >= 3.50.
- **Curated Educational Dataset** (`sql/04_seed.sql`):
  - 5 departments, 6 professors, 10 students, 8 courses, 8 sections, 9 grade scale rows, and 20 graded enrollments.
- **Python CLI & Dual-Mode Database Suite** (`src/school_db/`):
  - `DatabaseManager`: Support for live MySQL connections and zero-dependency in-memory engine.
  - `SchemaManager`: DDL execution, verification, table inventory counts, and consolidated SQL export.
  - `AcademicService`: High-level operational API for enrollment and grading.
  - `mysql-school`: CLI suite with commands `migrate`, `verify`, `info`, `seed`, `stats`, `transcript`, `honor-roll`, `enroll`, `grade`, and `export-sql`.
- **Automated Test Suite** (`tests/`):
  - 19 automated unit and integration tests across schema, procedures, views, and CLI commands.
- **GitHub Actions CI Pipeline** (`.github/workflows/ci.yml`):
  - Automated matrix testing across Python 3.10, 3.11, 3.12, and 3.13.
- **Project Documentation**:
  - `README.md` with Mermaid Entity-Relationship diagram and architecture notes.
  - `LICENSE` under MIT.
