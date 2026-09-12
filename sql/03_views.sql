-- sql/03_views.sql
-- Analytical and Reporting Views for School Management System
-- Provides Denormalized Reporting Across Students, Courses, and Departments

-- -------------------------------------------------------------
-- 1. View: Course Enrollment Statistics & Capacity Utilization
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_course_enrollment_stats AS
SELECT
    c.course_code,
    c.title AS course_title,
    d.name AS department_name,
    cs.term,
    cs.academic_year,
    CONCAT(p.first_name, ' ', p.last_name) AS professor_name,
    cs.enrolled_count,
    c.max_capacity,
    ROUND((cs.enrolled_count / c.max_capacity) * 100, 1) AS capacity_utilization_pct,
    CASE
        WHEN cs.enrolled_count >= c.max_capacity THEN 'FULL'
        WHEN cs.enrolled_count >= (c.max_capacity * 0.8) THEN 'NEAR CAPACITY'
        ELSE 'OPEN'
    END AS enrollment_status
FROM course_sections cs
JOIN courses c ON cs.course_id = c.course_id
JOIN departments d ON c.department_id = d.department_id
JOIN professors p ON cs.professor_id = p.professor_id;

-- -------------------------------------------------------------
-- 2. View: Comprehensive Student Academic Transcript
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_student_transcript AS
SELECT
    s.student_id,
    s.student_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.cumulative_gpa,
    c.course_code,
    c.title AS course_title,
    c.credits,
    cs.term,
    cs.academic_year,
    e.status AS enrollment_status,
    e.score,
    e.grade_letter,
    e.grade_points
FROM enrollments e
JOIN students s ON e.student_id = s.student_id
JOIN course_sections cs ON e.section_id = cs.section_id
JOIN courses c ON cs.course_id = c.course_id;

-- -------------------------------------------------------------
-- 3. View: Department Performance & Metrics Summary
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_department_performance AS
SELECT
    d.department_id,
    d.dept_code,
    d.name AS department_name,
    d.building,
    COUNT(DISTINCT p.professor_id) AS total_professors,
    COUNT(DISTINCT c.course_id) AS total_courses,
    COUNT(DISTINCT e.enrollment_id) AS total_enrollments,
    COALESCE(ROUND(AVG(e.grade_points), 2), 0.00) AS department_avg_gpa
FROM departments d
LEFT JOIN professors p ON d.department_id = p.department_id
LEFT JOIN courses c ON d.department_id = c.department_id
LEFT JOIN course_sections cs ON c.course_id = cs.course_id
LEFT JOIN enrollments e ON cs.section_id = e.section_id
GROUP BY d.department_id, d.dept_code, d.name, d.building;

-- -------------------------------------------------------------
-- 4. View: Honor Roll Students (GPA >= 3.50)
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_honor_roll AS
SELECT
    s.student_id,
    s.student_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.email,
    s.cumulative_gpa,
    s.status
FROM students s
WHERE s.cumulative_gpa >= 3.50
  AND s.status = 'active';

-- -------------------------------------------------------------
-- 5. View: Course Prerequisites Catalog
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_course_prerequisites AS
SELECT
    c.course_id,
    c.course_code,
    c.title AS course_title,
    req_c.course_id AS prerequisite_course_id,
    req_c.course_code AS prerequisite_code,
    req_c.title AS prerequisite_title,
    cp.min_grade_letter,
    cp.min_grade_points
FROM course_prerequisites cp
JOIN courses c ON cp.course_id = c.course_id
JOIN courses req_c ON cp.prerequisite_course_id = req_c.course_id;

-- -------------------------------------------------------------
-- 6. View: Student Degree Audit Progress
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_degree_progress AS
SELECT
    sd.declaration_id,
    s.student_id,
    s.student_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    dp.degree_id,
    dp.degree_code,
    dp.title AS degree_title,
    dp.total_credits_required,
    COALESCE(SUM(CASE WHEN e.status = 'completed' AND e.grade_points >= 1.0 THEN c.credits ELSE 0 END), 0) AS completed_credits,
    ROUND((COALESCE(SUM(CASE WHEN e.status = 'completed' AND e.grade_points >= 1.0 THEN c.credits ELSE 0 END), 0) * 100.0) / dp.total_credits_required, 1) AS credit_completion_pct,
    s.cumulative_gpa,
    dp.min_gpa_required,
    CASE
        WHEN COALESCE(SUM(CASE WHEN e.status = 'completed' AND e.grade_points >= 1.0 THEN c.credits ELSE 0 END), 0) >= dp.total_credits_required
         AND s.cumulative_gpa >= dp.min_gpa_required THEN 'ELIGIBLE'
        ELSE 'PENDING'
    END AS graduation_status
