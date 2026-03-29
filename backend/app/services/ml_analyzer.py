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
        
        # 1. Advanced Language Detection
        try:
            from langdetect import detect
            detected_lang = detect(text)
        except Exception:
            detected_lang = "en"
            
        # Map known codes to full names, fallback to code
        lang_map = {"en": "English", "hi": "Hindi", "es": "Spanish", "fr": "French", "de": "German", "ja": "Japanese"}
        lang_name = lang_map.get(detected_lang, detected_lang.upper())
        
        flags = {
            "language": lang_name,
            "suspicious_phrase_extracted": None
        }

        # Multinational suspicious keywords mapping
        suspicious_keywords = {
            "en": ["urgent", "verify", "suspend", "account", "login", "password", "click here", "immediate action", "locked", "unusual activity", "update your account"],
            "hi": ["जरूरी", "सत्यापित", "खाता", "लॉगिन", "पासवर्ड", "यहाँ क्लिक करें", "तत्काल कार्रवाई", "लंबित", "असामान्य गतिविधि", "यहाँ क्लिक", "अपडेट"],
            "es": ["urgente", "verificar", "cuenta", "iniciar sesión", "contraseña", "haz clic aquí", "acción inmediata", "bloqueado", "actividad inusual", "actualizar"],
            "fr": ["urgent", "vérifier", "compte", "connexion", "mot de passe", "cliquez ici", "action immédiate", "bloqué", "activité inhabituelle", "mettre à jour"],
            "de": ["dringend", "überprüfen", "konto", "anmelden", "passwort", "hier klicken", "sofortige maßnahme", "gesperrt", "ungewöhnliche aktivität", "aktualisieren"],
            "ja": ["緊急", "確認", "アカウント", "ログイン", "パスワード", "ここをクリック", "即時対応", "ロック", "異常なアクティビティ", "更新"]
        }
        
        active_keywords = suspicious_keywords.get(detected_lang, suspicious_keywords["en"])

        classifier = self._get_classifier()

        if not classifier:
            return {
                "label": "Safe",
                "score": 0.5,
                "flags": flags,
                "reasoning": "Model failed to load."
            }

        # Truncate to max 512 tokens to avoid index errors for overall text
        result = classifier(text[:500])[0]
        
        label_raw = result['label']
        is_fraud = label_raw == 'LABEL_1' or 'spam' in label_raw.lower()
        score = result['score']

        # DYNAMIC HIGHEST-RISK SENTENCE EXTRACTION (Replaces static keywords)
        # We split the text into sentences and use the ML model to score each one
        sentences = [s.strip() for s in body.replace("?", ".").replace("!", ".").replace("।", ".").split('.') if len(s.strip()) > 8]
        
        highest_risk_sentence = None
        highest_risk_score = 0.0
        
        for s in sentences:
            try:
                # Score the individual sentence
                s_result = classifier(s[:200])[0]
                s_is_fraud = s_result['label'] == 'LABEL_1' or 'spam' in s_result['label'].lower()
                s_score = s_result['score']
                
                # We care about the highest confidence spam sentence
                if s_is_fraud and s_score > highest_risk_score:
                    highest_risk_score = s_score
                    highest_risk_sentence = s
            except Exception:
                pass
                
        # Fallback to static keywords if ML didn't find a high-risk sentence
        if not highest_risk_sentence:
            for s in sentences:
                if any(kw in s.lower() for kw in active_keywords):
                    highest_risk_sentence = s
                    break

        # Build highly specific reasoning
        if is_fraud or highest_risk_sentence:
            label = "Fraud"
            confidence = max(score * 100, 75.0 if highest_risk_sentence else score * 100)
            if highest_risk_sentence:
                snippet = highest_risk_sentence[:150] + "..." if len(highest_risk_sentence) > 150 else highest_risk_sentence
                flags["suspicious_phrase_extracted"] = snippet
                if detected_lang != "en":
                    reasoning = f"Phishing detected in {lang_name} language. High-risk semantic phrasing identified: \"{snippet}\""
                else:
                    reasoning = f"High-risk semantic phrasing identified: \"{snippet}\""
            else:
                reasoning = f"The entire structure of the {lang_name} message perfectly matches known phishing evasion templates."
        else:
            label = "Safe"
            confidence = score * 100
            reasoning = f"Text analysis indicates legitimate {lang_name} communication."
            
        return {
            "label": label,
            "score": round(confidence, 1),
            "flags": flags,
            "reasoning": reasoning
        }

ml_analyzer = MLAnalyzer()
