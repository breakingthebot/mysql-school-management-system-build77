# src/school_db/cli.py
# Command-Line Interface for School Management System Database

import sys
import argparse
from . import __version__
from .db import DatabaseManager
from .schema import SchemaManager
from .service import AcademicService


def build_parser() -> argparse.ArgumentParser:
    # Construct CLI argument parser with commands and options
    parser = argparse.ArgumentParser(
        prog="mysql-school",
        description="MySQL School Management System Database Suite"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--in-memory",
        action="store_true",
        help="Execute against in-memory verification engine without external MySQL connection"
    )
    parser.add_argument(
        "--sql-dir",
        default="sql",
        help="Directory containing SQL schema and script files (default: sql)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # migrate
    subparsers.add_parser("migrate", help="Execute DDL migrations and view definitions")

    # verify
    subparsers.add_parser("verify", help="Verify tables and views exist in the database")

    # info
    subparsers.add_parser("info", help="Display table inventory and record counts")

    # seed
    subparsers.add_parser("seed", help="Populate database with curated educational seed dataset")

    # stats
    subparsers.add_parser("stats", help="Display department and enrollment statistics")

    # transcript
    p_trans = subparsers.add_parser("transcript", help="Display student academic transcript")
    p_trans.add_argument("--student", type=int, required=True, help="Student ID")

    # honor-roll
    subparsers.add_parser("honor-roll", help="Display active students on the honor roll")

    # enroll
    p_enroll = subparsers.add_parser("enroll", help="Enroll a student in a course section")
    p_enroll.add_argument("--student", type=int, required=True, help="Student ID")
    p_enroll.add_argument("--section", type=int, required=True, help="Course Section ID")

    # grade
    p_grade = subparsers.add_parser("grade", help="Assign grade and score to an enrollment")
    p_grade.add_argument("--enrollment", type=int, required=True, help="Enrollment ID")
    p_grade.add_argument("--score", type=float, required=True, help="Numerical score (0-100)")

    # prerequisites
    p_prereq = subparsers.add_parser("prerequisites", help="Display course prerequisites catalog")
    p_prereq.add_argument("--course", default=None, help="Filter by course code (e.g. CS-201)")

    # degree-audit
    p_audit = subparsers.add_parser("degree-audit", help="Run degree completion and graduation audit for a student")
    p_audit.add_argument("--student", type=int, required=True, help="Student ID")
    p_audit.add_argument("--degree", type=int, default=None, help="Degree Program ID (optional)")

    # export-sql
    p_export = subparsers.add_parser("export-sql", help="Export consolidated SQL deployment script")
    p_export.add_argument("--output", default="school_management_full.sql", help="Target output file path")

    return parser


def main():
    # CLI entry point dispatcher
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Initialize database and managers
    db = DatabaseManager(in_memory=args.in_memory)
    schema = SchemaManager(db=db, sql_dir=args.sql_dir)
    service = AcademicService(db=db)

    # Always migrate and seed in-memory for command execution if tables not yet populated
    if args.in_memory and args.command not in ["migrate", "export-sql"]:
        schema.migrate()
        schema.seed()

    if args.command == "migrate":
        print("Executing schema migrations and view definitions...")
        schema.migrate()
        print("Migrations completed successfully.")

    elif args.command == "seed":
        print("Populating database with curated seed data...")
        schema.seed()
        print("Database seeded successfully.")

    elif args.command == "verify":
        res = schema.verify()
        print("==================================================")
        print(f"SCHEMA INTEGRITY VERIFICATION: {res['status']}")
        print("==================================================")
        print(f"Tables Found ({len(res['tables_found'])}): {', '.join(res['tables_found'])}")
        if res["tables_missing"]:
            print(f"Tables Missing: {', '.join(res['tables_missing'])}")
        print(f"Views Found ({len(res['views_found'])}):  {', '.join(res['views_found'])}")
        if res["views_missing"]:
            print(f"Views Missing:  {', '.join(res['views_missing'])}")
        print("==================================================")

    elif args.command == "info":
        counts = schema.get_table_counts()
        print("==================================================")
        print("           TABLE RECORD INVENTORY                 ")
        print("==================================================")
        for tbl, cnt in counts.items():
            print(f"  - {tbl:<22}: {cnt:>4} records")
        print("==================================================")

    elif args.command == "stats":
        rows = db.fetch_all("SELECT * FROM vw_department_performance")
        print("==================================================")
        print("           DEPARTMENT PERFORMANCE METRICS         ")
        print("==================================================")
        for r in rows:
            print(f"[{r['dept_code']}] {r['department_name']} ({r['building']})")
            print(f"     Professors: {r['total_professors']} | Courses: {r['total_courses']} | Enrollments: {r['total_enrollments']} | Avg GPA: {r['department_avg_gpa']}")
        print("==================================================")

    elif args.command == "transcript":
        records = service.get_student_transcript(args.student)
        if not records:
            print(f"No academic transcript records found for student ID {args.student}.")
            return
        header = records[0]
        print("==================================================")
        print(f"ACADEMIC TRANSCRIPT: {header['student_name']} ({header['student_number']})")
        print(f"Cumulative GPA: {header['cumulative_gpa']}")
        print("==================================================")
        for rec in records:
            score_str = f"{rec['score']:.1f}" if rec['score'] is not None else "N/A"
            grade_str = rec['grade_letter'] or "In Progress"
            pts_str = f"{rec['grade_points']:.2f}" if rec['grade_points'] is not None else "N/A"
            print(f"  - [{rec['course_code']}] {rec['course_title']:<32} | {rec['term']} | Grade: {grade_str:<3} | Pts: {pts_str} | Score: {score_str}")
        print("==================================================")

    elif args.command == "honor-roll":
        records = service.get_honor_roll()
        print("==================================================")
        print("          HONOR ROLL STUDENTS (GPA >= 3.50)       ")
        print("==================================================")
        for rec in records:
            print(f"  - {rec['student_number']} | {rec['student_name']:<20} | GPA: {rec['cumulative_gpa']:.2f} | Status: {rec['status']}")
        print("==================================================")

    elif args.command == "enroll":
        try:
            result = service.enroll_student(args.student, args.section)
            print(f"Enrollment Success: {result['message']} (Enrollment ID: {result['enrollment_id']})")
        except ValueError as e:
            print(f"Enrollment Error: {e}")
            sys.exit(1)

    elif args.command == "grade":
        try:
            result = service.assign_grade(args.enrollment, args.score)
            print("Grade Assigned Successfully:")
            print(f"  - Enrollment ID: {result['enrollment_id']}")
            print(f"  - Score:         {result['score']}")
            print(f"  - Letter Grade:  {result['letter_grade']}")
            print(f"  - Grade Points:  {result['grade_points']}")
            print(f"  - Student GPA:   {result['cumulative_gpa']}")
        except ValueError as e:
            print(f"Grading Error: {e}")
            sys.exit(1)

    elif args.command == "prerequisites":
        catalog = service.get_course_prerequisites(args.course)
        print("==================================================")
        print("           COURSE PREREQUISITES CATALOG           ")
        print("==================================================")
        if not catalog:
            print("No prerequisite requirements found.")
        for item in catalog:
            print(f"[{item['course_code']}] {item['course_title']}")
            print(f"     Requires: [{item['prerequisite_code']}] {item['prerequisite_title']} (Min Grade: {item['min_grade_letter']})")
        print("==================================================")

    elif args.command == "degree-audit":
        try:
            audit = service.audit_degree(args.student, args.degree)
            print("==================================================")
            print(f"DEGREE COMPLETION AUDIT: {audit['student_name']} ({audit['student_number']})")
            print(f"Degree Program: {audit['degree_title']} ({audit['degree_code']})")
            print("==================================================")
            print(f"Credits Completed: {audit['completed_credits']} / {audit['total_credits_required']} ({audit['progress_pct']}%)")
            print(f"Cumulative GPA:    {audit['cumulative_gpa']} (Minimum Required: {audit['min_gpa_required']})")
            print(f"Graduation Status: {audit['graduation_status']}")
            print("--------------------------------------------------")
            print(f"Satisfied Requirements ({len(audit['satisfied_courses'])}):")
            for c in audit["satisfied_courses"]:
                print(f"  [x] [{c['course_code']}] {c['title']} ({c['credits']} cr) - Grade: {c['grade_letter']}")
            if audit["missing_mandatory_courses"]:
                print(f"Pending Mandatory Requirements ({len(audit['missing_mandatory_courses'])}):")
                for c in audit["missing_mandatory_courses"]:
                    print(f"  [ ] [{c['course_code']}] {c['title']} ({c['credits']} cr)")
            print("==================================================")
        except ValueError as e:
            print(f"Degree Audit Error: {e}")
            sys.exit(1)

    elif args.command == "export-sql":
        schema.export_sql(args.output)
        print(f"Consolidated deployment SQL exported to: {args.output}")


if __name__ == "__main__":
    main()
