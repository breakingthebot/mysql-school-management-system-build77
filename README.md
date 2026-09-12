# MySQL School Management System (Build 77)

[![CI](https://github.com/breakingthebot/mysql-school-management-system-build77/actions/workflows/ci.yml/badge.svg)](https://github.com/breakingthebot/mysql-school-management-system-build77/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/mysql-8.0+-orange.svg)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Production-grade MySQL school management system featuring normalized relational schema, stored procedures, triggers, audit logging, analytical views, and Python CLI suite.

---

## Architecture Notes

This system models a university academic operations platform built on MySQL 8.0+ standards. It coordinates student lifecycles, faculty departmental assignments, course scheduling, seat capacity enforcement, grade scale mapping, and academic transcripts with automated GPA recalculations.

### Architectural Entity-Relationship Model

```mermaid
erDiagram
    DEPARTMENTS ||--o{ PROFESSORS : employs
    DEPARTMENTS ||--o{ COURSES : offers
    DEPARTMENTS ||--o{ DEGREE_PROGRAMS : administers
    DEGREE_PROGRAMS ||--o{ DEGREE_REQUIREMENTS : specifies
    DEGREE_PROGRAMS ||--o{ STUDENT_DEGREES : declares
    COURSES ||--o{ DEGREE_REQUIREMENTS : satisfies
    COURSES ||--o{ COURSE_PREREQUISITES : defines
    COURSES ||--o{ COURSE_PREREQUISITES : requires
    PROFESSORS ||--o{ COURSE_SECTIONS : instructs
    COURSES ||--o{ COURSE_SECTIONS : schedules
    COURSE_SECTIONS ||--o{ ENROLLMENTS : registers
    STUDENTS ||--o{ ENROLLMENTS : undertakes
    STUDENTS ||--o{ STUDENT_DEGREES : enrolled_in
    GRADE_SCALE ||--o{ ENROLLMENTS : classifies
    ENROLLMENTS ||--o{ ACADEMIC_AUDIT_LOG : audits
    CLASSROOMS ||--o{ SECTION_SCHEDULES : hosts
    COURSE_SECTIONS ||--o{ SECTION_SCHEDULES : scheduled_in

    DEPARTMENTS {
        int department_id PK
        string dept_code UK
        string name
        string building
        decimal budget
    }

    PROFESSORS {
        int professor_id PK
        string first_name
        string last_name
        string email UK
        int department_id FK
        date hire_date
        decimal salary
        string status
    }

    STUDENTS {
        int student_id PK
        string student_number UK
        string first_name
        string last_name
        string email UK
        date date_of_birth
        date enrollment_date
        string status
        decimal cumulative_gpa
    }

    COURSES {
        int course_id PK
        string course_code UK
        string title
        int credits
        int department_id FK
        int max_capacity
    }

    COURSE_SECTIONS {
        int section_id PK
        int course_id FK
        int professor_id FK
        string term
        int academic_year
        string room_number
        int enrolled_count
    }

    ENROLLMENTS {
        int enrollment_id PK
        int section_id FK
        int student_id FK
        date enrollment_date
        string status
        decimal score
        string grade_letter FK
        decimal grade_points
    }

    GRADE_SCALE {
        string letter_grade PK
        decimal min_score
        decimal max_score
        decimal grade_points
    }

    ACADEMIC_AUDIT_LOG {
        int audit_id PK
        string table_name
        int record_id
        string action
        string field_name
        string old_value
        string new_value
        timestamp created_at
    }

    COURSE_PREREQUISITES {
        int prerequisite_id PK
        int course_id FK
        int prerequisite_course_id FK
        string min_grade_letter
        decimal min_grade_points
    }

    DEGREE_PROGRAMS {
        int degree_id PK
        string degree_code UK
        string title
        int department_id FK
        int total_credits_required
        decimal min_gpa_required
    }

    DEGREE_REQUIREMENTS {
        int requirement_id PK
        int degree_id FK
        int course_id FK
        boolean is_mandatory
    }

    STUDENT_DEGREES {
        int declaration_id PK
        int student_id FK
        int degree_id FK
        date declaration_date
        string status
    }

    CLASSROOMS {
        int room_id PK
        string building
        string room_number UK
        int seating_capacity
        string room_type
    }

    SECTION_SCHEDULES {
        int schedule_id PK
        int section_id FK
        int room_id FK
        string day_of_week
        time start_time
        time end_time
    }
```

---

## Core Schema & Business Logic Features

1. **Normalized Relational Model (3NF)**:
   - Eliminates data redundancy across 14 interconnected relational tables.
   - Enforces referential integrity with strict foreign key constraints, `ON UPDATE CASCADE`, and conditional `ON DELETE` rules.

2. **Course Prerequisite Enforcement (Directed Acyclic Graph)**:
   - `course_prerequisites`: Models foundational course requirements with minimum acceptable letter grade and grade point thresholds.
   - Dynamic validation prevents students from registering for advanced coursework without satisfactory completion of prerequisites.

3. **Degree Programs & Completion Audit Engine**:
   - `degree_programs`, `degree_requirements`, and `student_degrees` model degree requirements, mandatory courses, and declared degree tracks.
   - Real-time graduation auditing evaluates completed credits against total requirements, GPA thresholds, and outstanding mandatory courses.

4. **Classroom Scheduling & Conflict Detector**:
   - `classrooms` & `section_schedules`: Models room inventories, seating limits, and lecture/lab time slots.
   - Dual-constraint conflict detection prevents room double-booking and professor simultaneous instruction overlap.
   - Capacity guards ensure section capacity never exceeds assigned classroom seating.

5. **Automated Triggers (`sql/02_procedures_triggers.sql`)**:
   - `trg_check_section_capacity`: Before insert trigger on `enrollments` preventing enrollment if the section's enrolled count equals or exceeds course capacity.
   - `trg_increment_enrolled_count`: After insert trigger automatically incrementing `enrolled_count` on `course_sections`.
   - `trg_decrement_enrolled_count`: After delete trigger automatically decrementing `enrolled_count`.
   - `trg_audit_grade_change`: After update trigger recording historical grade transitions in `academic_audit_log`.

6. **Transactional Stored Procedures & Operations**:
   - `sp_enroll_student`: Verifies student status (must be `active`), validates prerequisite completion, checks capacity constraints, and prevents duplicate registrations.
   - `sp_calculate_student_gpa`: Calculates credit-weighted cumulative GPA and updates `students.cumulative_gpa`.
   - `sp_assign_grade`: Maps numerical exam scores to letter grades via `grade_scale` and triggers automatic GPA updates.

7. **Analytical SQL Views (`sql/03_views.sql`)**:
   - `vw_course_enrollment_stats`: Live capacity utilization percentages and section status (`OPEN`, `NEAR CAPACITY`, `FULL`).
   - `vw_student_transcript`: Denormalized transcript views including course credits, terms, and letter grades.
   - `vw_department_performance`: Aggregated department metrics tracking student enrollment counts and average GPA.
   - `vw_honor_roll`: Filtered reporting of active students with cumulative GPA ≥ 3.50.
   - `vw_course_prerequisites`: Catalog of prerequisite relationships and grade thresholds.
   - `vw_degree_progress`: Student degree progress percentages and graduation eligibility.
   - `vw_classroom_utilization`: Room scheduling utilization, active section counts, and total weekly hours.
   - `vw_faculty_workload`: Professor teaching credits, sections taught, hours, and workload categorization (`Light`, `Standard`, `Full`, `Overload`).
   - `vw_master_timetable`: Master consolidated schedule across classrooms, sections, days, and time blocks.

---

## Repository Structure

```
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI matrix (Python 3.10 - 3.13)
├── sql/
│   ├── 01_schema.sql            # Production MySQL 8.0 DDL schema (14 tables)
│   ├── 02_procedures_triggers.sql # Stored procedures and academic triggers
│   ├── 03_views.sql             # Analytical and reporting views (9 views)
│   └── 04_seed.sql              # Curated educational seed dataset
├── src/
│   └── school_db/
│       ├── __init__.py          # Package metadata (v1.2.0)
│       ├── db.py                # Dual-mode database manager (Live MySQL + in-memory engine)
│       ├── schema.py            # Migration runner and verification engine
│       ├── service.py           # Academic operations service layer
│       └── cli.py               # CLI tool entry point (mysql-school)
├── tests/
│   ├── test_schema.py           # Schema migration, DDL, and table tests
│   ├── test_procedures_triggers.py # Triggers, capacity, and GPA logic tests
│   ├── test_views.py            # Analytical view query tests
│   ├── test_prerequisites_degree.py # Prerequisite DAG & degree audit tests
│   ├── test_scheduling_conflicts.py # Classroom scheduling & faculty workload tests
│   └── test_cli.py              # CLI commands and argument parser tests
├── CHANGELOG.md                 # Project changelog
├── LICENSE                      # MIT License
├── pyproject.toml               # Python package configuration
└── requirements.txt             # Project dependencies
```

---

## Installation & Quickstart

### Prerequisites
- Python 3.10+
- *(Optional)* MySQL 8.0+ server (for live database execution)

### 1. Set Up Virtual Environment

```bash
# Create and activate virtual environment
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Linux / macOS
source venv/bin/activate

# Install dependencies in editable mode
pip install -e ".[dev]"
```

### 2. Environment Configuration

Copy the sample environment file:
```bash
cp .env.example .env
```

If connecting to a live MySQL instance, specify `DATABASE_URL`:
```env
DATABASE_URL=mysql://root:password@localhost:3306/school_management
```

*Note: If no `DATABASE_URL` is configured, or when using `--in-memory`, the suite runs against an embedded, zero-dependency in-memory engine for rapid local testing.*

### 3. CLI Commands

```bash
# Verify schema integrity
mysql-school --in-memory verify

# Display table inventory and record counts
mysql-school --in-memory info

# View department performance metrics
mysql-school --in-memory stats

# View academic transcript for Student #1
mysql-school --in-memory transcript --student 1

# List students on the Honor Roll (GPA >= 3.50)
mysql-school --in-memory honor-roll

# View course prerequisites catalog
mysql-school --in-memory prerequisites

# Run degree completion audit for Student #1
mysql-school --in-memory degree-audit --student 1

# View classroom capacity and weekly utilization
mysql-school --in-memory rooms

# View faculty teaching workload metrics
mysql-school --in-memory workload

# View master timetable schedule
mysql-school --in-memory timetable --term Fall

# Schedule a section into a room and time slot (enforces conflict guards)
mysql-school --in-memory schedule --section 2 --room 1 --day FRI --start 10:00:00 --end 11:30:00

# Enroll a student in a course section (enforces capacity & prerequisites)
mysql-school --in-memory enroll --student 4 --section 2

# Assign grade to an enrollment
mysql-school --in-memory grade --enrollment 1 --score 95.0

# Export consolidated deployment SQL script
mysql-school export-sql --output school_full.sql
```

---

## Running Automated Tests

Run the complete test suite using `pytest`:

```bash
pytest -v
```

All 41 tests run with zero external service dependencies in under 0.7 seconds.

---

## Iterations & Git Commit History

| Iteration | Version | Summary | Tests |
| :---: | :---: | :--- | :---: |
| **01** | `v1.0.0` | **Core MySQL Relational Schema, Procedures, Triggers & CLI**: 8 normalized tables, capacity constraints, academic audit logging, analytical views, and `mysql-school` CLI suite. | 23 / 23 |
| **02** | `v1.1.0` | **Course Prerequisite DAG & Degree Audit Engine**: 4 new tables, self-referential prerequisite enforcement, degree programs, requirements tracking, and `degree-audit` CLI command. | 30 / 30 |
| **03** | `v1.2.0` | **Classroom Conflict Detector & Faculty Workload Engine**: 2 new tables, double-booking and professor overlap guards, 3 analytical views, `rooms`, `workload`, `timetable`, and `schedule` CLI commands. | 41 / 41 |

---

## Data Handling & Privacy
- Zero persistent PII stored by default.
- Test fixtures use synthetic and historical educator names.
- Database credentials and secrets are managed exclusively through environment variables and excluded from source control.

---

## License
Distributed under the [MIT License](LICENSE). Copyright (c) 2026 BreakingTheBot.
