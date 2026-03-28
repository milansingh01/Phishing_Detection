from fastapi import APIRouter
from ..models.schema import ExtensionPayload, AnalysisResult
from ..models.db_models import EmailCase
from ..services.ml_analyzer import ml_analyzer
from ..services.rule_engine import rule_engine
from ..database import SessionLocal
import traceback

router = APIRouter(prefix="/api/analyze", tags=["extension"])

@router.post("/", response_model=AnalysisResult)
async def analyze_email_from_extension(payload: ExtensionPayload):
    """
    Called by popup.js to get immediate feedback for the user in the extension UI.
    Analyzes synchronously and inserts perfectly to the dashboard DB locally.
    """
    
    # Quick analysis
    try:
        ml_results = ml_analyzer.analyze_text(payload.subject, payload.body)
        cred_results = rule_engine.check_credentials(payload.body)
        attach_results = rule_engine.analyze_attachments(payload.attachments)
    except Exception as e:
        print("Error during analysis:", str(e))
        traceback.print_exc()
        ml_results = {"label": "Legitimate", "score": 50.0, "reasoning": "Fallback analysis", "flags": {}}
        cred_results = {"has_leaks": False}
        attach_results = {"reasoning": "", "flags": {}}
    
    combined_flags = {**ml_results["flags"], **attach_results["flags"]}
    if cred_results["has_leaks"]:
        combined_flags["credential_leaks"] = cred_results["leak_types"]
        
    final_label = ml_results["label"]
    final_score = ml_results["score"]
    reasoning = ml_results["reasoning"] + " " + attach_results["reasoning"]
    
    if cred_results["has_leaks"] or combined_flags.get("malicious_executable"):
        final_label = "Phishing"
        final_score = max(final_score, 95.0)
    elif final_label == "Legitimate" and len(combined_flags) > 0:
        if combined_flags.get("ai_generated_suspicion") or combined_flags.get("compressed_archive"):
            final_label = "Phishing"
            final_score = 80.0
        else:
            final_score = min(final_score, 60.0)
            
    # Also adjust labels right away into the DB ("Fraud" -> "Phishing", "Safe" -> "Legitimate")
    if final_label == "Fraud": final_label = "Phishing"
    if final_label == "Safe": final_label = "Legitimate"

    # Save to Database natively
    db = SessionLocal()
    try:
        new_case = EmailCase(
            subject=payload.subject,
            sender=payload.sender,
            original_content=payload.body,
            attachments=payload.attachments,
            predicted_label=final_label,
            confidence_score=final_score,
            explanation=reasoning.strip(),
            department="Auto-Detected",
            language=payload.lang,
            flags=combined_flags
        )
        db.add(new_case)
        db.commit()
    except Exception as e:
        print("Database save error:", str(e))
    finally:
        db.close()

    return AnalysisResult(
        subject=payload.subject,
        predicted_label=final_label,
        confidence_score=final_score,
        explanation=reasoning.strip(),
        flags=combined_flags
    )
