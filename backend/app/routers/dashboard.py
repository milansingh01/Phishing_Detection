from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.db_models import EmailCase, User
from ..models.schema import VerificationPayload
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/")
def get_dashboard_data(department: str = "All", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(EmailCase)
    
    if department != "All":
        query = query.filter(EmailCase.department == department)
        
    total_scanned = query.count()
    fraud_detected = query.filter(EmailCase.predicted_label == "Phishing").count()
    safe_emails = query.filter(EmailCase.predicted_label == "Legitimate").count()
    
    # Calculate simple accuracy heuristic based on confidence scores
    avg_conf = db.query(func.avg(EmailCase.confidence_score)).scalar() or 90.0
    
    cases_records = query.order_by(EmailCase.timestamp.desc()).limit(1000).all()
    cases = []
    for c in cases_records:
        cases.append({
            "id": str(c.id),
            "subject": c.subject,
            "sender": c.sender or "Unknown",
            "date": c.timestamp.isoformat() + "Z",
            "status": c.predicted_label,
            "score": round(c.confidence_score),
            "department": c.department or "General",
            "humanVerification": c.human_verification or "Pending",
            "explanation": c.explanation or ""
        })

    # For charts: emailsScanned last 5 days
    daily_scans = db.query(func.date(EmailCase.timestamp), func.count(EmailCase.id)).group_by(func.date(EmailCase.timestamp)).order_by(func.date(EmailCase.timestamp).desc()).limit(5).all()
    daily_scans.reverse()
    emails_scanned_chart = [{"date": str(date_val)[-5:], "emails": count} for date_val, count in daily_scans]
    if not emails_scanned_chart:
        emails_scanned_chart = [{"date": "Today", "emails": 0}]

    # For charts: department cases
    dept_cases_query = db.query(EmailCase.department, func.count(EmailCase.id)).group_by(EmailCase.department).all()
    department_cases = [{"department": dept or "General", "cases": count} for dept, count in dept_cases_query]
    if not department_cases:
        department_cases = [{"department": "General", "cases": 0}]

    return {
        "kpis": {
            "totalScanned": total_scanned,
            "fraudDetected": fraud_detected,
            "safeEmails": safe_emails,
            "accuracy": round(avg_conf, 1),
            "moneySaved": fraud_detected * 500 # Just a metric
        },
        "charts": {
            "emailsScanned": emails_scanned_chart,
            "fraudVsSafe": [
                {"name": "Phishing", "value": fraud_detected, "color": "hsl(0, 72%, 51%)"},
                {"name": "Legitimate", "value": safe_emails, "color": "hsl(217, 91%, 60%)"}
            ],
            "departmentCases": department_cases
        },
        "cases": cases,
        "performance": {
             "accuracy": round(avg_conf, 1),
             "falsePositives": db.query(EmailCase).filter(EmailCase.human_verification == "False Positive").count(),
             "falseNegatives": db.query(EmailCase).filter(EmailCase.human_verification == "Confirmed Safe").count()
        }
    }

@router.get("/users")
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role, "department": u.department} for u in users]

@router.patch("/cases/{case_id}/verify")
def verify_case(case_id: int, payload: VerificationPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = db.query(EmailCase).filter(EmailCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.human_verification = payload.status
    db.commit()
    return {"message": "Verification updated successfully"}
