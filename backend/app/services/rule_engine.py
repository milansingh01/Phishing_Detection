import re
import logging

logger = logging.getLogger(__name__)

class RuleEngine:
    def __init__(self):
        # Advanced heuristics for token extraction
        self.credential_patterns = {
            "OAuth Token": r"ya29\.[0-9a-zA-Z_-]{20,}",
            "Bearer Token": r"Bearer\s+([A-Za-z0-9\-\._~\+\/]{20,})",
            "Cleartext Password": r"(?i)(?:password|pwd|passcode|pass|username|user)[\s=:,-]+([a-zA-Z0-9!@#\$%\^&\*.-]{4,})",
            "Database Connection": r"(postgres|mysql|mongodb):\/\/[a-zA-Z0-9_]+:([^@]+)@[\w\.-]+",
            "Credit Card": r"\b(?:\d[ -]*?){13,16}\b",
            "API Key": r"(?i)(api[_-]?key|secret|token)[\s=:]+([A-Za-z0-9_-]{16,})"
        }
        
    def check_credentials(self, text: str) -> dict:
        leaks = []
        for c_type, pattern in self.credential_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                # Capture the actual matched string (or group if configured)
                raw_match = match.group(1) if len(match.groups()) > 0 else match.group(0)
                
                # Partially mask for safety: show first 3 chars, mask the rest, then show last 2
                str_match = str(raw_match)
                if len(str_match) > 5:
                    masked = str_match[:3] + "*" * (len(str_match) - 5) + str_match[-2:]
                else:
                    masked = "***"
                    
                leaks.append(f"{c_type} ({masked})")
                 
        return {
            "has_leaks": len(leaks) > 0,
            "leak_types": leaks
        }
        
    def analyze_attachments(self, attachments_str: str) -> dict:
        if not attachments_str or attachments_str == "None":
             return {"flags": {}, "reasoning": ""}
             
        flags = {}
        reasoning = []
        
        att_list = [v.strip() for v in attachments_str.split(",") if v.strip()]
        
        # Checking attachment extensions indicating potential risk based on fraud trends
        for att in att_list:
             att_lower = att.lower()
             if att_lower.endswith(".exe") or att_lower.endswith(".scr") or att_lower.endswith(".vbs"):
                 flags["malicious_executable"] = True
                 reasoning.append(f"Attachment '{att}' is an executable file capable of installing malware.")
             elif att_lower.endswith(".zip") or att_lower.endswith(".rar") or att_lower.endswith(".7z"):
                 flags["compressed_archive"] = True
                 reasoning.append(f"Attachment '{att}' is a compressed archive, often used to bypass antivirus scans.")
             elif att_lower.endswith(".html") or att_lower.endswith(".htm") or att_lower.endswith(".svg"):
                 flags["html_smuggling_suspect"] = True
                 reasoning.append(f"Attachment '{att}' relies on browser rendering, making it highly suspect for HTML/SVG credential smuggling.")
             elif att_lower.endswith(".pdf"):
                 flags["pdf_suspect"] = True
                 reasoning.append(f"Attachment '{att}' is a PDF; highly suspect for containing malicious embedded hyperlinks or macros.")
             elif att_lower.endswith(".jpg") or att_lower.endswith(".jpeg") or att_lower.endswith(".png") or att_lower.endswith(".gif"):
                 flags["image_steganography_suspect"] = True
                 reasoning.append(f"Attachment '{att}' is an Image file. Image attachments from untrusted senders may contain tracking pixels or steganographic payloads.")
                 
        return {
             "flags": flags,
             "reasoning": " ".join(reasoning)
        }

rule_engine = RuleEngine()
