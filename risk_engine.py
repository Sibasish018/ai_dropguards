from models import db, Student
from ml_predictor import get_ml_predictions
import logging

logging.basicConfig(level=logging.INFO)

def evaluate_risks():
    students = Student.query.all()
    if not students:
        logging.warning("No students to evaluate.")
        return

    logging.info(f"Starting rule-based risk evaluation for {len(students)} students...")

    for student in students:
        # Get the score and issues from our new reliable predictor
        score, issues = get_ml_predictions(student)
        
        # Determine risk level based on the score
        if score >= 70:
            level = "Red"
        elif score >= 40:
            level = "Yellow"
        else:
            level = "Green"
            
        # Update the student record
        student.ml_risk_score = score
        student.risk_level = level
        student.risk_reason = ", ".join(issues)

    # Commit all updates to the database
    db.session.commit()
    logging.info("Risk evaluation completed.")