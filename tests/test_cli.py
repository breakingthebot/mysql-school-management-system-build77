# tests/test_cli.py
# Unit Tests for Command-Line Interface Suite

import sys
from unittest.mock import patch
from school_db.cli import main


def test_cli_version(capsys):
    # Verify CLI --version output
    with patch.object(sys, "argv", ["mysql-school", "--version"]):
        try:
            main()
        except SystemExit:
            pass
    captured = capsys.readouterr()
    assert "mysql-school 1.2.0" in captured.out


def test_cli_verify(capsys):
    # Verify CLI verify subcommand
    with patch.object(sys, "argv", ["mysql-school", "--in-memory", "verify"]):
        main()
    captured = capsys.readouterr()
    assert "SCHEMA INTEGRITY VERIFICATION: PASS" in captured.out
    assert "Tables Found (14)" in captured.out
    assert "Views Found (9)" in captured.out


def test_cli_info(capsys):
    # Verify CLI info subcommand
    with patch.object(sys, "argv", ["mysql-school", "--in-memory", "info"]):
        main()
    captured = capsys.readouterr()
    assert "TABLE RECORD INVENTORY" in captured.out
    assert "departments" in captured.out
    assert "students" in captured.out


def test_cli_stats(capsys):
    # Verify CLI stats subcommand
    with patch.object(sys, "argv", ["mysql-school", "--in-memory", "stats"]):
        main()
    captured = capsys.readouterr()
    assert "DEPARTMENT PERFORMANCE METRICS" in captured.out
    assert "Computer Science" in captured.out


def test_cli_transcript(capsys):
    # Verify CLI transcript subcommand
    with patch.object(sys, "argv", ["mysql-school", "--in-memory", "transcript", "--student", "1"]):
        main()
    captured = capsys.readouterr()
    assert "ACADEMIC TRANSCRIPT: Maya Lin" in captured.out
    assert "Cumulative GPA: 3.85" in captured.out


def test_cli_honor_roll(capsys):
    # Verify CLI honor-roll subcommand
    with patch.object(sys, "argv", ["mysql-school", "--in-memory", "honor-roll"]):
        main()
    captured = capsys.readouterr()
    assert "HONOR ROLL STUDENTS (GPA >= 3.50)" in captured.out
    assert "Maya Lin" in captured.out


def test_cli_export_sql(capsys, tmp_path):
    # Verify CLI export-sql subcommand
    out_file = str(tmp_path / "cli_exported.sql")
    with patch.object(sys, "argv", ["mysql-school", "export-sql", "--output", out_file]):
        main()
    captured = capsys.readouterr()
    assert "Consolidated deployment SQL exported" in captured.out


def test_cli_rooms(capsys):
    # Verify CLI rooms subcommand displays classroom utilization
    with patch.object(sys, "argv", ["mysql-school", "--in-memory", "rooms"]):
        main()
    captured = capsys.readouterr()
    assert "CLASSROOM CAPACITY & UTILIZATION" in captured.out
    assert "Turing Hall" in captured.out


def test_cli_workload(capsys):
    # Verify CLI workload subcommand displays professor workload
    with patch.object(sys, "argv", ["mysql-school", "--in-memory", "workload"]):
        main()
    captured = capsys.readouterr()
    assert "FACULTY TEACHING WORKLOAD" in captured.out
    assert "Alan Turing" in captured.out


def test_cli_timetable(capsys):
    # Verify CLI timetable subcommand displays scheduled sections
    with patch.object(sys, "argv", ["mysql-school", "--in-memory", "timetable", "--term", "Fall"]):
        main()
    captured = capsys.readouterr()
    assert "MASTER CLASSROOM TIMETABLE" in captured.out
    assert "CS-101" in captured.out


def test_cli_schedule_success(capsys):
    # Verify CLI schedule subcommand successfully schedules a section
    with patch.object(
        sys,
        "argv",
        [
            "mysql-school",
            "--in-memory",
            "schedule",
            "--section",
            "4",
            "--room",
            "3",
            "--day",
            "FRI",
            "--start",
            "14:00:00",
            "--end",
            "16:00:00",
        ],
    ):
        main()
    captured = capsys.readouterr()
    assert "Scheduling Assignment Succeeded" in captured.out
    assert "FRI 14:00:00 to 16:00:00" in captured.out
