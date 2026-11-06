"""
ScamShield Telegram Spam & Bot Guardian
======================================
Interprets, inspects, and defends against incoming Telegram crypto scams,
fake investment bots, pump-and-dump channel broadcasts, and impersonation lures.
"""

import os
import sys
import json
import time
import re
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
from src.preprocessor import extract_urls
from src.localization import generate_auto_reply_warning, get_category_label

class TelegramMessage:
    def __init__(
        self,
        sender_username: str,
        message_text: str,
        sender_id: Optional[str] = None,
        chat_title: Optional[str] = None,
        is_channel: bool = False,
        is_bot: bool = False,
        forward_from: Optional[str] = None,
        timestamp: Optional[str] = None
    ):
        self.sender_username = sender_username
        self.message_text = message_text
        self.sender_id = sender_id or "tg_anon"
        self.chat_title = chat_title or "Direct Message"
        self.is_channel = is_channel
        self.is_bot = is_bot
        self.forward_from = forward_from
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_username": self.sender_username,
            "sender_id": self.sender_id,
            "chat_title": self.chat_title,
            "message_text": self.message_text,
            "is_channel": self.is_channel,
            "is_bot": self.is_bot,
            "forward_from": self.forward_from,
            "timestamp": self.timestamp
        }


class TelegramGuardian:
    def __init__(self, pipeline: Optional[ScamShieldPipeline] = None):
        self.pipeline = pipeline or ScamShieldPipeline()
        self.alert_history: List[Dict[str, Any]] = []

    def inspect_message(self, message: TelegramMessage, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        Inspects an incoming Telegram message, evaluating crypto signals,
        fake admin impersonations, and social engineering manipulation with language preference support.
        """
        scan_result = self.pipeline.scan_message(message.message_text, lang=lang)

        is_scam = scan_result["is_scam"]
        risk_score = scan_result["risk_score"]
        category = scan_result["category"]
        category_label = scan_result.get("category_label", category)
        risk_level = scan_result["risk_level"]
        active_lang = lang or scan_result.get("language")

        # Channel-specific heuristics: Telegram Invite links & Bot Handles
        urls = extract_urls(message.message_text)
        has_telegram_invite = bool(re.search(r'(t\.me\/joinchat|t\.me\/\+[a-zA-Z0-9_\-]+)', message.message_text, re.IGNORECASE))
        has_bot_lure = bool(re.search(r'(@[a-zA-Z0-9_]+bot|t\.me\/[a-zA-Z0-9_]+bot)', message.message_text, re.IGNORECASE))

        # Adjust score if suspicious invite in crypto / job context
        if (has_telegram_invite or has_bot_lure) and category in ["investment_crypto", "job_scam", "lottery_reward"]:
            risk_score = min(100.0, risk_score + 5.0)

        # Action determination
        if risk_score >= 80:
            action = "KICK_AND_DELETE_MESSAGE"
            notification_icon = "🚨"
            alert_status = "CRITICAL_THREAT"
        elif risk_score >= 50:
            action = "MUTE_USER_AND_WARN"
            notification_icon = "⚠️"
            alert_status = "SUSPICIOUS_BROADCAST"
        else:
            action = "ALLOW"
            notification_icon = "✅"
            alert_status = "BENIGN_MESSAGE"

        # Automated Safety Reply for Supergroup / Channel
        auto_reply = ""
        if is_scam:
            auto_reply = generate_auto_reply_warning(category, risk_score, lang=active_lang)

        alert = {
            "timestamp": message.timestamp,
            "platform": "Telegram",
            "chat": message.chat_title,
            "sender": f"@{message.sender_username.lstrip('@')}",
            "is_bot": message.is_bot,
            "is_channel": message.is_channel,
            "forward_from": message.forward_from,
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "alert_status": alert_status,
            "notification_icon": notification_icon,
            "category": category,
            "action_taken": action,
            "original_text": message.message_text,
            "tactics_detected": scan_result["tactics_detected"],
            "safety_advice": scan_result["safety_advice"],
            "auto_reply_warning": auto_reply
        }

        self.alert_history.append(alert)
        return alert

    def parse_telegram_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Parses standard Telegram Bot API webhook updates."""
        try:
            msg_obj = payload.get("message") or payload.get("channel_post") or {}
            from_obj = msg_obj.get("from", {})
            chat_obj = msg_obj.get("chat", {})

            sender_name = from_obj.get("username") or from_obj.get("first_name", "Anonymous")
            is_bot = from_obj.get("is_bot", False)
            chat_title = chat_obj.get("title", "Direct Chat")
            is_channel = chat_obj.get("type") == "channel"
            text = msg_obj.get("text", "")

            forward_from = None
            if "forward_from_chat" in msg_obj:
                forward_from = msg_obj["forward_from_chat"].get("title")

            msg = TelegramMessage(
                sender_username=sender_name,
                message_text=text,
                sender_id=str(from_obj.get("id", "0")),
                chat_title=chat_title,
                is_channel=is_channel,
                is_bot=is_bot,
                forward_from=forward_from
            )
            return self.inspect_message(msg)
        except Exception:
            text = payload.get("text") or payload.get("message", "")
            username = payload.get("username", "telegram_user")
            msg = TelegramMessage(sender_username=username, message_text=text)
            return self.inspect_message(msg)

    def print_alert(self, alert: Dict[str, Any]):
        """Prints a styled console banner for the alert."""
        print("=" * 65)
        print(f" {alert['notification_icon']} TELEGRAM GUARDIAN INTERCEPT ALERT")
        print("=" * 65)
        print(f" Chat / Group : {alert['chat']}")
        print(f" Sender       : {alert['sender']} (Bot: {alert['is_bot']})")
        print(f" Risk Score   : {alert['risk_score']}% ({alert['risk_level']})")
        print(f" Category     : {alert['category'].replace('_', ' ').title()}")
        print(f" Action       : {alert['action_taken']}")
        print(f" Message      : \"{alert['original_text'][:100]}\"")
        if alert["auto_reply_warning"]:
            print(f" Auto-Reply   :\n{alert['auto_reply_warning']}")
        print("=" * 65)


if __name__ == "__main__":
    guardian = TelegramGuardian()
    print("[*] ScamShield Telegram Guardian Active.")
    print("[*] Simulating deceptive Telegram crypto giveaway broadcast...\n")

    sample_msg = TelegramMessage(
        sender_username="Binance_VIP_QuantBot",
        sender_id="9281729",
        chat_title="SG VIP Crypto Signals & Arbitrage",
        message_text="Exclusive VIP Crypto Signals! Guaranteed 300% to 500% returns in 7 days using automated AI quant bot. Join Telegram bot @binance_yield_bot or http://binance-vault-promo.live",
        is_bot=True,
        is_channel=False
    )

    alert = guardian.inspect_message(sample_msg)
    guardian.print_alert(alert)
