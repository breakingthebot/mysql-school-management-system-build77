-- sql/04_seed.sql
-- Realistic Seed Dataset for School Management System
-- Populates Departments, Professors, Students, Courses, Sections, and Enrollments

-- -------------------------------------------------------------
-- 1. Populate Grade Scale
-- -------------------------------------------------------------
INSERT INTO grade_scale (letter_grade, min_score, max_score, grade_points) VALUES
('A',  93.00, 100.00, 4.00),
('A-', 90.00,  92.99, 3.70),
('B+', 87.00,  89.99, 3.30),
('B',  83.00,  86.99, 3.00),
('B-', 80.00,  82.99, 2.70),
('C+', 77.00,  79.99, 2.30),
('C',  73.00,  76.99, 2.00),
('D',  60.00,  72.99, 1.00),
('F',   0.00,  59.99, 0.00);

-- -------------------------------------------------------------
-- 2. Populate Departments
-- -------------------------------------------------------------
INSERT INTO departments (department_id, dept_code, name, building, budget) VALUES
(1, 'CS',   'Computer Science',        'Turing Hall',         750000.00),
(2, 'MATH', 'Mathematics',             'Euler Center',        520000.00),
(3, 'EE',   'Electrical Engineering',  'Franklin Laboratory', 680000.00),
(4, 'ENG',  'English & Literature',    'Shakespeare Hall',    380000.00),
(5, 'BUS',  'Business Administration', 'Smith Hall',          850000.00);

-- -------------------------------------------------------------
-- 3. Populate Professors
-- -------------------------------------------------------------
INSERT INTO professors (professor_id, first_name, last_name, email, department_id, hire_date, salary, status) VALUES
(1, 'Ada',     'Lovelace',  'alovelace@university.edu', 1, '2018-08-15', 115000.00, 'active'),
(2, 'Alan',    'Turing',    'aturing@university.edu',   1, '2016-01-10', 125000.00, 'active'),
(3, 'Carl',    'Gauss',     'cgauss@university.edu',    2, '2015-09-01', 118000.00, 'active'),
(4, 'Nikola',  'Tesla',     'ntesla@university.edu',    3, '2019-03-20', 112000.00, 'active'),
(5, 'Virginia','Woolf',     'vwoolf@university.edu',    4, '2020-08-15',  95000.00, 'active'),
(6, 'Adam',    'Smith',     'asmith@university.edu',    5, '2017-08-15', 120000.00, 'active');

-- -------------------------------------------------------------
-- 4. Populate Students
-- -------------------------------------------------------------
INSERT INTO students (student_id, student_number, first_name, last_name, email, date_of_birth, enrollment_date, status, cumulative_gpa) VALUES
(1,  'STU-1001', 'Maya',    'Lin',       'mlin@students.edu',       '2004-05-14', '2022-09-01', 'active', 3.85),
(2,  'STU-1002', 'Devon',   'Miller',    'dmiller@students.edu',    '2003-11-22', '2021-09-01', 'active', 3.60),
(3,  'STU-1003', 'Elena',   'Rostova',   'erostova@students.edu',   '2004-02-18', '2022-09-01', 'active', 3.92),
(4,  'STU-1004', 'Jordan',  'Bell',      'jbell@students.edu',      '2005-07-09', '2023-09-01', 'active', 2.80),
(5,  'STU-1005', 'Kenji',   'Sato',      'ksato@students.edu',      '2004-09-30', '2022-09-01', 'active', 3.75),
(6,  'STU-1006', 'Sofia',   'Carvalho',  'scarvalho@students.edu',  '2003-04-12', '2021-09-01', 'active', 3.40),
(7,  'STU-1007', 'Liam',    'OConnor',   'loconnor@students.edu',   '2004-12-05', '2022-09-01', 'active', 3.10),
(8,  'STU-1008', 'Aisha',   'Al-Mansoor','aalmansoor@students.edu', '2005-01-25', '2023-09-01', 'active', 3.90),
(9,  'STU-1009', 'Marcus',  'Vance',     'mvance@students.edu',     '2003-08-19', '2021-09-01', 'probation', 1.95),
(10, 'STU-1010', 'Chloe',   'Dupont',    'cdupont@students.edu',    '2002-10-11', '2020-09-01', 'graduated', 3.70);

