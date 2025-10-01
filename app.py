import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from sqlalchemy import inspect
from config import DB_URI, SECRET_KEY, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD
from models import db, Admin, Student
from risk_engine import evaluate_risks
from reports import generate_csv_report
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SECRET_KEY"] = SECRET_KEY
app.config["UPLOAD_FOLDER"] = "uploads"
db.init_app(app)

def create_tables_and_seed():
    with app.app_context():
        # This will force the database to be reset on every startup, ensuring fresh data.
        logging.info("Forcing a full database reset to load all required columns...")
        db.drop_all() 
        db.create_all()

        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            os.makedirs(app.config["UPLOAD_FOLDER"])
        if not Admin.query.first():
            db.session.add(Admin(email="admin@test.com", password="admin"))
            db.session.commit()
            logging.info("Admin user seeded.")
        try:
            df = pd.read_csv("student_risk_dataset_precise.csv")
            logging.info(f"CSV loaded. Seeding {len(df)} students...")
            
            # Clean data before loading
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].fillna('')
            for col in df.select_dtypes(include=['number']).columns:
                df[col] = df[col].fillna(0)

            # This constructor is now complete and matches the model and predictor.
            for _, row in df.iterrows():
                student = Student(
                    student_id=row["Student_ID"], name=row["Student_Name"], email=row["Email_ID"], password=row["Student_ID"],
                    attendance=row["Avg_Attendance"], marks=row["Avg_Performance"], fee_status=row["Fee_Status"],
                    Age=row["Age"], Gender=row["Gender"], Year_of_Study=row["Year_of_Study"],
                    Parent_Annual_Income=row["Parent_Annual_Income"], Scholarship_Status=row["Scholarship_Status"],
                    Loan_Status=row["Loan_Status"], Chronic_Health_Issue=row["Chronic_Health_Issue"],
                    Health_Issue_Type=row["Health_Issue_Type"], Total_Leaves=row["Total_Leaves"],
                    Counseling_Sessions_Attended=row["Counseling_Sessions_Attended"],
                    Disciplinary_Actions=row["Disciplinary_Actions"], Class_Participation=row["Class_Participation"],
                    Extracurricular_Activities_Score=row["Extracurricular_Activities_Score"],
                    LMS_Logins_Per_Week=row["LMS_Logins_Per_Week"], Avg_Attendance=row["Avg_Attendance"],
                    Avg_Performance=row["Avg_Performance"], Semester_GPA=row["Semester_GPA"],
                    
                    # **FIX: Add the subject marks from the CSV file here**
                    Marks_Math=row["Marks_Math"],
                    Marks_Physics=row["Marks_Physics"],
                    Marks_Chemistry=row["Marks_Chemistry"],
                    Marks_CS=row["Marks_CS"],
                    Marks_Lab1=row["Marks_Lab1"],
                    Marks_Lab2=row["Marks_Lab2"]
                )
                db.session.add(student)
            
            db.session.commit()
            logging.info("Student seeding complete with all columns.")
        except Exception as e:
            logging.error(f"FATAL ERROR during CSV seeding: {e}")
            db.session.rollback()
with app.app_context():
    create_tables_and_seed()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/demo-login/<role>")
def demo_login(role):
    if role == "admin":
        user = Admin.query.first()
    else:
        user = Student.query.order_by(Student.ml_risk_score.desc()).first() or Student.query.first()
    
    if user:
        session["user_id"], session["role"] = user.id, role
        flash(f"Welcome {role.capitalize()}. Demo login successful!", "success")
        return redirect(url_for(f"{role}_dashboard"))
    
    flash("Demo user not found.", "error")
    return redirect(url_for("login"))

@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin": return redirect(url_for("login"))
    try: evaluate_risks()
    except Exception as e: logging.error(f"Error during risk evaluation: {e}")
    students = Student.query.order_by(Student.ml_risk_score.desc()).all()
    return render_template("dashboard_admin.html", students=students)

@app.route("/student")
def student_dashboard():
    if session.get("role") != "student": return redirect(url_for("login"))
    student = Student.query.get(session["user_id"])
    return render_template("dashboard_student.html", student=student)

