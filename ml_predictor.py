import logging

logging.basicConfig(level=logging.INFO)

def get_ml_predictions(student):
    """
    Calculates a risk score based on a clear, rule-based heuristic model.
    This version is reliable and does not depend on external .joblib files.
    """
    try:
        # --- 1. Calculate the Risk Score ---
        risk_score = 0.0
        
        # Academic Factors (Max 40 points)
        if student.Avg_Attendance < 50: risk_score += 20
        elif student.Avg_Attendance < 75: risk_score += 10
        if student.Avg_Performance < 40: risk_score += 15
        elif student.Avg_Performance < 60: risk_score += 5
        if student.Semester_GPA < 5.0: risk_score += 5

        # Behavioral Factors (Max 30 points)
        if student.Disciplinary_Actions > 0: risk_score += 15
        if student.Total_Leaves > 10: risk_score += 10
        elif student.Total_Leaves > 5: risk_score += 5
        if student.LMS_Logins_Per_Week < 2: risk_score += 5

        # Financial Factors (Max 20 points)
        if student.fee_status != 'Paid': risk_score += 15
        if student.Loan_Status == 'Yes' and student.Scholarship_Status == 'No': risk_score += 5
            
        # Personal Factors (Max 10 points)
        if student.Chronic_Health_Issue == 'Yes': risk_score += 5
        if student.Counseling_Sessions_Attended == 0 and student.risk_level != 'Green': risk_score += 5
        
        risk_score = min(risk_score, 100.0) # Cap the score at 100

        # --- 2. Determine Risk Issues ---
        issues = []
        if student.Avg_Attendance < 75 or student.Avg_Performance < 50 or student.Semester_GPA < 6.0:
            issues.append("Academic")
        if student.fee_status != 'Paid':
            issues.append("Financial")
        if student.Disciplinary_Actions > 0 or student.Total_Leaves > 10:
            issues.append("Behavioral")
        if student.Chronic_Health_Issue == 'Yes':
            issues.append("Health")
        if student.LMS_Logins_Per_Week < 3 or student.Extracurricular_Activities_Score < 40:
             issues.append("Engagement")

        if not issues:
            issues = ["No specific issues detected"]

        return risk_score, list(set(issues))

    except Exception as e:
        logging.error(f"Error in rule-based prediction for {student.student_id}: {e}")
        return 0.0, ["Prediction error"]