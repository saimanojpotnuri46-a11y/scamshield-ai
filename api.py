"""
ScamShield FastAPI REST Service
Exposes endpoints for message scanning, WhatsApp webhooks, email inspection,
and challenge evaluation.
"""

import os
import sys
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

# Ensure package path is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline import ScamShieldPipeline
from src.whatsapp_guardian import WhatsAppGuardian, WhatsAppMessage
from src.email_scanner import EmailPhishingScanner
from src.clipboard_guard import ClipboardGuard
from src.telegram_guardian import TelegramGuardian, TelegramMessage
from src.qr_scanner import QuishingScanner

app = FastAPI(
    title="ScamShield NLP Multi-Channel Defense API",
    description="Real-time fraud prevention across SMS, WhatsApp Notifications, Telegram, Email, Clipboard, and QR Quishing.",
    version="2.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engines
pipeline = None
whatsapp_guardian = None
email_scanner = None
clipboard_guard = None
telegram_guardian = None
quishing_scanner = None

@app.on_event("startup")
def startup_event():
    global pipeline, whatsapp_guardian, email_scanner, clipboard_guard, telegram_guardian, quishing_scanner
    print("Initializing ScamShield Pipeline and Guardians...")
    pipeline = ScamShieldPipeline()
    whatsapp_guardian = WhatsAppGuardian(pipeline)
    email_scanner = EmailPhishingScanner(pipeline)
    clipboard_guard = ClipboardGuard(pipeline)
    telegram_guardian = TelegramGuardian(pipeline)
    quishing_scanner = QuishingScanner(pipeline)

class ScanRequest(BaseModel):
    text: str = Field(..., description="Message text to inspect", min_length=1)

class BatchScanRequest(BaseModel):
    texts: List[str] = Field(..., description="List of messages to inspect", max_items=100)

class WhatsAppScanRequest(BaseModel):
    sender_name: str = "Unknown Sender"
    sender_number: str = "+65 0000 0000"
    message_text: str = Field(..., min_length=1)
    is_group: bool = False
    group_name: Optional[str] = None

class EmailScanRequest(BaseModel):
    sender_email: str = Field(..., description="Sender's email address")
    subject: str = Field(..., description="Email Subject line")
    body: str = Field(..., description="Email body content")
    reply_to: Optional[str] = None

class ClipboardScanRequest(BaseModel):
    text: str = Field(..., description="Copied text or URL from clipboard")

class TelegramScanRequest(BaseModel):
    sender_username: str = "telegram_user"
    message_text: str = Field(..., min_length=1)
    chat_title: Optional[str] = "Direct Message"
    is_bot: bool = False
    is_channel: bool = False
    forward_from: Optional[str] = None

class QuishingScanRequest(BaseModel):
    payload_text: str = Field(..., description="Decoded QR payload or URL", min_length=1)
    source_context: str = "Physical Sticker / QR Code"
    location_tag: Optional[str] = "Public Location"

@app.get("/")
def root():
    return {
        "service": "ScamShield NLP API",
        "status": "online",
        "version": "2.5.0",
        "supported_channels": ["SMS", "WhatsApp Notifications", "Telegram", "Email Phishing", "Clipboard", "QR Quishing"],
        "endpoints": {
            "health": "/health",
            "categories": "/categories",
            "scan": "POST /scan",
            "whatsapp_scan": "POST /whatsapp/scan",
            "whatsapp_webhook": "POST /whatsapp/webhook",
            "email_scan": "POST /email/scan",
            "clipboard_check": "POST /clipboard/check"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": pipeline is not None and pipeline.is_ready,
        "classes": pipeline.model.classes_multiclass.tolist() if pipeline and pipeline.is_ready else []
    }

@app.get("/categories")
def get_categories():
    return {
        "categories": [
            {"id": "legitimate", "name": "Legitimate / Ham", "desc": "Genuine user messages, regular OTP notifications, appointment reminders."},
            {"id": "bank_impersonation", "name": "Banking Fraud", "desc": "Spoofing banks (DBS, OCBC, UOB, Chase) with fake token expiration or unauthorized login alerts."},
            {"id": "delivery_fraud", "name": "Delivery & Parcel Fraud", "desc": "Spoofing SingPost, DHL, FedEx with fake customs duty or invalid address links."},
            {"id": "job_scam", "name": "Recruitment & Job Scam", "desc": "Fake high-paying remote video liking/rating tasks requesting WhatsApp/Telegram contact."},
            {"id": "investment_crypto", "name": "Investment & Crypto Fraud", "desc": "Guaranteed high-yield investment schemes, bogus crypto giveaways, AI bot trading."},
            {"id": "lottery_reward", "name": "Lottery & Lucky Draw Bait", "desc": "Fake prize claims, uncollected government grant payouts, supermarket gift vouchers."},
            {"id": "government_police", "name": "Authority Impersonation", "desc": "Threatening arrest warrants, tax fines (IRAS), court summons to instill panic."},
            {"id": "tech_support", "name": "Tech Support Scam", "desc": "Fake virus alerts claiming Windows/Apple ID is hacked with toll-free helpline numbers."}
        ]
    }

@app.post("/scan")
def scan_single(req: ScanRequest):
    if not pipeline or not pipeline.is_ready:
        raise HTTPException(status_code=503, detail="Pipeline initializing.")
    return pipeline.scan_message(req.text)

@app.post("/batch-scan")
def scan_batch(req: BatchScanRequest):
    if not pipeline or not pipeline.is_ready:
        raise HTTPException(status_code=503, detail="Pipeline initializing.")
    return pipeline.batch_scan(req.texts)

# ----------------- APPLICATION 1: WHATSAPP GUARDIAN ENDPOINTS -----------------
@app.post("/whatsapp/scan")
def scan_whatsapp_message(req: WhatsAppScanRequest):
    """Inspects an incoming WhatsApp notification."""
    if not whatsapp_guardian:
        raise HTTPException(status_code=503, detail="WhatsApp Guardian initializing.")
    msg = WhatsAppMessage(
        sender_name=req.sender_name,
        sender_number=req.sender_number,
        message_text=req.message_text,
        is_group=req.is_group,
        group_name=req.group_name
    )
    return whatsapp_guardian.inspect_message(msg)

@app.post("/whatsapp/webhook")
def whatsapp_webhook(payload: Dict[str, Any] = Body(...)):
    """Receives Meta WhatsApp Cloud API or Twilio incoming webhooks."""
    if not whatsapp_guardian:
        raise HTTPException(status_code=503, detail="WhatsApp Guardian initializing.")
    return whatsapp_guardian.process_webhook_payload(payload)

# ----------------- APPLICATION 2: EMAIL & CLIPBOARD GUARDIAN -----------------
@app.post("/email/scan")
def scan_email_message(req: EmailScanRequest):
    """Inspects email for BEC, domain spoofing, and malicious attachments/links."""
    if not email_scanner:
        raise HTTPException(status_code=503, detail="Email Scanner initializing.")
    return email_scanner.scan_email(
        sender_email=req.sender_email,
        subject=req.subject,
        body=req.body,
        reply_to=req.reply_to
    )

@app.post("/clipboard/check")
def check_clipboard(req: ClipboardScanRequest):
    """Fast check for clipboard copies or URL clicks."""
    if not clipboard_guard:
        raise HTTPException(status_code=503, detail="Clipboard Guard initializing.")
    alert = clipboard_guard.inspect_clipboard_text(req.text)
    return {"has_threat": alert is not None, "alert": alert}

# ----------------- APPLICATION 4: TELEGRAM GUARDIAN -----------------
@app.post("/telegram/scan")
def scan_telegram_message(req: TelegramScanRequest):
    """Inspects an incoming Telegram message, broadcast, or bot interaction."""
    if not telegram_guardian:
        raise HTTPException(status_code=503, detail="Telegram Guardian initializing.")
    msg = TelegramMessage(
        sender_username=req.sender_username,
        message_text=req.message_text,
        chat_title=req.chat_title,
        is_bot=req.is_bot,
        is_channel=req.is_channel,
        forward_from=req.forward_from
    )
    return telegram_guardian.inspect_message(msg)

@app.post("/telegram/webhook")
def telegram_webhook(payload: Dict[str, Any] = Body(...)):
    """Receives Telegram Bot API updates webhook."""
    if not telegram_guardian:
        raise HTTPException(status_code=503, detail="Telegram Guardian initializing.")
    return telegram_guardian.parse_telegram_webhook(payload)

# ----------------- APPLICATION 5: QUISHING (QR PHISHING) -----------------
@app.post("/quishing/scan")
def scan_quishing_payload(req: QuishingScanRequest):
    """Audits decoded QR codes, stickers, and visual phishing links."""
    if not quishing_scanner:
        raise HTTPException(status_code=503, detail="Quishing Scanner initializing.")
    return quishing_scanner.scan_qr_payload(
        payload_text=req.payload_text,
        source_context=req.source_context,
        location_tag=req.location_tag
    )
