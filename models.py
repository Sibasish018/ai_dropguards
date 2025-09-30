from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    # General fields
    attendance = db.Column(db.Float, default=0.0)
    marks = db.Column(db.Float, default=0.0)
    fee_status = db.Column(db.String(50), default="Paid")
    
    # Risk analysis fields
    risk_level = db.Column(db.String(20), default="Green")
    risk_reason = db.Column(db.String(255), default="")
    ml_risk_score = db.Column(db.Float, default=0.0)
    
    # --- ALL Comprehensive fields required by the ML preprocessor ---
    Age = db.Column(db.Integer, default=20)
    Gender = db.Column(db.String(10), default="Male")
    Year_of_Study = db.Column(db.Integer, default=1)
    Parent_Annual_Income = db.Column(db.Float, default=50000.0)
    Scholarship_Status = db.Column(db.String(20), default="No")
    Loan_Status = db.Column(db.String(20), default="No")
    Chronic_Health_Issue = db.Column(db.String(10), default="No")
    Health_Issue_Type = db.Column(db.String(50), default="None")
    Total_Leaves = db.Column(db.Integer, default=0)
    Counseling_Sessions_Attended = db.Column(db.Integer, default=0)
    Disciplinary_Actions = db.Column(db.Integer, default=0)
    Class_Participation = db.Column(db.String(20), default="Medium")
    Extracurricular_Activities_Score = db.Column(db.Float, default=50.0)
    LMS_Logins_Per_Week = db.Column(db.Float, default=5.0)
    Avg_Attendance = db.Column(db.Float, default=75.0)
    Avg_Performance = db.Column(db.Float, default=50.0)
    Semester_GPA = db.Column(db.Float, default=6.0)
    # In models.py, inside the Student class
    Marks_Math = db.Column(db.Float, default=50.0)
    Marks_Physics = db.Column(db.Float, default=50.0)
    Marks_Chemistry = db.Column(db.Float, default=50.0)
    Marks_CS = db.Column(db.Float, default=50.0)
    Marks_Lab1 = db.Column(db.Float, default=50.0)
    Marks_Lab2 = db.Column(db.Float, default=50.0)

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attendance_cutoff = db.Column(db.Float, default=75.0)
    marks_cutoff = db.Column(db.Float, default=40.0)
    fee_delay_days = db.Column(db.Integer, default=30)