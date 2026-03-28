import re
import logging

logger = logging.getLogger(__name__)

class RuleEngine:
    def __init__(self):
        # Extremely simple heuristics for token extraction
        self.credential_patterns = {
            "oauth_token": r"ya29\.[0-9a-zA-Z_-]+",
            "bearer_token": r"Bearer\s+[A-Za-z0-9\-\._~\+\/]+",
            "password_hint": r"(?i)password[\s:]*([a-zA-Z0-9!@#\$%\^&\*]{6,})",
            "db_conn_str": r"(postgres|mysql|mongodb):\/\/[a-zA-Z0-9_]+:[^@]+@[\w\.-]+",
        }
        
    def check_credentials(self, text: str) -> dict:
        leaks = []
        for c_type, pattern in self.credential_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                 leaks.append(f"{c_type}_exposed")
                 
        return {
            "has_leaks": len(leaks) > 0,
            "leak_types": leaks
        }
        
    def analyze_attachments(self, attachments_str: str) -> dict:
        if not attachments_str or attachments_str == "None":
             return {"flags": {}, "reasoning": ""}
             
        flags = {}
        reasoning = []
        
        att_list = [v.strip().lower() for v in attachments_str.split(",")]
        
        # Checking attachment extensions indicating potential risk based on fraud trends
        for att in att_list:
             if att.endswith(".exe") or att.endswith(".scr") or att.endswith(".vbs"):
                 flags["malicious_executable"] = True
                 reasoning.append(f"Executable payload detected ({att}).")
             elif att.endswith(".zip") or att.endswith(".rar"):
                 flags["compressed_archive"] = True
                 reasoning.append(f"Compressed archive requiring deep scan ({att}).")
             elif att.endswith(".html") or att.endswith(".htm"):
                 flags["html_smuggling_suspect"] = True
                 reasoning.append(f"HTML attachment suspect of credential smuggling ({att}).")
             elif att.endswith(".pdf"):
                 # Normally, we'd use PyMuPDF to parse the actual PDF if we had the file stream.
                 # Since extension only gives names, we run basic checks.
                 pass
                 
        return {
             "flags": flags,
             "reasoning": " ".join(reasoning)
        }

rule_engine = RuleEngine()
