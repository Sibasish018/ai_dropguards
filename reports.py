import pandas as pd
import os
from models import Student

def generate_csv_report(directory, filename="report.csv"):
    """Generate CSV report of at-risk students with ML scores"""
    students = Student.query.filter(Student.risk_level != "Green").all()
    data = [
        {
            "Student ID": s.student_id,
            "Name": s.name,
            "Attendance": s.attendance,
            "Marks": s.marks,
            "Fee Status": s.fee_status,
            "Risk Level": s.risk_level,
            "ML Risk Score": f"{s.ml_risk_score:.1f}%" if s.ml_risk_score > 0 else "N/A",
            "Reason": s.risk_reason,
        }
        for s in students
    ]

    df = pd.DataFrame(data)
    filepath = os.path.join(directory, filename)
    df.to_csv(filepath, index=False)
    return filepath