@app.route("/student_details/<student_id>")
def student_details(student_id):
    if session.get("role") != "admin": return jsonify({"error": "Unauthorized"}), 403
    student = Student.query.filter_by(student_id=student_id).first()
    if not student: return jsonify({"error": "Student not found"}), 404
    
    student_data = {
        "name": student.name, "student_id": student.student_id, "email": student.email,
        "risk_level": student.risk_level, "risk_reason": student.risk_reason,
        "ml_risk_score": f"{student.ml_risk_score:.1f}%", "age": student.Age,
        "gender": student.Gender, "year_of_study": student.Year_of_Study,
        "gpa": student.Semester_GPA, "avg_attendance": f"{student.Avg_Attendance:.1f}%",
        "avg_performance": f"{student.Avg_Performance:.1f}",
        "scholarship": student.Scholarship_Status, "loan": student.Loan_Status,
        "fee_status": student.fee_status, "health_issue": student.Chronic_Health_Issue,
        "total_leaves": student.Total_Leaves, "disciplinary_actions": student.Disciplinary_Actions,
        "lms_logins": student.LMS_Logins_Per_Week,
        "counseling_sessions": student.Counseling_Sessions_Attended,
        "class_participation": student.Class_Participation,
        
        # **FIX:** Added the missing subject marks data
        "marks_math": student.Marks_Math,
        "marks_physics": student.Marks_Physics,
        "marks_chemistry": student.Marks_Chemistry,
        "marks_cs": student.Marks_CS,
        "marks_lab1": student.Marks_Lab1,
        "marks_lab2": student.Marks_Lab2
    }
    return jsonify(student_data)

@app.route("/evaluate")
def evaluate():
    if session.get("role") != "admin": return redirect(url_for("login"))
    
    try:
        evaluate_risks()
        logging.info("Risk evaluation completed.")
    except Exception as e:
        flash(f"Risk evaluation error: {e}", "error")
        return redirect(url_for("admin_dashboard"))
   
    at_risk_students = Student.query.filter(Student.risk_level.in_(["Yellow", "Red"])).all()
    if not at_risk_students:
        flash("Risk analysis complete. No at-risk students found.", "success")
        return redirect(url_for("admin_dashboard"))

    emails_sent = 0
    server = None
    try:
        logging.info(f"Connecting to SMTP server to send {len(at_risk_students)} emails...")
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        if MAIL_USE_TLS: server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        logging.info("SMTP Login successful.")

        for student in at_risk_students:
            subject = f"Academic Warning: Your Status is '{student.risk_level}'"
            message = (f"Dear {student.name},\n\nThis is a notification that your academic profile has been flagged for review.\n"
                       f"Risk Level: {student.risk_level}\n"
                       f"Identified Factors: {student.risk_reason}\n\n"
                       "Please contact your academic advisor to discuss this.\n\nSincerely,\nEduRisk AI System")
            
            msg = MIMEText(message)
            msg["Subject"], msg["From"], msg["To"] = subject, MAIL_USERNAME, student.email
            server.sendmail(MAIL_USERNAME, [student.email], msg.as_string())
            emails_sent += 1
            logging.info(f"Email sent to {student.name}")

        flash(f"Risk analysis complete. {emails_sent} notifications dispatched.", "success")

    except Exception as e:
        logging.error(f"Failed to send emails: {e}")
        flash(f"Email sending failed after {emails_sent} notifications. Error: {e}", "error")
    
    finally:
        if server:
            server.quit()
            logging.info("SMTP connection closed.")
    return redirect(url_for("admin_dashboard"))
    
@app.route("/report")
def report():
    if session.get("role") != "admin": return redirect(url_for("login"))
    try:
        filename = generate_csv_report(app.config["UPLOAD_FOLDER"])
        flash(f"Report generated: {os.path.basename(filename)}.", "success")
    except Exception as e:
        flash(f"Error generating report: {e}", "error")
    return redirect(url_for("admin_dashboard"))

@app.route("/download-report")
def download_report():
    if session.get("role") != "admin": return redirect(url_for("admin_dashboard"))
    directory, filename = app.config["UPLOAD_FOLDER"], "report.csv"
    if not os.path.exists(os.path.join(directory, filename)):
        flash("Report file not found. Please 'Generate Report' first.", "error")
        return redirect(url_for("admin_dashboard"))
    return send_from_directory(directory, filename, as_attachment=True)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if session.get("role") != "admin": return redirect(url_for("login"))
    return render_template("upload.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

