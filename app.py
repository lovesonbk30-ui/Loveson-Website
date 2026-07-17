import os
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)
from flask_sqlalchemy import SQLAlchemy

# --------------------------------------------------
# Flask App
# --------------------------------------------------

app = Flask(__name__)
app.secret_key = "your_super_secret_session_key"

# --------------------------------------------------
# Database Configuration
# Uses PostgreSQL on Render/Neon
# Falls back to SQLite locally
# --------------------------------------------------

db_url = os.environ.get("DATABASE_URL")

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///Loveson.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --------------------------------------------------
# Database Models
# --------------------------------------------------

class Loveson(db.Model):
    __tablename__ = "todos"

    Sn = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.Sn} - {self.title}"


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --------------------------------------------------
# Quiz Questions
# --------------------------------------------------

questions = [
    {
        "question": "What is the capital of Nepal?",
        "options": [
            "Pokhara",
            "Kathmandu",
            "Butwal",
            "Janakpur"
        ],
        "answer": "Kathmandu"
    },
    {
        "question": "HTML stands for?",
        "options": [
            "Hyper Text Markup Language",
            "High Text Machine Language",
            "Home Tool Markup Language",
            "Hyper Transfer Language"
        ],
        "answer": "Hyper Text Markup Language"
    },
    {
        "question": "CSS is used for?",
        "options": [
            "Programming",
            "Database",
            "Styling Web Pages",
            "Networking"
        ],
        "answer": "Styling Web Pages"
    },
    {
        "question": "Python is a?",
        "options": [
            "Programming Language",
            "Database",
            "Browser",
            "Operating System"
        ],
        "answer": "Programming Language"
    },
    {
        "question": "2 + 8 = ?",
        "options": [
            "9",
            "10",
            "11",
            "12"
        ],
        "answer": "10"
    }
]
# ==================================================
# MAIN PAGE
# ==================================================

@app.route("/")
def main():
    return render_template("index.html")


# ==================================================
# TODO LIST
# ==================================================

@app.route("/todo", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        title = request.form.get("title")
        desc = request.form.get("desc")

        if title and desc:
            todo = Loveson(
                title=title,
                desc=desc
            )

            db.session.add(todo)
            db.session.commit()

            flash("Task Added Successfully!", "success")

        return redirect(url_for("home"))

    all_todo = Loveson.query.order_by(Loveson.Sn.desc()).all()

    return render_template(
        "ToDo.html",
        all_todo=all_todo
    )


@app.route("/product")
def product():
    return "This shows ToDo List"


@app.route("/update/<int:Sn>", methods=["GET", "POST"])
def update(Sn):

    todo = Loveson.query.get_or_404(Sn)

    if request.method == "POST":

        todo.title = request.form.get("title")
        todo.desc = request.form.get("desc")

        db.session.commit()

        flash("Task Updated Successfully!", "success")

        return redirect(url_for("home"))

    return render_template(
        "update.html",
        todo=todo
    )


@app.route("/delete/<int:Sn>")
def delete(Sn):

    todo = Loveson.query.get_or_404(Sn)

    db.session.delete(todo)
    db.session.commit()

    flash("Task Deleted Successfully!", "success")

    return redirect(url_for("home"))


# ==================================================
# TASK PAGE
# ==================================================

@app.route("/task")
def task():
    return render_template("Task.html")


# ==================================================
# ATTENDANCE
# ==================================================

@app.route("/attendance")
def center():

    students = Student.query.order_by(Student.name).all()

    records = Attendance.query.order_by(
        Attendance.id.desc()
    ).all()

    unique_dates = set()

    for record in records:
        unique_dates.add(record.date)

    total_days = len(unique_dates)

    total_presents = Attendance.query.filter_by(
        status="Present"
    ).count()

    total_absents = Attendance.query.filter_by(
        status="Absent"
    ).count()

    selected_student = request.args.get(
        "selected_student"
    )

    student_records = []

    attendance_rate = 0

    if selected_student:

        student_records = Attendance.query.filter_by(
            student_name=selected_student
        ).all()

        total_student_days = len(student_records)

        if total_student_days > 0:

            present_days = 0

            for record in student_records:

                if record.status == "Present":
                    present_days += 1

            attendance_rate = round(
                (present_days / total_student_days) * 100,
                1
            )

    return render_template(

        "Attendance.html",

        students=students,

        records=records,

        total_days=total_days,

        total_presents=total_presents,

        total_absents=total_absents,

        selected_student=selected_student,

        student_records=student_records,

        attendance_rate=attendance_rate

    )


# ==================================================
# ADD STUDENT
# ==================================================

@app.route("/add_student", methods=["POST"])
def add_student():

    name = request.form.get("name")

    if name:

        student = Student(
            name=name.strip()
        )

        db.session.add(student)
        db.session.commit()

        flash("Student Added!", "success")

    return redirect(url_for("center"))


# ==================================================
# MARK ATTENDANCE
# ==================================================

@app.route("/mark", methods=["POST"])
def mark():

    students = Student.query.all()

    today = datetime.now().strftime("%Y-%m-%d")

    for student in students:

        status = request.form.get(
            f"status_{student.id}"
        )

        if status:

            already = Attendance.query.filter_by(
                student_name=student.name,
                date=today
            ).first()

            if not already:

                db.session.add(

                    Attendance(

                        student_name=student.name,

                        status=status,

                        date=today

                    )

                )

    db.session.commit()

    flash("Attendance Saved!", "success")

    return redirect(url_for("center"))


# ==================================================
# CONTACT
# ==================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        message = Message(

            name=request.form.get("name"),

            email=request.form.get("email"),

            subject=request.form.get("subject"),

            message=request.form.get("message")

        )

        db.session.add(message)

        db.session.commit()

        flash(
            "Your message has been sent successfully!",
            "success"
        )

        return redirect(url_for("contact"))

    return render_template(
        "Contact.html"
    )


