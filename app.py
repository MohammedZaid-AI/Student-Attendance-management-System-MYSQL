from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import mysql.connector
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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

# Only one index route with login required
@app.route('/')
@login_required
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

class Teacher(UserMixin):
    def __init__(self, id, email, first_name, last_name):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

@login_manager.user_loader
def load_user(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teachers WHERE teacher_id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user_data:
        return Teacher(
            id=user_data['teacher_id'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teachers WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        
        if user_data and check_password_hash(user_data['password'], password):
            # Update last login time
            current_time = datetime.now()
            cursor.execute("""
                UPDATE teachers 
                SET last_login = %s 
                WHERE teacher_id = %s
            """, (current_time, user_data['teacher_id']))
            
            # Record login in history table
            cursor.execute("""
                INSERT INTO teacher_logins (teacher_id)
                VALUES (%s)
            """, (user_data['teacher_id'],))
            
            conn.commit()
            
            user = Teacher(
                id=user_data['teacher_id'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid email or password')
        cursor.close()
        conn.close()
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        try:
            # Connect to database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Check if email already exists
            cursor.execute("SELECT * FROM teachers WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash('Email already registered. Please use a different email.')
                return render_template('signup.html')
            
            # Insert new teacher
            cursor.execute("""
                INSERT INTO teachers (email, password, first_name, last_name)
                VALUES (%s, %s, %s, %s)
            """, (email, hashed_password, first_name, last_name))
            
            # Get the new teacher's ID
            teacher_id = cursor.lastrowid
            
            # Commit changes
            conn.commit()
            
            # Create user object and log in
            user = Teacher(
                id=teacher_id,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            login_user(user)
            
            # Redirect to index page
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error creating account: {str(e)}')
            return render_template('signup.html')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    # GET request - show signup form
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)