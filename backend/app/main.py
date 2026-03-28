import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .database import engine, Base, SessionLocal
from .models.db_models import User, EmailCase
from .routers import extension, dashboard, auth
from .services.queue_manager import consumer_worker
from .auth import get_password_hash

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AlertShield Backend API")

# Setup CORS for the chrome extension (can be * or exactly Chrome extension ID)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed initial data
def seed_database():
    db = SessionLocal()
    try:
        # Upsert saakshi
        u1 = db.query(User).filter(User.email == "saakshi@barclays.com").first()
        if not u1:
            db.add(User(name="Saakshi", email="saakshi@barclays.com", role="Admin", department="Fraud Team", hashed_password=get_password_hash("pass345")))
            
        # Upsert pragya
        u2 = db.query(User).filter(User.email == "pragya@barclays.com").first()
        if not u2:
            db.add(User(name="Pragya", email="pragya@barclays.com", role="Analyst", department="Fraud Team", hashed_password=get_password_hash("pass123")))
            
        db.commit()
        
        # Check if we have some starting cases just to not show an empty dashboard
        if db.query(EmailCase).count() == 0:
            db.add(EmailCase(
                subject="Invoice Payment Required",
                sender="billing@external.com",
                original_content="Please pay the attached invoice.",
                predicted_label="Investigation",
                confidence_score=78.0,
                explanation="External sender with payment request.",
                department="Finance",
                flags={"malicious_executable": False}
            ))
        db.commit() # ensure everything is committed
    finally:
        db.close()
    db.close()

seed_database()

# Include Routers
app.include_router(extension.router)
app.include_router(dashboard.router)
app.include_router(auth.router)

# Startup Tasks
@app.on_event("startup")
async def startup_event():
    logger.info("Application Startup Complete.")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AlertShield Python Backend is running."}