# ==================================================
# VIEW MESSAGES
# ==================================================

@app.route("/View_message")
def view_message():

    messages = Message.query.order_by(
        Message.id.desc()
    ).all()

    return render_template(

        "Message.html",

        Loveson_Messages=messages

    )


# ==================================================
# QUIZ PAGE
# ==================================================

@app.route("/quiz")
def quiz():
    return render_template("Quiz.html")
# ==================================================
# QUIZ GAME
# ==================================================

@app.route("/fun", methods=["GET", "POST"])
def fun():

    if "current" not in session:
        session["current"] = 0

    if "score" not in session:
        session["score"] = 0

    current = session["current"]

    # Quiz Finished
    if current >= len(questions):

        final_score = session["score"]
        total_questions = len(questions)

        session.clear()

        return f"""
        <html>
        <head>
            <title>Quiz Result</title>
            <style>
                body {{
                    font-family: Arial;
                    text-align: center;
                    margin-top: 80px;
                    background: #f5f5f5;
                }}
                h1 {{
                    color: green;
                }}
                a {{
                    text-decoration: none;
                    background: orange;
                    color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                }}
            </style>
        </head>
        <body>
            <h1>Quiz Finished!</h1>
            <h2>Your Score: {final_score}/{total_questions}</h2>
            <br>
            <a href="/fun">Play Again</a>
        </body>
        </html>
        """

    if request.method == "POST":

        selected = request.form.get("answer")

        if selected == questions[current]["answer"]:
            session["score"] += 1

        session["current"] += 1

        return redirect(url_for("fun"))

    return render_template(
        "Fun.html",
        question=questions[current],
        qno=current + 1,
        total=len(questions)
    )


# ==================================================
# RESTART QUIZ
# ==================================================

@app.route("/restart", methods=["POST"])
def restart():

    session.clear()

    return redirect(url_for("fun"))


# ==================================================
# CREATE DATABASE
# ==================================================

with app.app_context():
    db.create_all()


# ==================================================
# START APP
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )

