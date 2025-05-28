CREATE DATABASE attendance_system;
USE attendance_system;

CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    class VARCHAR(20),
    parent_phone VARCHAR(15),
    parent_email VARCHAR(100)
);

CREATE TABLE attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    date DATE,
    status ENUM('present', 'absent'),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

INSERT INTO students (first_name, last_name, class, parent_phone, parent_email) VALUES
('John', 'Doe', '10A', '1234567890', 'parent1@example.com'),
('Jane', 'Smith', '10A', '0987654321', 'parent2@example.com'),
('Emily', 'Johnson', '8C', '2345678901', 'parent3@example.com'),
('Michael', 'Brown', '10A', '3456789012', 'parent4@example.com'),
('Sarah', 'Davis', '7D', '4567890123', 'parent5@example.com'),
('Daniel', 'Wilson', '9A', '5678901234', 'parent6@example.com'),
('Olivia', 'Martinez', '8B', '6789012345', 'parent7@example.com'),
('James', 'Taylor', '7C', '7890123456', 'parent8@example.com'),
('Sophia', 'Anderson', '10B', '8901234567', 'parent9@example.com'),
('Ethan', 'Thomas', '9C', '9012345678', 'parent10@example.com'),
('Ava', 'Jackson', '8A', '0123456789', 'parent11@example.com');