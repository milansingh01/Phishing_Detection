from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from datetime import datetime
from ..database import Base

class EmailCase(Base):
    __tablename__ = "email_cases"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    sender = Column(String, nullable=True)
    original_content = Column(Text)
    attachments = Column(String)  # Comma separated
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Analysis Results
    predicted_label = Column(String)  # 'Fraud', 'Safe'
    confidence_score = Column(Float)
    explanation = Column(Text)       # LLM Reasoning
    department = Column(String)      # e.g., 'Finance', 'HR', 'Engineering'
    language = Column(String, default="English")
    
    # Flags (stored as JSON)
    flags = Column(JSON)  # e.g., {"ai_generated": true, "credential_exposed": true}
    
    # Analyst Verification
    human_verification = Column(String, default="Pending")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    role = Column(String) # 'Admin', 'Employee'
    department = Column(String)
