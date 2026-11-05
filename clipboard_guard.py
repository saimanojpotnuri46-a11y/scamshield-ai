"""
ScamShield Clipboard & Browser Phishing Shield
Monitors system clipboard activity or text copies from WhatsApp Web / Chrome,
evaluating links and messages in real time to prevent accidental navigation.
"""

import os
import sys
import time
from typing import Optional, Dict, Any, List

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline import ScamShieldPipeline
from src.preprocessor import extract_urls

class ClipboardGuard:
    def __init__(self, pipeline: Optional[ScamShieldPipeline] = None):
        self.pipeline = pipeline or ScamShieldPipeline()
        self.intercepted_history: List[Dict[str, Any]] = []

    def inspect_clipboard_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Scans clipboard content and returns alert if suspicious."""
        if not text or len(text.strip()) < 5:
            return None

        result = self.pipeline.scan_message(text)
        urls = extract_urls(text)

        # Flag if classified as scam OR has suspicious URLs
        if result["is_scam"] or result["risk_score"] >= 40:
            alert = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "Clipboard / Browser Intercept",
                "copied_text": text,
                "urls_found": urls,
                "risk_score": result["risk_score"],
                "risk_level": result["risk_level"],
                "category": result["category"],
                "tactics": result["tactics_detected"],
                "safety_advice": result["safety_advice"],
                "warning": (
                    f"⚠️ SCAMSHIELD CLIPBOARD ALERT: Copied content flagged as "
                    f"{result['category'].upper()} with {result['risk_score']}% risk!"
                )
            }
            self.intercepted_history.append(alert)
            return alert

        return None

    def print_alert(self, alert: Dict[str, Any]):
        print("\n" + "=" * 65)
        print(" 📋 [CLIPBOARD INTERCEPTOR] PHISHING LINK / SCAM DETECTED!")
        print("=" * 65)
        print(f" Warning    : {alert['warning']}")
        print(f" Risk Score : {alert['risk_score']}% ({alert['risk_level']})")
        print(f" Category   : {alert['category'].replace('_', ' ').title()}")
        print(f" Copied Text: \"{alert['copied_text'][:100]}...\"")
        if alert["urls_found"]:
            print(f" URLs Found : {', '.join(alert['urls_found'])}")
        print(" Recommended Action: DO NOT paste or open this link in your browser!")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    guard = ClipboardGuard()
    print("[*] ScamShield Clipboard Shield running in simulation mode...")

    # Test sample suspicious copy action from browser
    suspicious_copied_link = "Verify your DBS digital token before expiration: http://dbs-secure-verify.xyz"
    alert = guard.inspect_clipboard_text(suspicious_copied_link)
    if alert:
        guard.print_alert(alert)
