# tests/test_scheduling_conflicts.py
# Unit Tests for Classroom Conflict Detection, Master Timetable, and Faculty Workload

import pytest
from school_db.db import DatabaseManager
from school_db.schema import SchemaManager
from school_db.service import AcademicService


@pytest.fixture
def service():
    # Provide initialized academic service with migrated and seeded schema
    db = DatabaseManager(in_memory=True)
    schema = SchemaManager(db=db, sql_dir="sql")
    schema.migrate()
    schema.seed()
    return AcademicService(db=db)


def test_classroom_double_booking_conflict(service):
    # Verify that scheduling two sections in the same room with overlapping time is blocked
    # In seed data: Section 1 is in Room 1 (Turing-101) on MON 09:00:00 - 10:30:00 (Fall 2026)
    # Attempting to schedule Section 3 in Room 1 on MON 09:30:00 - 11:00:00 must fail
    with pytest.raises(ValueError) as exc_info:
        service.schedule_section(
            section_id=3,
            classroom_id=1,
            day_of_week="MON",
            start_time="09:30:00",
            end_time="11:00:00",
        )
    assert "Classroom double-booking conflict" in str(exc_info.value)
    assert "Turing-101" in str(exc_info.value)


def test_professor_schedule_overlap_conflict(service):
    # Verify that scheduling a professor to teach two sections at the same time is blocked
    # In seed data: Professor 1 (Dr. Ada Lovelace) teaches Section 1 on MON 09:00:00 - 10:30:00 (Fall 2026)
    # Section 3 is also taught by Professor 1 (Dr. Ada Lovelace).
    # Room 6 is completely free on MON. Attempting to schedule Section 3 on MON 09:30:00 - 11:00:00 must fail
    with pytest.raises(ValueError) as exc_info:
        service.schedule_section(
            section_id=3,
            classroom_id=6,
            day_of_week="MON",
            start_time="09:30:00",
            end_time="11:00:00",
        )
    assert "Professor schedule overlap detected" in str(exc_info.value)
    assert "Ada Lovelace" in str(exc_info.value)


def test_room_capacity_insufficient_conflict(service):
    # Verify scheduling fails if classroom capacity is less than course section capacity
    # Room 5 (Shakespeare Hall, Shakes-12) has capacity 20
    # Section 1 has course capacity 35
    with pytest.raises(ValueError) as exc_info:
        service.schedule_section(
            section_id=1,
            classroom_id=5,
            day_of_week="FRI",
            start_time="14:00:00",
            end_time="16:00:00",
        )
    assert "smaller than section capacity" in str(exc_info.value)


def test_invalid_time_range_conflict(service):
    # Verify scheduling fails when end time is before or equal to start time
    with pytest.raises(ValueError) as exc_info:
        service.schedule_section(
            section_id=3,
            classroom_id=2,
            day_of_week="TUE",
            start_time="11:00:00",
            end_time="09:00:00",
        )
    assert "End time must be after start time" in str(exc_info.value)


def test_successful_section_scheduling(service):
    # Verify valid scheduling assignment succeeds and persists in timetable
    # Section 2 (CS-201 Sec 1, Capacity 30, Prof 2 Alan Turing)
    # Room 1 (Turing-101, Capacity 35) is free on FRI 10:00:00 - 11:30:00
    res = service.schedule_section(
        section_id=2,
        classroom_id=1,
        day_of_week="FRI",
        start_time="10:00:00",
        end_time="11:30:00",
    )
    assert res["schedule_id"] is not None
    assert res["classroom_code"] == "Turing-101"
    assert res["day_of_week"] == "FRI"
    assert res["start_time"] == "10:00:00"
    assert res["end_time"] == "11:30:00"

    # Verify presence in master timetable
    timetable = service.get_master_timetable(term="Fall", year=2026)
    matched = [
        t for t in timetable
        if t["classroom_code"] == "Turing-101"
        and t["day_of_week"] == "FRI"
        and t["start_time"] == "10:00:00"
    ]
    assert len(matched) == 1
    assert matched[0]["course_code"] == "CS-201"
    assert matched[0]["professor_name"] == "Alan Turing"


def test_classroom_utilization_view(service):
    # Verify vw_classroom_utilization returns expected metric aggregations
    utilization = service.get_classroom_utilization()
    assert len(utilization) == 6

    # Verify Turing-101 has scheduled sections
    tur_101 = next(r for r in utilization if r["classroom_code"] == "Turing-101")
    assert tur_101["room_capacity"] == 35
    assert tur_101["scheduled_sections"] >= 1
    assert tur_101["total_weekly_hours"] > 0.0


def test_faculty_workload_view(service):
    # Verify vw_faculty_workload returns workload indicators for professors
    workloads = service.get_faculty_workload()
    assert len(workloads) == 6

    # Verify Ada Lovelace's workload metrics
    lovelace = next(w for w in workloads if "Lovelace" in w["professor_name"])
    assert lovelace["sections_teaching"] >= 2
    assert lovelace["total_teaching_credits"] >= 7
    assert lovelace["workload_status"] in ["Light", "Standard", "Full", "Overload"]
