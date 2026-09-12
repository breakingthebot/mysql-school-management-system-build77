-- sql/02_procedures_triggers.sql
-- Stored Procedures and Triggers for School Management System
-- Enforcing Academic Integrity, Capacity Constraints, and Automated GPA Calculations

DELIMITER //

-- -------------------------------------------------------------
-- 1. Trigger: Enforce Section Capacity Before Enrollment
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_check_section_capacity //
CREATE TRIGGER trg_check_section_capacity
BEFORE INSERT ON enrollments
FOR EACH ROW
BEGIN
    DECLARE current_count INT DEFAULT 0;
    DECLARE capacity INT DEFAULT 0;

    SELECT enrolled_count INTO current_count
    FROM course_sections
    WHERE section_id = NEW.section_id;

    SELECT c.max_capacity INTO capacity
    FROM course_sections cs
    JOIN courses c ON cs.course_id = c.course_id
    WHERE cs.section_id = NEW.section_id;

    IF current_count >= capacity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Section has reached maximum student capacity';
    END IF;
END //

-- -------------------------------------------------------------
-- 2. Trigger: Increment Enrolled Count on Section
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_increment_enrolled_count //
CREATE TRIGGER trg_increment_enrolled_count
AFTER INSERT ON enrollments
FOR EACH ROW
BEGIN
    UPDATE course_sections
    SET enrolled_count = enrolled_count + 1
    WHERE section_id = NEW.section_id;
END //

-- -------------------------------------------------------------
-- 3. Trigger: Decrement Enrolled Count on Section
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_decrement_enrolled_count //
CREATE TRIGGER trg_decrement_enrolled_count
AFTER DELETE ON enrollments
FOR EACH ROW
BEGIN
    UPDATE course_sections
    SET enrolled_count = GREATEST(0, enrolled_count - 1)
    WHERE section_id = OLD.section_id;
END //

-- -------------------------------------------------------------
-- 4. Trigger: Audit Log Grade Changes
-- -------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_audit_grade_change //
CREATE TRIGGER trg_audit_grade_change
AFTER UPDATE ON enrollments
FOR EACH ROW
BEGIN
    IF (OLD.grade_letter <=> NEW.grade_letter) = 0 THEN
        INSERT INTO academic_audit_log (
            table_name,
            record_id,
            action,
            field_name,
            old_value,
            new_value,
            performed_by
        ) VALUES (
            'enrollments',
            NEW.enrollment_id,
            'UPDATE',
            'grade_letter',
            OLD.grade_letter,
            NEW.grade_letter,
            'system_grade_trigger'
        );
    END IF;
END //

-- -------------------------------------------------------------
-- 5. Stored Procedure: Enroll Student in Section
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_enroll_student //
CREATE PROCEDURE sp_enroll_student(
    IN p_student_id INT,
    IN p_section_id INT,
    OUT p_enrollment_id INT,
    OUT p_message VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_student_status VARCHAR(20);
    DECLARE v_existing_count INT DEFAULT 0;

    -- Verify student exists and is active
    SELECT status INTO v_student_status
    FROM students
    WHERE student_id = p_student_id;

    IF v_student_status IS NULL THEN
        SET p_enrollment_id = -1;
        SET p_message = 'Error: Student does not exist';
        LEAVE proc_label;
    END IF;

    IF v_student_status != 'active' THEN
        SET p_enrollment_id = -1;
        SET p_message = CONCAT('Error: Student status is ', v_student_status, ' (must be active)');
        LEAVE proc_label;
    END IF;

    -- Check if student already enrolled in section
    SELECT COUNT(*) INTO v_existing_count
    FROM enrollments
    WHERE student_id = p_student_id AND section_id = p_section_id;

    IF v_existing_count > 0 THEN
        SET p_enrollment_id = -1;
        SET p_message = 'Error: Student is already enrolled in this section';
        LEAVE proc_label;
    END IF;

    -- Insert enrollment (capacity checked by before insert trigger)
    INSERT INTO enrollments (section_id, student_id, enrollment_date, status)
    VALUES (p_section_id, p_student_id, CURDATE(), 'enrolled');

    SET p_enrollment_id = LAST_INSERT_ID();
    SET p_message = 'Success: Student enrolled successfully';
END //

-- -------------------------------------------------------------
-- 6. Stored Procedure: Calculate and Update Student Cumulative GPA
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_calculate_student_gpa //
CREATE PROCEDURE sp_calculate_student_gpa(
    IN p_student_id INT,
    OUT p_calculated_gpa DECIMAL(3, 2)
)
BEGIN
    DECLARE v_total_points DECIMAL(10, 2) DEFAULT 0.00;
    DECLARE v_total_credits INT DEFAULT 0;

    SELECT
        COALESCE(SUM(e.grade_points * c.credits), 0.00),
        COALESCE(SUM(c.credits), 0)
    INTO v_total_points, v_total_credits
    FROM enrollments e
    JOIN course_sections cs ON e.section_id = cs.section_id
    JOIN courses c ON cs.course_id = c.course_id
    WHERE e.student_id = p_student_id
      AND e.status = 'completed'
      AND e.grade_points IS NOT NULL;

    IF v_total_credits > 0 THEN
        SET p_calculated_gpa = ROUND(v_total_points / v_total_credits, 2);
    ELSE
        SET p_calculated_gpa = 0.00;
    END IF;

    UPDATE students
    SET cumulative_gpa = p_calculated_gpa
    WHERE student_id = p_student_id;
END //

-- -------------------------------------------------------------
-- 7. Stored Procedure: Assign Grade and Recalculate GPA
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_assign_grade //
CREATE PROCEDURE sp_assign_grade(
    IN p_enrollment_id INT,
    IN p_score DECIMAL(5, 2),
    OUT p_letter_grade VARCHAR(2),
    OUT p_grade_points DECIMAL(3, 2),
    OUT p_new_gpa DECIMAL(3, 2)
)
BEGIN
    DECLARE v_student_id INT;

    -- Resolve score to letter grade and grade points
    SELECT letter_grade, grade_points
    INTO p_letter_grade, p_grade_points
    FROM grade_scale
    WHERE p_score >= min_score AND p_score <= max_score
    LIMIT 1;

    -- Update enrollment record
    UPDATE enrollments
    SET score = p_score,
        grade_letter = p_letter_grade,
        grade_points = p_grade_points,
        status = 'completed'
    WHERE enrollment_id = p_enrollment_id;

    -- Find student ID to recalculate GPA
    SELECT student_id INTO v_student_id
    FROM enrollments
    WHERE enrollment_id = p_enrollment_id;

    CALL sp_calculate_student_gpa(v_student_id, p_new_gpa);
END //

DELIMITER ;
