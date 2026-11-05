"""
ScamShield WhatsApp Spam & Notification Guardian
Interprets, inspects, and defends against incoming WhatsApp scams,
group spam broadcasts, and malicious phishing notifications.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure package root is available
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline import ScamShieldPipeline

class WhatsAppMessage:
    def __init__(
        self,
        sender_name: str,
        sender_number: str,
        message_text: str,
        timestamp: Optional[str] = None,
        is_group: bool = False,
        group_name: Optional[str] = None
    ):
        self.sender_name = sender_name
        self.sender_number = sender_number
        self.message_text = message_text
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.is_group = is_group
        self.group_name = group_name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_name": self.sender_name,
            "sender_number": self.sender_number,
            "message_text": self.message_text,
            "timestamp": self.timestamp,
            "is_group": self.is_group,
            "group_name": self.group_name
        }


class WhatsAppGuardian:
    def __init__(self, pipeline: Optional[ScamShieldPipeline] = None):
        self.pipeline = pipeline or ScamShieldPipeline()
        self.alert_history: List[Dict[str, Any]] = []

    def inspect_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """
        Processes an incoming WhatsApp message/notification, calculates threat level,
        and generates automated alert notification and auto-reply warning.
        """
        scan_result = self.pipeline.scan_message(message.message_text)

        is_scam = scan_result["is_scam"]
        risk_score = scan_result["risk_score"]
        category = scan_result["category"]
        risk_level = scan_result["risk_level"]

        # Determine notification severity
        if risk_score >= 80:
            notification_type = "CRITICAL_INTERCEPT"
            notification_icon = "🚨"
            action = "QUARANTINE_AND_BLOCK"
        elif risk_score >= 50:
            notification_type = "HIGH_RISK_WARNING"
            notification_icon = "⚠️"
            action = "ALERT_USER"
        elif risk_score >= 25:
            notification_type = "SUSPICIOUS_CONTENT"
            notification_icon = "🟡"
            action = "FLAG_FOR_REVIEW"
        else:
            notification_type = "SAFE"
            notification_icon = "✅"
            action = "DELIVER_NORMALLY"

        # Generate automated WhatsApp response warning
        auto_reply = ""
        if is_scam or risk_score >= 50:
            auto_reply = (
                f"🛡️ [SCAMSHIELD NOTIFICATION INTERCEPT]\n"
                f"WARNING: This message was detected as a potential {category.replace('_', ' ').upper()} (Risk: {risk_score}%).\n"
                f"DO NOT click external links, provide 2FA OTPs, or transfer money."
            )

        alert_payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "WhatsApp",
            "sender": f"{message.sender_name} ({message.sender_number})",
            "is_group": message.is_group,
            "group_name": message.group_name,
            "original_text": message.message_text,
            "notification_type": notification_type,
            "notification_icon": notification_icon,
            "action_taken": action,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "category": category,
            "tactics": scan_result["tactics_detected"],
            "flagged_tokens": scan_result["flagged_tokens"],
            "extracted_urls": scan_result["extracted_urls"],
            "safety_advice": scan_result["safety_advice"],
            "auto_reply_warning": auto_reply
        }

        self.alert_history.append(alert_payload)
        return alert_payload

    def process_webhook_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses incoming Meta WhatsApp Cloud API or Twilio webhook format.
        """
        # Meta Cloud API standard format
        try:
            entry = payload.get("entry", [{}])[0]
            change = entry.get("changes", [{}])[0]
            value = change.get("value", {})
            contacts = value.get("contacts", [{}])[0]
            messages = value.get("messages", [{}])[0]

            sender_name = contacts.get("profile", {}).get("name", "Unknown Contact")
            sender_num = messages.get("from", "Unknown Number")
            text_body = messages.get("text", {}).get("body", "")

            msg = WhatsAppMessage(
                sender_name=sender_name,
                sender_number=sender_num,
                message_text=text_body
            )
            return self.inspect_message(msg)
        except Exception:
            # Fallback simple format
            sender = payload.get("sender", "WhatsApp User")
            sender_num = payload.get("phone", "Unknown Phone")
            text = payload.get("text") or payload.get("body", "")
            msg = WhatsAppMessage(sender_name=sender, sender_number=sender_num, message_text=text)
            return self.inspect_message(msg)

    def trigger_windows_toast(self, alert: Dict[str, Any]):
        """Emits a formatted alert to console and desktop."""
        print("=" * 60)
        print(f" {alert['notification_icon']} WHATSAPP NOTIFICATION GUARDIAN ALERT")
        print("=" * 60)
        print(f" Sender      : {alert['sender']}")
        print(f" Risk Score  : {alert['risk_score']}% ({alert['risk_level']})")
        print(f" Category    : {alert['category'].replace('_', ' ').title()}")
        print(f" Action      : {alert['action_taken']}")
        print(f" Message     : \"{alert['original_text']}\"")
        if alert["auto_reply_warning"]:
            print(f" Auto-Reply  : \n{alert['auto_reply_warning']}")
        print("=" * 60)


if __name__ == "__main__":
    guardian = WhatsAppGuardian()
    print("[*] ScamShield WhatsApp Notification Guardian Active.")
    print("[*] Simulating incoming deceptive WhatsApp broadcast...\n")

    sample_msg = WhatsAppMessage(
        sender_name="Recruiter Dave (Telegram Promo)",
        sender_number="+65 8921 4452",
        message_text="Earn $300-$800 daily working from home! Like YouTube videos. Daily payout via PayNow. Message HR WhatsApp: +65 8921 4452",
        is_group=True,
        group_name="SG Part-Time Job Seekers"
    )

    alert = guardian.inspect_message(sample_msg)
    guardian.trigger_windows_toast(alert)
