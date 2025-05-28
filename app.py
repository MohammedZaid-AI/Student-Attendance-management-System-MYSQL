from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import requests

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # replace with your MySQL username
    'password': '821481',  # replace with your MySQL password
    'database': 'attendance_system'
}

def send_sms(phone_number, message):
    # You'll need to sign up for an SMS service like Twilio
    # This is a placeholder for SMS sending logic
    pass

def send_email(email, message):
    # Email configuration
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"
    
    msg = MIMEText(message)
    msg['Subject'] = 'Student Attendance Notification'
    msg['From'] = sender_email
    msg['To'] = email
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    student_id = data['student_id']
    status = data['status']
    date = datetime.now().date()
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Mark attendance
        cursor.execute("""
            INSERT INTO attendance (student_id, date, status)
            VALUES (%s, %s, %s)
        """, (student_id, date, status))
        
        # If absent, notify parents
        if status == 'absent':
            cursor.execute("""
                SELECT parent_phone, parent_email, first_name, last_name
                FROM students
                WHERE student_id = %s
            """, (student_id,))
            
            parent_data = cursor.fetchone()
            if parent_data:
                phone, email, first_name, last_name = parent_data
                message = f"Dear Parent, This is to inform you that {first_name} {last_name} was absent from school today ({date})."
                
                send_sms(phone, message)
                send_email(email, message)
        
        conn.commit()
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/get_students')

def get_students():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT student_id as id, CONCAT(first_name, ' ', last_name) as name, class FROM students")
        students = cursor.fetchall()
        
        return jsonify(students)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)