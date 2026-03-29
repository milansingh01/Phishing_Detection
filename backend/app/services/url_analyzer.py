import urllib.parse
import re

class UrlAnalyzer:
    def __init__(self):
        # Known dangerous strings commonly used in pirated/illegal or malicious setups
        self.pirate_keywords = ["crack", "keygen", "free-movies", "pirate", "torrent", "nulled", "watch-free", "movies-online"]
        
        # High-risk TLDs
        self.risky_tlds = [".xyz", ".tk", ".top", ".ml", ".ga", ".cf", ".gq", ".ru", ".cn", ".su"]
        
        # Homoglyphs and Typosquatting (e.g. paypa1 vs paypal)
        self.homoglyph_patterns = [
            r"paypa1", r"barc1ays", r"barclays[a-z]{1,2}\.com", r"goggle\.com", r"micr0soft"
        ]
        
    def analyze_url(self, url: str) -> dict:
        if not url or not url.startswith("http"):
             return {"is_dangerous": False, "reason": "System URL bypassed."}
             
        try:
             parsed = urllib.parse.urlparse(url)
             domain = parsed.netloc.lower()
             path = parsed.path.lower()
             
             # Check 1: Raw IP Adress Instead of Domain (e.g., http://192.168.1.1)
             if re.match(r"^(\d{1,3}\.){3}\d{1,3}(:\d+)?$", domain):
                  return {"is_dangerous": True, "reason": "Direct IP connection detected. This is a common tactic to bypass domain reputation checks."}
             
             # Check 2: Pirated Keywords
             if any(kw in domain or kw in path for kw in self.pirate_keywords):
                  return {"is_dangerous": True, "reason": "Pirated Content or Malicious Media host detected. Access is strictly prohibited to prevent drive-by malware infections."}
                  
             # Check 3: Risky TLDs
             if any(domain.endswith(tld) for tld in self.risky_tlds):
                  return {"is_dangerous": True, "reason": f"High-risk Top Level Domain ({domain.split('.')[-1]}) detected. Often used for anonymous spear-phishing."}
                  
             # Check 4: Typosquatting / Homoglyphs
             if any(re.search(pat, domain) for pat in self.homoglyph_patterns):
                  return {"is_dangerous": True, "reason": "Typosquatting or Homoglyph detected. The domain is attempting to mimic a trusted financial institution."}
                  
             # Check 5: Excessive Hyphens (frequent in auto-generated malicious domains)
             if domain.count("-") > 3:
                  return {"is_dangerous": True, "reason": "Excessive hyphens in the domain suggest an auto-generated or evasive infrastructure."}
                  
        except Exception as e:
             return {"is_dangerous": False, "reason": "Failed to parse URL natively."}
             
        # Safe fallback
        return {"is_dangerous": False, "reason": "Domain appears legitimate based on heuristic checks."}

url_analyzer = UrlAnalyzer()
