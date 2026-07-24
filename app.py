import os
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# --------------------------------------------------
# App & Database Configuration
# --------------------------------------------------
app = Flask(__name__)
app.secret_key = "your_super_secret_session_key"

# Uses Render/Neon PostgreSQL if present, otherwise defaults to local SQLite
db_url = os.environ.get("DATABASE_URL", "sqlite:///app.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --------------------------------------------------
# Database Models (Linked to Users via user_id)
# --------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.Text, nullable=False)   # ✅ Fix


class Loveson(db.Model):
    __tablename__ = "todos"
    Sn = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


# Dynamic Helper to get current logged-in user
def get_current_user():
    user_id = session.get('user_id')
    return User.query.get(user_id) if user_id else None

# --------------------------------------------------
# Quiz Data
# --------------------------------------------------
questions = [
    {"question": "What is the capital of Nepal?", "options": ["Pokhara", "Kathmandu", "Butwal", "Janakpur"], "answer": "Kathmandu"},
    {"question": "HTML stands for?", "options": ["Hyper Text Markup Language", "High Text Machine Language", "Home Tool Markup Language", "Hyper Transfer Language"], "answer": "Hyper Text Markup Language"},
    {"question": "CSS is used for?", "options": ["Programming", "Database", "Styling Web Pages", "Networking"], "answer": "Styling Web Pages"},
    {"question": "Python is a?", "options": ["Programming Language", "Database", "Browser", "Operating System"], "answer": "Programming Language"},
    {"question": "2 + 8 = ?", "options": ["9", "10", "11", "12"], "answer": "10"}
]

# ==================================================
# AUTHENTICATION
# ==================================================
@app.route("/")
def main():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username Already Taken', 'danger')
            return redirect(url_for('register'))

        user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        flash('Registration Successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('Register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login Successful!', 'success')
            return redirect(url_for('dashboard'))
            
        flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=user.username)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==================================================
# TODO LIST
# ==================================================
@app.route("/todo", methods=["GET", "POST"])
def home():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if request.method == "POST":
        title = request.form.get("title")
        desc = request.form.get("desc")
        if title and desc:
            db.session.add(Loveson(title=title, desc=desc, user_id=user.id))
            db.session.commit()
            flash("Task Added Successfully!", "success")
        return redirect(url_for("home"))

    all_todo = Loveson.query.filter_by(user_id=user.id).order_by(Loveson.Sn.desc()).all()
    return render_template("ToDo.html", all_todo=all_todo)


@app.route("/update/<int:Sn>", methods=["GET", "POST"])
def update(Sn):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    todo = Loveson.query.filter_by(Sn=Sn, user_id=user.id).first_or_404()
    if request.method == "POST":
        todo.title = request.form.get("title")
        todo.desc = request.form.get("desc")
        db.session.commit()
        flash("Task Updated Successfully!", "success")
        return redirect(url_for("home"))

    return render_template("update.html", todo=todo)


@app.route("/delete/<int:Sn>")
def delete(Sn):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    todo = Loveson.query.filter_by(Sn=Sn, user_id=user.id).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    flash("Task Deleted Successfully!", "success")
    return redirect(url_for("home"))

# ==================================================
# ATTENDANCE
# ==================================================
@app.route("/attendance")
def center():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    students = Student.query.filter_by(user_id=user.id).order_by(Student.name).all()
    records = Attendance.query.filter_by(user_id=user.id).order_by(Attendance.id.desc()).all()

    total_days = len({r.date for r in records})
    total_presents = Attendance.query.filter_by(user_id=user.id, status="Present").count()
    total_absents = Attendance.query.filter_by(user_id=user.id, status="Absent").count()

    selected_student = request.args.get("selected_student")
    student_records = []
    attendance_rate, student_presents, student_absents = 0, 0, 0

    if selected_student:
        student_records = Attendance.query.filter_by(user_id=user.id, student_name=selected_student).all()
        if student_records:
            student_presents = sum(1 for r in student_records if r.status == "Present")
            student_absents = sum(1 for r in student_records if r.status == "Absent")
            attendance_rate = round((student_presents / len(student_records)) * 100, 1)

    return render_template(
        "Attendance.html",
        students=students,
        records=records,
        total_days=total_days,
        total_presents=total_presents,
        total_absents=total_absents,
        selected_student=selected_student,
        student_records=student_records,
        attendance_rate=attendance_rate,
        student_presents=student_presents,
        student_absents=student_absents
    )


@app.route("/add_student", methods=["POST"])
def add_student():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    name = request.form.get("name")
    if name:
        db.session.add(Student(name=name.strip(), user_id=user.id))
        db.session.commit()
        flash("Student Added!", "success")
    return redirect(url_for("center"))


@app.route("/mark", methods=["POST"])
def mark():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    students = Student.query.filter_by(user_id=user.id).all()
    today = datetime.now().strftime("%Y-%m-%d")

    for student in students:
        status = request.form.get(f"status_{student.id}")
        if status:
            already = Attendance.query.filter_by(user_id=user.id, student_name=student.name, date=today).first()
            if not already:
                db.session.add(Attendance(student_name=student.name, status=status, date=today, user_id=user.id))

    db.session.commit()
    flash("Attendance Saved!", "success")
    return redirect(url_for("center"))

# ==================================================
# CONTACT MESSAGES
# ==================================================
@app.route("/contact", methods=["GET", "POST"])
def contact():
    
    

    if request.method == "POST":
        msg = Message(
            name=request.form.get("name"),
            email=request.form.get("email"),
            subject=request.form.get("subject"),
            message=request.form.get("message"),
            user_id=user.id
        )
        db.session.add(msg)
        db.session.commit()
        flash("Your message has been sent successfully!", "success")
        return redirect(url_for("contact"))

    return render_template("Contact.html")


@app.route("/View_message")
def view_message():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    messages = Message.query.filter_by(user_id=user.id).order_by(Message.id.desc()).all()
    return render_template("Message.html", Loveson_Messages=messages)

# ==================================================
# QUIZ GAME & MISC
# ==================================================
@app.route("/task")
def task():
    return render_template("Task.html")


@app.route("/quiz")
def quiz():
    return render_template("Quiz.html")


@app.route("/fun", methods=["GET", "POST"])
def fun():
    session.setdefault("current", 0)
    session.setdefault("score", 0)

    current = session["current"]

    if current >= len(questions):
        final_score = session.pop("score", 0)
        session.pop("current", None)
        return f"""
        <html>
        <head><title>Quiz Result</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 80px;">
            <h1 style="color: green;">Quiz Finished!</h1>
            <h2>Your Score: {final_score}/{len(questions)}</h2><br>
            <a href="/fun" style="background: orange; color: white; padding: 10px 15px; text-decoration: none;">Play Again</a>
        </body>
        </html>
        """

    if request.method == "POST":
        if request.form.get("answer") == questions[current]["answer"]:
            session["score"] += 1
        session["current"] += 1
        return redirect(url_for("fun"))

    return render_template("Fun.html", question=questions[current], qno=current + 1, total=len(questions))


@app.route("/restart", methods=["POST"])
def restart():
    session.pop("current", None)
    session.pop("score", None)
    return redirect(url_for("fun"))


# --------------------------------------------------
# Database Initialization & Startup
# --------------------------------------------------
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
