from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExtensionPayload(BaseModel):
    subject: str
    body: str
    attachments: Optional[str] = "None"
    lang: str = "English"
    sender: str = "Unknown Extracted"

class AnalysisResult(BaseModel):
    subject: str
    predicted_label: str
    confidence_score: float
    explanation: str
    flags: Dict[str, Any]

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    department: str

    class Config:
        from_attributes = True

class DashboardKPIs(BaseModel):
    totalScanned: int
    fraudDetected: int
    safeEmails: int
    accuracy: float
    moneySaved: int

class DashboardCaseOut(BaseModel):
    id: str
    subject: str
    sender: str
    date: str
    status: str
    score: int
    department: str
    humanVerification: str = "Pending"
    explanation: str

    class Config:
        from_attributes = True

class VerificationPayload(BaseModel):
    status: str
