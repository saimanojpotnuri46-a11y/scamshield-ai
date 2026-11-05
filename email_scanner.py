"""
ScamShield Email Phishing & Corporate Impersonation Scanner
Inspects email headers, subject lines, body text, and embedded attachments/links
to detect Business Email Compromise (BEC) and phishing campaigns.
"""

import os
import sys
import re
from typing import Dict, Any, List, Optional

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline import ScamShieldPipeline
from src.preprocessor import extract_urls, analyze_url

class EmailPhishingScanner:
    def __init__(self, pipeline: Optional[ScamShieldPipeline] = None):
        self.pipeline = pipeline or ScamShieldPipeline()

    def scan_email(
        self,
        sender_email: str,
        subject: str,
        body: str,
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes an email for spoofing, deceptive reply-to mismatch,
        and malicious content.
        """
        full_text = f"Subject: {subject}\n\n{body}"
        scan_result = self.pipeline.scan_message(full_text)

        # Check for Reply-To / Sender domain mismatch
        sender_domain = sender_email.split("@")[-1] if "@" in sender_email else ""
        reply_to_domain = reply_to.split("@")[-1] if reply_to and "@" in reply_to else sender_domain
        domain_mismatch = (reply_to and sender_domain != reply_to_domain)

        # Free webmail spoofing check (e.g. CEO using @gmail.com)
        is_free_webmail = sender_domain.lower() in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        is_exec_spoofing = bool(re.search(r"\b(ceo|cfo|director|payroll|hr|finance)\b", sender_email.lower() + " " + subject.lower())) and is_free_webmail

        email_risk_score = scan_result["risk_score"]
        flags = []

        if domain_mismatch:
            email_risk_score = min(100.0, email_risk_score + 25.0)
            flags.append(f"Reply-To domain mismatch: '{reply_to_domain}' differs from sender '{sender_domain}'.")

        if is_exec_spoofing:
            email_risk_score = min(100.0, email_risk_score + 30.0)
            flags.append("Executive/Corporate impersonation detected originating from free webmail domain.")

        # Re-tier risk level
        if email_risk_score >= 80:
            tier = "CRITICAL PHISHING"
            badge = "🔴 Critical Phishing"
        elif email_risk_score >= 50:
            tier = "HIGH RISK EMAIL"
            badge = "🟠 High Risk"
        elif email_risk_score >= 25:
            tier = "SUSPICIOUS EMAIL"
            badge = "🟡 Suspicious"
        else:
            tier = "CLEAN EMAIL"
            badge = "🟢 Safe / Clean"

        return {
            "sender": sender_email,
            "subject": subject,
            "reply_to": reply_to or sender_email,
            "email_risk_score": round(email_risk_score, 1),
            "threat_tier": tier,
            "badge": badge,
            "category": scan_result["category"],
            "is_phishing": email_risk_score >= 50,
            "domain_mismatch": domain_mismatch,
            "flags": flags,
            "tactics": scan_result["tactics_detected"],
            "urls": scan_result["extracted_urls"],
            "safety_advice": scan_result["safety_advice"]
        }


if __name__ == "__main__":
    scanner = EmailPhishingScanner()
    print("[*] ScamShield Email Phishing Scanner Test...")

    res = scanner.scan_email(
        sender_email="payroll-update@dbs-corp-service.xyz",
        subject="URGENT: Outstanding Tax Invoice & Salary Hold",
        body="Dear Employee, IRAS tax audit requires urgent settlement of $1,420 fee. Confirm payment: http://iras-tax-clearance.vip",
        reply_to="secret-account@gmail.com"
    )

    print(f"Verdict: {res['threat_tier']} ({res['email_risk_score']}%)")
    print(f"Flags  : {res['flags']}")
