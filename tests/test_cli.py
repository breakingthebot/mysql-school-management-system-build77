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
    assert "mysql-school 1.0.0" in captured.out


def test_cli_verify(capsys):
    # Verify CLI verify subcommand
    with patch.object(sys, "argv", ["mysql-school", "--in-memory", "verify"]):
        main()
    captured = capsys.readouterr()
    assert "SCHEMA INTEGRITY VERIFICATION: PASS" in captured.out
    assert "Tables Found (8)" in captured.out
    assert "Views Found (4)" in captured.out


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