FROM student_degrees sd
JOIN students s ON sd.student_id = s.student_id
JOIN degree_programs dp ON sd.degree_id = dp.degree_id
LEFT JOIN enrollments e ON s.student_id = e.student_id
LEFT JOIN course_sections cs ON e.section_id = cs.section_id
LEFT JOIN courses c ON cs.course_id = c.course_id
GROUP BY sd.declaration_id, s.student_id, s.student_number, s.first_name, s.last_name, dp.degree_id, dp.degree_code, dp.title, dp.total_credits_required, s.cumulative_gpa, dp.min_gpa_required;

-- -------------------------------------------------------------
-- 7. View: Classroom Scheduling Utilization
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_classroom_utilization AS
SELECT
    cl.room_id,
    cl.building,
    cl.room_number,
    cl.room_number AS classroom_code,
    cl.seating_capacity AS room_capacity,
    cl.seating_capacity,
    cl.room_type,
    COUNT(ss.schedule_id) AS scheduled_sections,
    COUNT(ss.schedule_id) AS total_scheduled_blocks,
    COALESCE(SUM(cs.enrolled_count), 0) AS total_students_seated,
    COALESCE(ROUND(SUM(TIME_TO_SEC(TIMEDIFF(ss.end_time, ss.start_time)) / 3600.0), 1), 0.0) AS total_weekly_hours
FROM classrooms cl
LEFT JOIN section_schedules ss ON cl.room_id = ss.room_id
LEFT JOIN course_sections cs ON ss.section_id = cs.section_id
GROUP BY cl.room_id, cl.building, cl.room_number, cl.seating_capacity, cl.room_type;

-- -------------------------------------------------------------
-- 8. View: Faculty Teaching Workload
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_faculty_workload AS
SELECT
    p.professor_id,
    CONCAT('EMP-', p.professor_id) AS employee_number,
    CONCAT(p.first_name, ' ', p.last_name) AS professor_name,
    CASE
        WHEN p.salary >= 120000 THEN 'Full Professor'
        WHEN p.salary >= 110000 THEN 'Associate Professor'
        ELSE 'Assistant Professor'
    END AS academic_rank,
    d.dept_code,
    d.dept_code AS department_code,
    d.name AS department_name,
    COUNT(DISTINCT cs.section_id) AS sections_teaching,
    COUNT(DISTINCT cs.section_id) AS total_sections_taught,
    COALESCE(SUM(c.credits), 0) AS total_teaching_credits,
    COALESCE(SUM(cs.enrolled_count), 0) AS total_students_taught,
    COALESCE(ROUND(SUM(TIME_TO_SEC(TIMEDIFF(ss.end_time, ss.start_time)) / 3600.0), 1), 0.0) AS weekly_instruction_hours,
    CASE
        WHEN COALESCE(SUM(c.credits), 0) >= 12 THEN 'Overload'
        WHEN COALESCE(SUM(c.credits), 0) >= 7 THEN 'Full'
        WHEN COALESCE(SUM(c.credits), 0) >= 4 THEN 'Standard'
        ELSE 'Light'
    END AS workload_status
FROM professors p
JOIN departments d ON p.department_id = d.department_id
LEFT JOIN course_sections cs ON p.professor_id = cs.professor_id
LEFT JOIN courses c ON cs.course_id = c.course_id
LEFT JOIN section_schedules ss ON cs.section_id = ss.section_id
GROUP BY p.professor_id, p.first_name, p.last_name, p.salary, d.dept_code, d.name;

-- -------------------------------------------------------------
-- 9. View: Master Course Section Timetable
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_master_timetable AS
SELECT
    ss.schedule_id,
    cs.term,
    cs.academic_year,
    c.course_code,
    c.title AS course_title,
    cs.section_id,
    cs.section_id AS section_number,
    cs.enrolled_count AS current_enrollment,
    c.max_capacity AS course_capacity,
    CONCAT(p.first_name, ' ', p.last_name) AS professor_name,
    cl.room_id,
    cl.building,
    cl.room_number,
    cl.room_number AS classroom_code,
    cl.seating_capacity AS room_capacity,
    cl.seating_capacity,
    ss.day_of_week,
    ss.start_time,
    ss.end_time
FROM section_schedules ss
JOIN course_sections cs ON ss.section_id = cs.section_id
JOIN courses c ON cs.course_id = c.course_id
JOIN professors p ON cs.professor_id = p.professor_id
JOIN classrooms cl ON ss.room_id = cl.room_id;


