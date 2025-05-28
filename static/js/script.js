document.addEventListener('DOMContentLoaded', function() {
    // Set current date
    const currentDate = new Date().toLocaleDateString();
    document.getElementById('current-date').textContent = currentDate;

    // Fetch students and populate table
    async function fetchStudents() {
        try {
            const response = await fetch('/get_students');
            const students = await response.json();
            
            // Debug: Log the response
            console.log('Students data:', students);
            
            // Check if we got an error response
            if (students.error) {
                console.error('Server error:', students.error);
                alert('Error: ' + students.error);
                return;
            }
            
            // Check if students array is empty
            if (!students || students.length === 0) {
                console.log('No students found in database');
                document.getElementById('student-list').innerHTML = '<tr><td colspan="4">No students found in database</td></tr>';
                return;
            }

            const studentList = document.getElementById('student-list');
            studentList.innerHTML = ''; // Clear any existing content
            
            students.forEach(student => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${student.id}</td>
                    <td>${student.name}</td>
                    <td>${student.class}</td>
                    <td>
                        <div class="attendance-buttons">
                            <button class="present-btn" onclick="markAttendance(${student.id}, 'present', this)">Present</button>
                            <button class="absent-btn" onclick="markAttendance(${student.id}, 'absent', this)">Absent</button>
                        </div>
                    </td>
                `;
                studentList.appendChild(row);
            });
        } catch (error) {
            console.error('Error fetching students:', error);
            document.getElementById('student-list').innerHTML = '<tr><td colspan="4">Error loading students. Please check console for details.</td></tr>';
        }
    }

    // Function to mark attendance
    window.markAttendance = async function(studentId, status, button) {
        try {
            const response = await fetch('/mark_attendance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    student_id: studentId,
                    status: status
                })
            });
            
            const data = await response.json();
            if (data.success) {
                // Disable both buttons in the row
                const row = button.closest('tr');
                const buttons = row.querySelectorAll('button');
                buttons.forEach(btn => btn.disabled = true);
                
                // Add visual feedback
                row.className = status === 'present' ? 'marked-present' : 'marked-absent';
                alert(`Attendance marked as ${status}`);
            } else {
                alert('Error marking attendance');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error marking attendance');
        }
    };

    // Load students when page loads
    fetchStudents();
});