-- -------------------------------------------------------------
-- 5. Populate Courses
-- -------------------------------------------------------------
INSERT INTO courses (course_id, course_code, title, description, credits, department_id, max_capacity) VALUES
(1, 'CS-101',   'Introduction to Computer Science', 'Foundations of programming, algorithms, and data structures', 4, 1, 35),
(2, 'CS-201',   'Data Structures & Algorithms',    'Trees, graphs, dynamic programming, and complexity analysis',    4, 1, 30),
(3, 'CS-301',   'Database Management Systems',     'Relational algebra, SQL, normalization, and ACID transactions',  3, 1, 25),
(4, 'MATH-150', 'Calculus I',                      'Differential and integral calculus with applications',           4, 2, 40),
(5, 'MATH-220', 'Linear Algebra',                  'Vector spaces, matrices, eigenvalues, and linear transformations',3, 2, 30),
(6, 'EE-110',   'Circuits & Digital Logic',        'Boolean algebra, logic gates, and circuit analysis',             4, 3, 25),
(7, 'ENG-102',  'Academic Writing & Literature',   'Critical analysis, research methodology, and essay composition', 3, 4, 20),
(8, 'BUS-200',  'Principles of Management',        'Organizational behavior, strategic planning, and leadership',    3, 5, 35);

-- -------------------------------------------------------------
-- 6. Populate Course Sections
-- -------------------------------------------------------------
INSERT INTO course_sections (section_id, course_id, professor_id, term, academic_year, room_number, enrolled_count) VALUES
(1, 1, 1, 'Fall',   2026, 'Turing-101',  4),
(2, 2, 2, 'Fall',   2026, 'Turing-202',  3),
(3, 3, 1, 'Fall',   2026, 'Turing-105',  3),
(4, 4, 3, 'Fall',   2026, 'Euler-301',   4),
(5, 5, 3, 'Spring', 2026, 'Euler-204',   2),
(6, 6, 4, 'Fall',   2026, 'Franklin-10', 2),
(7, 7, 5, 'Fall',   2026, 'Shakes-12',   2),
(8, 8, 6, 'Fall',   2026, 'Smith-40',    2);

-- -------------------------------------------------------------
-- 7. Populate Enrollments with Grades
-- -------------------------------------------------------------
INSERT INTO enrollments (enrollment_id, section_id, student_id, enrollment_date, status, score, grade_letter, grade_points) VALUES
(1,  1, 1, '2026-08-28', 'completed', 95.50, 'A',  4.00),
(2,  1, 2, '2026-08-28', 'completed', 88.00, 'B+', 3.30),
(3,  1, 3, '2026-08-29', 'completed', 97.00, 'A',  4.00),
(4,  1, 4, '2026-08-30', 'completed', 74.50, 'C',  2.00),
(5,  2, 1, '2026-08-28', 'completed', 92.00, 'A-', 3.70),
(6,  2, 3, '2026-08-29', 'completed', 94.00, 'A',  4.00),
(7,  2, 5, '2026-08-30', 'completed', 89.00, 'B+', 3.30),
(8,  3, 1, '2026-08-28', 'completed', 96.00, 'A',  4.00),
(9,  3, 5, '2026-08-29', 'completed', 91.50, 'A-', 3.70),
(10, 3, 8, '2026-08-30', 'completed', 98.00, 'A',  4.00),
(11, 4, 2, '2026-08-28', 'completed', 85.00, 'B',  3.00),
(12, 4, 4, '2026-08-28', 'completed', 78.00, 'C+', 2.30),
(13, 4, 6, '2026-08-29', 'completed', 86.50, 'B',  3.00),
(14, 4, 7, '2026-08-30', 'completed', 81.00, 'B-', 2.70),
(15, 5, 2, '2026-01-15', 'completed', 90.00, 'A-', 3.70),
(16, 5, 6, '2026-01-15', 'completed', 88.50, 'B+', 3.30),
(17, 6, 7, '2026-08-28', 'completed', 84.00, 'B',  3.00),
(18, 6, 9, '2026-08-29', 'completed', 62.00, 'D',  1.00),
(19, 7, 8, '2026-08-28', 'completed', 95.00, 'A',  4.00),
(20, 8, 10,'2026-08-28', 'completed', 91.00, 'A-', 3.70);

