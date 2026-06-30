from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__) # configure the SQLite database, relative to the app instance folder 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Loveson.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
# Secret key is required to use 'flash' messages for user session alerts
app.secret_key = 'your_super_secret_session_key'

db = SQLAlchemy(app)

class Loveson(db.Model):
    Sn = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

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


# Define the homepage route
@app.route('/')
def main():
    all_todo = Loveson.query.all()
    print(all_todo)
    return render_template('index.html')

@app.route('/todo', methods=['GET', 'POST'])
def home():
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Loveson(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()
    all_todo = Loveson.query.all()
    return render_template('ToDo.html', all_todo=all_todo)
 
@app.route('/product')
def product():
    all_todo = Loveson.query.all()
    print(all_todo)
    return 'This shows ToDo list'
	
@app.route('/update/<int:Sn>', methods=['GET', 'POST'])
def update(Sn):
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Loveson.query.filter_by(Sn=Sn).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect('/todo')
		
    todo = Loveson.query.filter_by(Sn=Sn).first()
    return render_template('update.html', todo=todo)
	
@app.route('/delete/<int:Sn>')
def delete(Sn):
    todo = Loveson.query.filter_by(Sn=Sn).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect('/todo')
    
    
@app.route('/task')
def task():
	return  render_template('Task.html')

@app.route("/attendance")
def center():
    students = Student.query.all()
    records = Attendance.query.order_by(Attendance.id.desc()).all()
    
    # Global Stats calculations
    unique_dates = {record.date for record in records if record.date}
    total_days = len(unique_dates)
    total_presents = sum(1 for record in records if record.status == "Present")
    total_absents = sum(1 for record in records if record.status == "Absent")

    # Get individual student logic from GET parameters
    selected_student = request.args.get("selected_student")
    student_records = []
    attendance_rate = 0

    if selected_student:
        # Filter the global records list for the chosen student name
        student_records = [r for r in records if r.student_name == selected_student]
        
        # Calculate individual student metrics
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
    name = request.form["name"]
    if name.strip():
        student = Student(name=name)
        db.session.add(student)
        db.session.commit()
    return redirect("/attendance")

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
    return redirect("/attendance")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        user_name = request.form.get('name')
        user_email = request.form.get('email')
        email_subject = request.form.get('subject')
        user_message = request.form.get('message')

        print(f"--- NEW MESSAGE RECEIVED ---")
        print(f"From: {user_name} ({user_email})")
        print(f"Subject: {email_subject}")
        print(f"Message: {user_message}")
        print(f"----------------------------")

        flash(f"Thank you, {user_name}! Your message has been sent successfully.")
        return redirect(url_for('contact'))

    return render_template('Contact.html')

@app.route('/quiz')
def quiz():
	return render_template('Quiz.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
