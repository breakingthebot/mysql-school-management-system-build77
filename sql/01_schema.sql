-- sql/01_schema.sql
-- Production MySQL 8.0+ Schema for School Management System
-- Comprehensive Relational Tables, Constraints, and Audit Infrastructure

-- -------------------------------------------------------------
-- 1. Departments Table
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    building VARCHAR(100) NOT NULL,
    budget DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------------
-- 2. Professors Table
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS professors (
    professor_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    department_id INT NOT NULL,
    hire_date DATE NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    status ENUM('active', 'on_leave', 'retired') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_professor_department
        FOREIGN KEY (department_id)
        REFERENCES departments (department_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------------
-- 3. Students Table
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    student_number VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    enrollment_date DATE NOT NULL,
    status ENUM('active', 'probation', 'graduated', 'suspended') NOT NULL DEFAULT 'active',
    cumulative_gpa DECIMAL(3, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------------
-- 4. Courses Table
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    credits INT NOT NULL DEFAULT 3,
    department_id INT NOT NULL,
    max_capacity INT NOT NULL DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_course_department
        FOREIGN KEY (department_id)
        REFERENCES departments (department_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------------
-- 5. Course Sections Table
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS course_sections (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    professor_id INT NOT NULL,
    term VARCHAR(20) NOT NULL,
    academic_year INT NOT NULL,
    room_number VARCHAR(30) NOT NULL,
    enrolled_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_section_course
        FOREIGN KEY (course_id)
        REFERENCES courses (course_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_section_professor
        FOREIGN KEY (professor_id)
        REFERENCES professors (professor_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT uq_section_course_term
        UNIQUE (course_id, term, academic_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------------
-- 6. Grade Scale Reference Table
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS grade_scale (
    letter_grade VARCHAR(2) PRIMARY KEY,
    min_score DECIMAL(5, 2) NOT NULL,
    max_score DECIMAL(5, 2) NOT NULL,
    grade_points DECIMAL(3, 2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------------
-- 7. Enrollments Table
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    section_id INT NOT NULL,
    student_id INT NOT NULL,
    enrollment_date DATE NOT NULL,
    status ENUM('enrolled', 'dropped', 'completed') NOT NULL DEFAULT 'enrolled',
    score DECIMAL(5, 2) DEFAULT NULL,
    grade_letter VARCHAR(2) DEFAULT NULL,
    grade_points DECIMAL(3, 2) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_enrollment_section
        FOREIGN KEY (section_id)
        REFERENCES course_sections (section_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_enrollment_student
        FOREIGN KEY (student_id)
        REFERENCES students (student_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_enrollment_grade
        FOREIGN KEY (grade_letter)
        REFERENCES grade_scale (letter_grade)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT uq_student_section
        UNIQUE (section_id, student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------------
-- 8. Academic Audit Log Table
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS academic_audit_log (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INT NOT NULL,
    action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    field_name VARCHAR(50) DEFAULT NULL,
    old_value TEXT DEFAULT NULL,
    new_value TEXT DEFAULT NULL,
    performed_by VARCHAR(50) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------------
-- 9. Optimization Indexes
-- -------------------------------------------------------------
CREATE INDEX idx_student_status ON students (status);
CREATE INDEX idx_student_gpa ON students (cumulative_gpa);
CREATE INDEX idx_course_dept ON courses (department_id);
CREATE INDEX idx_section_term ON course_sections (term, academic_year);
CREATE INDEX idx_enrollment_status ON enrollments (status);
CREATE INDEX idx_audit_table_record ON academic_audit_log (table_name, record_id);