-- -------------------------------------------------------------
-- 8. Populate Course Prerequisites
-- -------------------------------------------------------------
INSERT INTO course_prerequisites (prerequisite_id, course_id, prerequisite_course_id, min_grade_letter, min_grade_points) VALUES
(1, 2, 1, 'C', 2.00),  -- CS-201 requires CS-101
(2, 3, 2, 'C', 2.00),  -- CS-301 requires CS-201
(3, 5, 4, 'C', 2.00);  -- MATH-220 requires MATH-150

-- -------------------------------------------------------------
-- 9. Populate Degree Programs
-- -------------------------------------------------------------
INSERT INTO degree_programs (degree_id, degree_code, title, department_id, total_credits_required, min_gpa_required) VALUES
(1, 'BS-CS',   'Bachelor of Science in Computer Science', 1, 120, 2.00),
(2, 'BS-MATH', 'Bachelor of Science in Mathematics',      2, 120, 2.00);

-- -------------------------------------------------------------
-- 10. Populate Degree Requirements
-- -------------------------------------------------------------
INSERT INTO degree_requirements (requirement_id, degree_id, course_id, is_mandatory) VALUES
(1, 1, 1, TRUE),  -- BS-CS requires CS-101
(2, 1, 2, TRUE),  -- BS-CS requires CS-201
(3, 1, 3, TRUE),  -- BS-CS requires CS-301
(4, 1, 4, TRUE),  -- BS-CS requires MATH-150
(5, 1, 5, TRUE),  -- BS-CS requires MATH-220
(6, 2, 4, TRUE),  -- BS-MATH requires MATH-150
(7, 2, 5, TRUE),  -- BS-MATH requires MATH-220
(8, 2, 1, TRUE);  -- BS-MATH requires CS-101

-- -------------------------------------------------------------
-- 11. Populate Student Degree Declarations
-- -------------------------------------------------------------
INSERT INTO student_degrees (declaration_id, student_id, degree_id, declaration_date, status) VALUES
(1, 1, 1, '2022-09-01', 'declared'),     -- Maya Lin: BS-CS
(2, 2, 2, '2021-09-01', 'declared'),     -- Devon Miller: BS-MATH
(3, 3, 1, '2022-09-01', 'declared');     -- Elena Rostova: BS-CS

-- -------------------------------------------------------------
-- 12. Populate Classrooms
-- -------------------------------------------------------------
INSERT INTO classrooms (room_id, building, room_number, seating_capacity, room_type) VALUES
(1, 'Turing Hall',         'Turing-101', 35, 'lecture_hall'),
(2, 'Turing Hall',         'Turing-202', 30, 'computer_lab'),
(3, 'Euler Center',        'Euler-301',  40, 'lecture_hall'),
(4, 'Franklin Laboratory', 'Franklin-10',25, 'laboratory'),
(5, 'Shakespeare Hall',    'Shakes-12',  20, 'seminar_room'),
(6, 'Smith Hall',          'Smith-40',   35, 'lecture_hall');

-- -------------------------------------------------------------
-- 13. Populate Section Schedules
-- -------------------------------------------------------------
INSERT INTO section_schedules (schedule_id, section_id, room_id, day_of_week, start_time, end_time) VALUES
(1,  1, 1, 'MON', '09:00:00', '10:30:00'),
(2,  1, 1, 'WED', '09:00:00', '10:30:00'),
(3,  2, 2, 'TUE', '10:00:00', '11:30:00'),
(4,  2, 2, 'THU', '10:00:00', '11:30:00'),
(5,  3, 2, 'MON', '13:00:00', '14:30:00'),
(6,  4, 3, 'MON', '10:00:00', '11:30:00'),
(7,  4, 3, 'WED', '10:00:00', '11:30:00'),
(8,  6, 4, 'FRI', '14:00:00', '17:00:00'),
(9,  7, 5, 'TUE', '13:00:00', '14:30:00'),
(10, 8, 6, 'THU', '13:00:00', '14:30:00');


