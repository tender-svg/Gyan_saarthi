from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "erp.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_: object) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    with open(BASE_DIR / "schema.sql", "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()
    db.close()


@app.route("/")
def dashboard():
    db = get_db()
    metrics = {
        "students": db.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "teachers": db.execute("SELECT COUNT(*) FROM teachers").fetchone()[0],
        "classes": db.execute("SELECT COUNT(*) FROM classes").fetchone()[0],
        "present_today": db.execute(
            "SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Present'",
            (str(date.today()),),
        ).fetchone()[0],
        "fees_collected": db.execute("SELECT COALESCE(SUM(amount_paid),0) FROM fee_payments").fetchone()[0],
    }

    recent_attendance = db.execute(
        """
        SELECT a.date, a.status, s.name AS student_name, c.name AS class_name
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        JOIN classes c ON c.id = a.class_id
        ORDER BY a.date DESC, a.id DESC
        LIMIT 10
        """
    ).fetchall()

    recent_fees = db.execute(
        """
        SELECT f.payment_date, f.amount_paid, s.name AS student_name
        FROM fee_payments f
        JOIN students s ON s.id = f.student_id
        ORDER BY f.payment_date DESC, f.id DESC
        LIMIT 10
        """
    ).fetchall()
    return render_template("dashboard.html", metrics=metrics, recent_attendance=recent_attendance, recent_fees=recent_fees)


@app.route("/students", methods=["GET", "POST"])
def students():
    db = get_db()
    if request.method == "POST":
        name = request.form["name"].strip()
        parent_name = request.form["parent_name"].strip()
        contact = request.form["contact"].strip()
        class_id = request.form["class_id"]
        if name and class_id:
            db.execute(
                "INSERT INTO students (name, parent_name, contact, class_id) VALUES (?, ?, ?, ?)",
                (name, parent_name, contact, class_id),
            )
            db.commit()
            flash("Student added successfully", "success")
        else:
            flash("Name and class are required", "error")
        return redirect(url_for("students"))

    student_rows = db.execute(
        """
        SELECT s.id, s.name, s.parent_name, s.contact, c.name as class_name
        FROM students s
        JOIN classes c ON c.id = s.class_id
        ORDER BY s.id DESC
        """
    ).fetchall()
    classes = db.execute("SELECT id, name FROM classes ORDER BY name").fetchall()
    return render_template("students.html", students=student_rows, classes=classes)


@app.route("/teachers", methods=["GET", "POST"])
def teachers():
    db = get_db()
    if request.method == "POST":
        name = request.form["name"].strip()
        subject = request.form["subject"].strip()
        phone = request.form["phone"].strip()
        if name:
            db.execute("INSERT INTO teachers (name, subject, phone) VALUES (?, ?, ?)", (name, subject, phone))
            db.commit()
            flash("Teacher added successfully", "success")
        else:
            flash("Teacher name is required", "error")
        return redirect(url_for("teachers"))

    teacher_rows = db.execute("SELECT * FROM teachers ORDER BY id DESC").fetchall()
    return render_template("teachers.html", teachers=teacher_rows)


@app.route("/classes", methods=["GET", "POST"])
def classes():
    db = get_db()
    if request.method == "POST":
        name = request.form["name"].strip()
        room_number = request.form["room_number"].strip()
        if name:
            db.execute("INSERT INTO classes (name, room_number) VALUES (?, ?)", (name, room_number))
            db.commit()
            flash("Class added successfully", "success")
        else:
            flash("Class name is required", "error")
        return redirect(url_for("classes"))

    class_rows = db.execute("SELECT * FROM classes ORDER BY id DESC").fetchall()
    return render_template("classes.html", classes=class_rows)


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    db = get_db()
    if request.method == "POST":
        student_id = request.form["student_id"]
        class_id = request.form["class_id"]
        status = request.form["status"]
        day = request.form["date"]

        db.execute(
            "INSERT INTO attendance (student_id, class_id, date, status) VALUES (?, ?, ?, ?)",
            (student_id, class_id, day, status),
        )
        db.commit()
        flash("Attendance marked", "success")
        return redirect(url_for("attendance"))

    students = db.execute("SELECT id, name FROM students ORDER BY name").fetchall()
    class_rows = db.execute("SELECT id, name FROM classes ORDER BY name").fetchall()
    attendance_rows = db.execute(
        """
        SELECT a.date, a.status, s.name as student_name, c.name as class_name
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        JOIN classes c ON c.id = a.class_id
        ORDER BY a.date DESC, a.id DESC
        """
    ).fetchall()
    return render_template("attendance.html", students=students, classes=class_rows, attendance_records=attendance_rows)


@app.route("/fees", methods=["GET", "POST"])
def fees():
    db = get_db()
    if request.method == "POST":
        student_id = request.form["student_id"]
        amount = request.form["amount_paid"]
        payment_date = request.form["payment_date"]
        mode = request.form["payment_mode"]

        db.execute(
            "INSERT INTO fee_payments (student_id, amount_paid, payment_date, payment_mode) VALUES (?, ?, ?, ?)",
            (student_id, amount, payment_date, mode),
        )
        db.commit()
        flash("Fee payment recorded", "success")
        return redirect(url_for("fees"))

    students = db.execute("SELECT id, name FROM students ORDER BY name").fetchall()
    fee_rows = db.execute(
        """
        SELECT f.payment_date, f.amount_paid, f.payment_mode, s.name as student_name
        FROM fee_payments f
        JOIN students s ON s.id = f.student_id
        ORDER BY f.payment_date DESC, f.id DESC
        """
    ).fetchall()
    return render_template("fees.html", students=students, fee_payments=fee_rows)


if __name__ == "__main__":
    if not DB_PATH.exists():
        init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
