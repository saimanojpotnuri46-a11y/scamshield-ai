"""
ScamShield Preprocessing & Heuristic Extraction Engine
Analyzes raw messages, extracts threat indicators, normalizes leetspeak,
and extracts structural signals (URLs, phone numbers, urgency markers).
"""

import re
from typing import Dict, List, Any

# Known suspicious TLDs frequently used in malicious infrastructure
SUSPICIOUS_TLDS = {
    "xyz", "top", "vip", "work", "cc", "club", "live", "link",
    "site", "online", "click", "info", "tk", "ml", "ga", "cf"
}

# Financial and high-value brands commonly targeted for spoofing
SPOOFED_BRANDS = [
    "dbs", "ocbc", "uob", "citi", "citibank", "hsbc", "standardchartered",
    "chase", "wellsfargo", "singpost", "dhl", "fedex", "usps", "ninjavan",
    "shopee", "lazada", "amazon", "apple", "google", "microsoft", "iras", "spf"
]

# Urgency and coercion patterns
URGENCY_PATTERNS = [
    r"\burgent(ly)?\b",
    r"\bimmediat(e|ely)\b",
    r"\bwithin \d+\s*(hours?|hrs?|mins?|minutes?)\b",
    r"\baccount.*(suspend(ed)?|lock(ed)?|freeze|frozen|restrict(ed)?)\b",
    r"\bunauthori[sz]ed (login|access|transaction|withdrawal)\b",
    r"\barrest warrant\b",
    r"\basset seizure\b",
    r"\bsubpoena\b",
    r"\baction required\b",
    r"\bexpire(d|s)? today\b",
    r"\bpenalt(y|ies)\b",
    r"\b24\s*h(ours?)?\b"
]

# Financial bait patterns
BAIT_PATTERNS = [
    r"\bguaranteed\b",
    r"\b(earn|make) \$\d+.*(daily|per day|day)\b",
    r"\bpassive income\b",
    r"\b(won|winner|winning)\b",
    r"\b(lucky draw|promo|prize|jackpot)\b",
    r"\bfree.*voucher\b",
    r"\b\d+%\s*(roi|apy|return|profit)\b",
    r"\bdouble your (crypto|btc|eth|money)\b"
]

# Credential / OTP solicitation patterns
CREDENTIAL_PATTERNS = [
    r"\bverify.*(identity|account|card|details)\b",
    r"\benter.*(otp|pin|password|token)\b",
    r"\bre-?activate.*(token|account|access)\b",
    r"\bclearance fee\b",
    r"\bcustoms duty\b",
    r"\bpay.*fee to release\b"
]

# Leetspeak / homoglyph mapping table
LEET_MAP = {
    "@": "a",
    "0": "o",
    "1": "i",
    "$": "s",
    "3": "e",
    "5": "s",
    "8": "b"
}

URL_REGEX = re.compile(
    r"(?:https?://|www\.)[^\s/$.?#].[^\s]*",
    re.IGNORECASE
)

IP_URL_REGEX = re.compile(
    r"https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s]*)?",
    re.IGNORECASE
)

PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b"
)

MONEY_REGEX = re.compile(
    r"(?:SGD|S\$|\$|USD|EUR|GBP)\s*[\d,]+(?:\.\d{1,2})?",
    re.IGNORECASE
)

def normalize_text(text: str) -> str:
    """Normalize whitespace and map common leetspeak substitutions."""
    if not isinstance(text, str):
        return ""
    text_clean = text.strip()
    return text_clean

def deobfuscate_leetspeak(text: str) -> str:
    """Replaces common leet substitutions inside suspected words."""
    result = text
    for char, replacement in LEET_MAP.items():
        result = result.replace(char, replacement)
    return result

def extract_urls(text: str) -> List[str]:
    """Extract all URLs from message text."""
    matches = URL_REGEX.findall(text)
    # Also find raw ip urls if missed
    ip_matches = IP_URL_REGEX.findall(text)
    urls = list(dict.fromkeys(matches + ip_matches))
    return urls

