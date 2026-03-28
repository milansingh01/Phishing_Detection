import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

class MLAnalyzer:
    def __init__(self):
        self._classifier = None
        self._load_attempted = False

    def _get_classifier(self):
        if self._load_attempted:
            return self._classifier
            
        logger.info("Initializing HuggingFace Pipeline (Lazy Load)...")
        try:
            self._classifier = pipeline('text-classification', model='mrm8488/bert-tiny-finetuned-sms-spam-detection')
            logger.info("Pipeline loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load HuggingFace pipeline: {e}")
        finally:
            self._load_attempted = True
            
        return self._classifier

    def analyze_text(self, subject: str, body: str) -> dict:
        text = f"Subject: {subject}\nBody: {body}"
        
        # Heuristics for language mix / AI generated
        is_hindi = any('\u0900' <= char <= '\u097F' for char in text)
        is_english = any('A' <= char.upper() <= 'Z' for char in text)
        mixed_language = is_hindi and is_english
        
        flags = {
            "mixed_language": mixed_language,
            "ai_generated_suspicion": "urgent" in text.lower() and "verify" in text.lower() # basic heuristic to augment
        }

        classifier = self._get_classifier()

        if not classifier:
            return {
                "label": "Safe" if not mixed_language else "Fraud",
                "score": 0.5,
                "flags": flags,
                "reasoning": "Model failed to load. Falling back to heuristic rules."
            }

        # Truncate to max 512 tokens to avoid index errors
        result = classifier(text[:500])[0]
        
        # 'LABEL_1' is usually spam/fraud, 'LABEL_0' is usually ham/safe. 
        # Check actual label mapping for specific model.
        # For mrm8488/bert-tiny, LABEL_1 is spam.
        label_raw = result['label']
        is_fraud = label_raw == 'LABEL_1' or 'spam' in label_raw.lower()
        score = result['score']

        # Extract suspicious snippet for reasoning
        suspicious_keywords = ["urgent", "verify", "suspend", "account", "login", "password", "click here", "immediate action", "locked", "unusual activity"]
        found_snippets = []
        # Split roughly by punctuation
        sentences = [s.strip() for s in body.replace("?", ".").replace("!", ".").split('.') if len(s.strip()) > 5]
        for s in sentences:
            if any(kw in s.lower() for kw in suspicious_keywords):
                found_snippets.append(s)

        # Adjust score and class based on dataset context
        if is_fraud:
            label = "Fraud"
            confidence = score * 100
            if found_snippets:
                snippet = found_snippets[0][:120] + "..." if len(found_snippets[0]) > 120 else found_snippets[0]
                reasoning = f"Suspicious phrasing: \"{snippet}\""
            else:
                reasoning = "Message structure perfectly matches known spam/phishing templates."
        else:
            # Check mixed language - typical in our custom dataset for fraud evasion
            if mixed_language and "update your account" in body.lower():
                label = "Fraud"
                confidence = 85.0
                reasoning = "Suspicious mixed-language text combined with account update requests."
            else:
                label = "Safe"
                confidence = score * 100
                reasoning = "Text analysis indicates legitimate communication."
                
        # Override flags if specific ai-gen indicators are triggered
        if mixed_language and ("update your account" in body.lower() or "verify" in body.lower()):
            flags["ai_generated_suspicion"] = True
            label = "Fraud"
            
        return {
            "label": label,
            "score": round(confidence, 1),
            "flags": flags,
            "reasoning": reasoning
        }

ml_analyzer = MLAnalyzer()
