import asyncio
import logging
from ..models.schema import ExtensionPayload
from ..models.db_models import EmailCase
from ..database import SessionLocal
from .ml_analyzer import ml_analyzer
from .rule_engine import rule_engine

logger = logging.getLogger(__name__)

# Simulated Kafka Topic / Async Queue
phishing_event_queue = asyncio.Queue()

async def producer(payload: ExtensionPayload):
    """
    Simulates a Kafka Producer. Enqueues the raw email data from extension.
    """
    logger.info(f"Producing event for subject: {payload.subject}")
    await phishing_event_queue.put(payload)

async def consumer_worker():
    """
    Simulates a Kafka Consumer. Continually reads from queue,
    analyzes the payload using ML models & Rules, and saves to DB.
    """
    logger.info("Kafka Consumer Simulator Started.")
    while True:
        try:
            payload: ExtensionPayload = await phishing_event_queue.get()
            logger.info(f"Consuming event for subject: {payload.subject}")
            
            # --- Analysis Pipeline ---
            ml_results = ml_analyzer.analyze_text(payload.subject, payload.body)
            cred_results = rule_engine.check_credentials(payload.body)
            attach_results = rule_engine.analyze_attachments(payload.attachments)
            
            # Combine Flags
            combined_flags = {**ml_results["flags"], **attach_results["flags"]}
            if cred_results["has_leaks"]:
                combined_flags["credential_leaks"] = cred_results["leak_types"]
                
            # Final Labeling logic based on rules
            final_label = ml_results["label"]
            final_score = ml_results["score"]
            reasoning = ml_results["reasoning"] + " " + attach_results["reasoning"]
            
            if cred_results["has_leaks"] or combined_flags.get("malicious_executable"):
                final_label = "Fraud"
                final_score = max(final_score, 95.0)
                reasoning += f" Validated severe risk vectors: {combined_flags}."
            elif final_label == "Safe" and len(combined_flags) > 0:
                if combined_flags.get("ai_generated_suspicion") or combined_flags.get("compressed_archive"):
                    final_label = "Fraud"
                    final_score = 80.0
                    reasoning += " Safe prediction overturned due to heuristics indicators."
                else:
                    final_score = min(final_score, 60.0)
                    reasoning += " Minor flags present, overall deemed Safe."

            # Save to Database
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
                    department="Auto-Detected", # Could be parsed from headers if available
                    language=payload.lang,
                    flags=combined_flags
                )
                db.add(new_case)
                db.commit()
                db.refresh(new_case)
                logger.info(f"Successfully processed and stored Email Case #{new_case.id}")
            except Exception as e:
                logger.error(f"Database insertion failed: {e}")
            finally:
                db.close()
                phishing_event_queue.task_done()
                
        except asyncio.CancelledError:
            break
        except Exception as e:
             logger.error(f"Error in consumer loop: {e}")
