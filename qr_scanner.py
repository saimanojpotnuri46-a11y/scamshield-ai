"""
ScamShield Quishing (QR Code Phishing) & Visual Lure Scanner
===========================================================
Defends against QR code cyber-fraud (Quishing), such as malicious PayNow/SGQR
payment stickers, deceptive courier rescheduling QR codes, and fake utility bills.
"""

import os
import sys
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure package root is available
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline import ScamShieldPipeline
from src.preprocessor import extract_urls, analyze_url

class QuishingScanner:
    def __init__(self, pipeline: Optional[ScamShieldPipeline] = None):
        self.pipeline = pipeline or ScamShieldPipeline()
        self.scanned_history: List[Dict[str, Any]] = []

    def scan_qr_payload(
        self,
        payload_text: str,
        source_context: str = "Physical Sticker / Mailer",
        location_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Inspects decoded QR code text or URL payload for phishing and malicious routing.
        """
        payload = payload_text.strip()
        urls = extract_urls(payload)

        # Base scan using ScamShield Dual-Tier NLP Engine
        scan_result = self.pipeline.scan_message(payload)
        base_risk = scan_result["risk_score"]
        category = scan_result["category"]

        url_audit = []
        is_high_risk_url = False

        for u in urls:
            analysis = analyze_url(u)
            url_audit.append(analysis)
            if analysis["url_risk_score"] >= 25:
                is_high_risk_url = True
                base_risk = max(base_risk, 75.0)

        # Quishing-specific heuristics
        parsed_domain = ""
        if urls:
            try:
                parsed = urlparse(urls[0])
                parsed_domain = parsed.netloc.lower()
            except Exception:
                pass

        # Check for fake payment lures (PayNow / SGQR / FAST impersonation)
        is_payment_spoof = bool(re.search(r'(paynow|sgqr|fast-transfer|payment-gateway|parking-fine)', payload, re.IGNORECASE))
        if is_payment_spoof and (is_high_risk_url or scan_result["is_scam"]):
            category = "bank_impersonation" if category == "legitimate" else category
            base_risk = min(100.0, max(base_risk, 88.0))

        risk_score = round(base_risk, 1)

        if risk_score >= 80:
            threat_level = "CRITICAL_QUISHING_RISK"
            icon = "🚨"
            action = "DO_NOT_SCAN_OR_PAY"
        elif risk_score >= 50:
            threat_level = "SUSPICIOUS_QR_CODE"
            icon = "⚠️"
            action = "INSPECT_DESTINATION_DOMAIN"
        else:
            threat_level = "BENIGN_QR_PAYLOAD"
            icon = "✅"
            action = "SAFE_TO_PROCEED"

        quishing_advice = [
            "Never scan untrusted QR codes pasted over official parking meters or store banners.",
            "Always check that the resolved browser URL begins with 'https://' and matches the official entity.",
            "Official Singapore government or banking bodies will never direct you to third-party domains via QR."
        ]

        result = {
            "payload": payload,
            "source_context": source_context,
            "location_tag": location_tag or "Unspecified Location",
            "threat_level": threat_level,
            "threat_icon": icon,
            "risk_score": risk_score,
            "category": category,
            "action_recommendation": action,
            "detected_urls": urls,
            "url_security_audit": url_audit,
            "tactics_detected": scan_result["tactics_detected"],
            "safety_checklist": quishing_advice,
            "summary": (
                f"{icon} {threat_level}: QR payload flagged with {risk_score}% risk ({category.replace('_', ' ').title()}). "
                f"Action: {action}."
            )
        }

        self.scanned_history.append(result)
        return result

    def print_qr_report(self, report: Dict[str, Any]):
        """Prints formatted console report for QR scan."""
        print("=" * 65)
        print(f" {report['threat_icon']} SCAMSHIELD QUISHING (QR PHISHING) AUDIT")
        print("=" * 65)
        print(f" Source Context : {report['source_context']}")
        print(f" Threat Level   : {report['threat_level']} (Score: {report['risk_score']}%)")
        print(f" Category       : {report['category'].replace('_', ' ').title()}")
        print(f" Action         : {report['action_recommendation']}")
        print(f" Decoded Payload: \"{report['payload']}\"")
        if report["detected_urls"]:
            print(f" Embedded URLs  : {', '.join(report['detected_urls'])}")
        print("-" * 65)
        print(" Safety Guidance:")
        for advice in report["safety_checklist"]:
            print(f"  • {advice}")
        print("=" * 65)


if __name__ == "__main__":
    scanner = QuishingScanner()
    print("[*] ScamShield Quishing Defense Scanner Active.")
    print("[*] Simulating scanning deceptive Parking Meter QR sticker...\n")

    fake_parking_qr = "Scan to pay overdue Singapore HDB parking fine of $12.00 immediately: http://hdb-parking-notice.top/paynow"
    report = scanner.scan_qr_payload(
        payload_text=fake_parking_qr,
        source_context="Tampered QR sticker over public parking ticket machine",
        location_tag="Tampines Ave 4 Carpark"
    )
    scanner.print_qr_report(report)