def analyze_url(url: str) -> Dict[str, Any]:
    """
    Heuristically checks if a URL has suspicious red flags:
    - Direct IP address hosting
    - Suspicious high-risk TLD
    - Spoofed brand in subdomain/domain
    - Excessive dashes or subdomains
    """
    url_lower = url.lower()
    is_ip = bool(IP_URL_REGEX.search(url_lower))
    
    # Extract domain part
    domain_match = re.search(r"https?://([^/:\s]+)", url_lower)
    domain = domain_match.group(1) if domain_match else url_lower
    
    # Check TLD
    tld = domain.split(".")[-1] if "." in domain else ""
    is_suspicious_tld = tld in SUSPICIOUS_TLDS
    
    # Brand spoofing check
    spoofed_brand = None
    for brand in SPOOFED_BRANDS:
        if brand in domain and not domain.endswith(f".{brand}.com") and not domain.endswith(f".{brand}.gov.sg"):
            spoofed_brand = brand
            break

    # URL shorteners
    is_shortener = any(s in domain for s in ["bit.ly", "tinyurl.com", "t.co", "is.gd", "rb.gy"])

    risk_score = 0
    reasons = []
    if is_ip:
        risk_score += 45
        reasons.append("Direct IP address in link URL")
    if is_suspicious_tld:
        risk_score += 35
        reasons.append(f"Suspicious high-risk top-level domain: .{tld}")
    if spoofed_brand:
        risk_score += 40
        reasons.append(f"Potential brand spoofing of '{spoofed_brand}' in unauthorized domain")
    if is_shortener:
        risk_score += 25
        reasons.append("Shortened link disguising real destination")

    return {
        "url": url,
        "domain": domain,
        "is_ip": is_ip,
        "tld": tld,
        "is_suspicious_tld": is_suspicious_tld,
        "spoofed_brand": spoofed_brand,
        "is_shortener": is_shortener,
        "url_risk_score": min(risk_score, 100),
        "reasons": reasons
    }

def extract_phone_numbers(text: str) -> List[str]:
    """Find telephone numbers in text."""
    matches = PHONE_REGEX.findall(text)
    # Filter out short strings that are just 4-digit years or OTPs
    valid_phones = [m.strip() for m in matches if len(re.sub(r"\D", "", m)) >= 7]
    return valid_phones

def extract_monetary_values(text: str) -> List[str]:
    """Extract money mentions (SGD 500, $2,499.00)."""
    return MONEY_REGEX.findall(text)

def detect_pattern_triggers(text: str) -> Dict[str, List[str]]:
    """Detect presence of urgency, financial bait, and credential harvesting patterns."""
    text_lower = text.lower()
    urgency_hits = []
    for pat in URGENCY_PATTERNS:
        match = re.search(pat, text_lower)
        if match:
            urgency_hits.append(match.group(0))

    bait_hits = []
    for pat in BAIT_PATTERNS:
        match = re.search(pat, text_lower)
        if match:
            bait_hits.append(match.group(0))

    cred_hits = []
    for pat in CREDENTIAL_PATTERNS:
        match = re.search(pat, text_lower)
        if match:
            cred_hits.append(match.group(0))

    return {
        "urgency_triggers": urgency_hits,
        "bait_triggers": bait_hits,
        "credential_triggers": cred_hits
    }

def compute_linguistic_features(text: str) -> Dict[str, float]:
    """Extract quantitative linguistic signals."""
    length = len(text)
    if length == 0:
        return {
            "char_length": 0,
            "word_count": 0,
            "uppercase_ratio": 0.0,
            "digit_ratio": 0.0,
            "exclamation_count": 0,
            "url_count": 0,
            "phone_count": 0
        }
    
    words = text.split()
    uppercase_chars = sum(1 for c in text if c.isupper())
    digit_chars = sum(1 for c in text if c.isdigit())
    exclamations = text.count("!") + text.count("?")
    urls = extract_urls(text)
    phones = extract_phone_numbers(text)

    return {
        "char_length": float(length),
        "word_count": float(len(words)),
        "uppercase_ratio": float(uppercase_chars) / max(length, 1),
        "digit_ratio": float(digit_chars) / max(length, 1),
        "exclamation_count": float(exclamations),
        "url_count": float(len(urls)),
        "phone_count": float(len(phones))
    }
