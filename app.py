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
