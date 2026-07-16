

# Database for messages using raw sqlite3
import os
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from datetime import datetime

app = Flask(__name__) 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Loveson.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.secret_key = 'your_super_secret_session_key'

# 1. Define an absolute path for the messages database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MESSAGES_DB = os.path.join(BASE_DIR, 'Loveson_Messages.db')


# This pulls the URL directly from what you just pasted into Render
DATABASE_URL = os.environ.get("DATABASE_URL")

# Pass 'DATABASE_URL' into SQLAlchemy, Tortoise, or your psycopg2 connect function!

# Database for messages using raw sqlite3
def init_db():
    # 2. Use the absolute path here
    conn = sqlite3.connect(MESSAGES_DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        subject TEXT,  
        message TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ... (Keep your questions list, SQLAlchemy models, and other routes exactly the same) ...


questions = [
    {
        "question": "What is the capital of Nepal?",
        "options": ["Pokhara", "Kathmandu", "Butwal", "Janakpur"],
        "answer": "Kathmandu"
    },
    {
        "question": "HTML stands for?",
        "options": ["Hyper Text Markup Language", "High Text Machine Language", "Home Tool Markup Language", "Hyper Transfer Language"],
        "answer": "Hyper Text Markup Language"
    },
    {
        "question": "CSS is used for?",
        "options": ["Programming", "Database", "Styling Web Pages", "Networking"],
        "answer": "Styling Web Pages"
    },
    {
        "question": "Python is a?",
        "options": ["Programming Language", "Database", "Browser", "Operating System"],
        "answer": "Programming Language"
    },
    {
        "question": "2 + 8 = ?",
        "options": ["9", "10", "11", "12"],
        "answer": "10"
    }
]

db = SQLAlchemy(app)

class Loveson(db.Model):
    Sn = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'{self.Sn} - {self.title}'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    status = db.Column(db.String(20))
    date = db.Column(db.String(20))

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/todo', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        if title and desc:
            todo = Loveson(title=title, desc=desc)
            db.session.add(todo)
            db.session.commit()
    all_todo = Loveson.query.all()
    return render_template('ToDo.html', all_todo=all_todo)
 
@app.route('/product')
def product():
    return 'This shows ToDo list'
	
@app.route('/update/<int:Sn>', methods=['GET', 'POST'])
def update(Sn):
    todo = Loveson.query.get_or_404(Sn)
    if request.method == 'POST':
        todo.title = request.form['title']
        todo.desc = request.form['desc']
        db.session.commit()
        return redirect(url_for('home'))
		
    return render_template('update.html', todo=todo)
	
@app.route('/delete/<int:Sn>')
def delete(Sn):
    todo = Loveson.query.get_or_404(Sn)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('home'))
    
@app.route('/task')
def task():
    return render_template('Task.html')

@app.route("/attendance")
def center():
    students = Student.query.all()
    records = Attendance.query.order_by(Attendance.id.desc()).all()
    
    unique_dates = {record.date for record in records if record.date}
    total_days = len(unique_dates)
    total_presents = sum(1 for record in records if record.status == "Present")
    total_absents = sum(1 for record in records if record.status == "Absent")

    selected_student = request.args.get("selected_student")
    student_records = []
    attendance_rate = 0

    if selected_student:
        student_records = [r for r in records if r.student_name == selected_student]
        total_student_days = len(student_records)
        if total_student_days > 0:
            student_presents = sum(1 for r in student_records if r.status == "Present")
            attendance_rate = round((student_presents / total_student_days) * 100, 1)

    return render_template(
        'Attendance.html',
        students=students,
        records=records,
        total_days=total_days,
        total_presents=total_presents,
        total_absents=total_absents,
        selected_student=selected_student,
        student_records=student_records,
        attendance_rate=attendance_rate
    )
    
@app.route("/add_student", methods=["POST"])
def add_student():
    name = request.form.get("name")
    if name and name.strip():
        student = Student(name=name.strip())
        db.session.add(student)
        db.session.commit()
    return redirect(url_for('center'))

@app.route("/mark", methods=["POST"])
def mark():
    students = Student.query.all()
    today = datetime.now().strftime("%Y-%m-%d")

    for student in students:
        status = request.form.get(f"status_{student.id}")
        if status:
            attendance = Attendance(
                student_name=student.name,
                status=status,
                date=today
            )
            db.session.add(attendance)

    db.session.commit()
    return redirect(url_for('center'))
    
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        user_name = request.form.get('name')
        user_email = request.form.get('email')
        user_subject = request.form.get('subject')
        user_message = request.form.get('message')

        if user_name and user_email and user_subject and user_message:
            # 3. Use the absolute path here
            conn = sqlite3.connect(MESSAGES_DB)
            c = conn.cursor()
            c.execute(
                "INSERT INTO messages (name, email, subject, message) VALUES (?, ?, ?, ?)", 
                (user_name, user_email, user_subject, user_message)
            )
            conn.commit()
            conn.close()
            flash(f"Thank you, {user_name}! Your message has been sent successfully.")
        else:
            flash("Please fill out all fields.")
            
        return redirect(url_for('contact'))

    return render_template('Contact.html')
    
@app.route('/View_message')
def view_message():
    # 4. Use the absolute path here
    conn = sqlite3.connect(MESSAGES_DB)
    c = conn.cursor()
    c.execute('SELECT * FROM messages')
    data = c.fetchall()
    conn.close()
    return render_template('Message.html', Loveson_Messages=data)

@app.route('/quiz')
def quiz():
	return render_template('Quiz.html')

@app.route("/fun", methods=["GET", "POST"])
def fun():
    if "current" not in session or "score" not in session:
        session["current"] = 0
        session["score"] = 0

    current = session["current"]

    # End the quiz safely if out of bounds
    if current >= len(questions):
        final_score = session["score"]
        total_qs = len(questions)
        session.clear()
        return f"<h1>Quiz Finished!</h1><p>Your score: {final_score}/{total_qs}</p><a href='{url_for('fun')}'>Try Again</a>"

    if request.method == "POST":
        selected = request.form.get("answer")
        if selected == questions[current]["answer"]:
            session["score"] += 1

        session["current"] += 1
        return redirect(url_for("fun"))

    return render_template('Fun.html',
        finished=False,
        question=questions[current],
        qno=current,
        total=len(questions)
    )

@app.route("/restart", methods=["POST"])
def restart():
    session.clear()
    return redirect(url_for("fun"))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
