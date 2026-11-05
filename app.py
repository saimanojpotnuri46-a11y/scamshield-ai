"""
ScamShield NLP Multi-Channel Defense Dashboard
Interactive Operations Center for SMS, WhatsApp Notification Guardian,
Email Phishing Scanner, Clipboard Shield, and NLP Challenge Evaluation.
"""

import os
import sys
import pandas as pd
import streamlit as st

# Configure page
st.set_page_config(
    page_title="ScamShield AI | Multi-Channel Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure project root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.pipeline import ScamShieldPipeline
from src.whatsapp_guardian import WhatsAppGuardian, WhatsAppMessage
from src.email_scanner import EmailPhishingScanner
from src.clipboard_guard import ClipboardGuard
from src.telegram_guardian import TelegramGuardian, TelegramMessage
from src.qr_scanner import QuishingScanner
from challenge.evaluate_submission import evaluate
from challenge.leaderboard import get_leaderboard_dataframe, register_submission

# Cache pipeline and guardians
@st.cache_resource
def get_engines():
    pipe = ScamShieldPipeline()
    wa = WhatsAppGuardian(pipe)
    email = EmailPhishingScanner(pipe)
    clip = ClipboardGuard(pipe)
    tg = TelegramGuardian(pipe)
    quish = QuishingScanner(pipe)
    return pipe, wa, email, clip, tg, quish

pipeline, whatsapp_guardian, email_scanner, clipboard_guard, telegram_guardian, quishing_scanner = get_engines()

# Preset Test Scenarios
SAMPLE_PRESETS = {
    "🏦 OCBC Bank Token Phishing": "OCBC Bank: Your digital token has expired today. Re-activate your access now at http://ocbc-auth-portal.online to avoid permanent account freeze.",
    "📦 SingPost Customs Fee Scam": "SingPost: Your package SG920192 is held at our distribution hub due to unpaid customs fee of $2.50. Pay fee to release: http://singpost-tracking-fees.top",
    "💼 WhatsApp Part-Time Job Scam": "Earn $200-$600 daily working from home! Simple task: like YouTube videos and review products. No experience needed. Contact WhatsApp: +65 8921 4452",
    "📈 Crypto Guaranteed 500% ROI": "Exclusive VIP Crypto Signals! Guaranteed 300% to 500% returns in 7 days using automated AI quant bot. Join Telegram @sg_crypto_admin or http://crypto-vault-multiplier.live",
    "⚖️ Police Arrest Warrant Threat": "Singapore Police Force Notice: An arrest warrant has been issued under your IC for transnational money laundering. Contact Inspector Tan immediately at +65 6712 9012",
    "💻 Microsoft Tech Support Alert": "Microsoft Security Alert: Critical Trojan virus detected on your Windows PC! Credit card details leaking. Call Toll-Free +1-800-419-0921 immediately.",
    "🟢 Genuine Bank OTP (Ham)": "Your OTP for login to OCBC Digital is 829104. Valid for 3 mins. Never share your OTP with anyone, including bank staff.",
    "🟢 Genuine Courier Delivery (Ham)": "Your package from Amazon order #112-9281928 is out for delivery today. Track in the official Amazon app.",
    "🟢 Genuine Personal SMS (Ham)": "Hey! Are we still meeting for lunch at 12:30pm tomorrow at Bugis Junction? Let me know!"
}

# Sidebar
st.sidebar.image("https://img.icons8.com/fluency/96/shield.png", width=70)
st.sidebar.title("🛡️ ScamShield AI")
st.sidebar.markdown(
    """
    **Autonomous Multi-Channel Defense**  
    Protects citizens across SMS, WhatsApp Notifications, Email Phishing, and Browser Clipboard.
    """
)
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Core Engine**: {'🟢 Ready' if pipeline.is_ready else '🔴 Off'}")
st.sidebar.markdown("**Channels Protected**:")
st.sidebar.markdown("- 💬 SMS / Smishing")
st.sidebar.markdown("- 📱 WhatsApp Notifications")
st.sidebar.markdown("- ✈️ Telegram Channel & Bot Guard")
st.sidebar.markdown("- 📧 Email Phishing & BEC")
st.sidebar.markdown("- 📋 Clipboard / Link Guard")
st.sidebar.markdown("- 📷 Quishing (QR Code Phishing)")
st.sidebar.markdown("---")
st.sidebar.caption("Inspired by Singapore ScamShield initiative. Built for cybersecurity engineers.")

# Main Header
st.title("🛡️ ScamShield Multi-Channel Fraud Defense System")
st.markdown(
    "Detect, analyze, and intercept deceptive cyber-fraud in real time across mobile and desktop workflows."
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🔍 SMS Message Scanner",
    "📱 WhatsApp Guardian",
    "✈️ Telegram Guardian",
    "📧 Email Phishing Scanner",
    "📋 Clipboard & Browser Shield",
    "📷 Quishing (QR Phishing) Audit",
    "🏆 NLP Challenge & Leaderboard",
    "🔌 Multi-Channel REST API"
])

# ==========================================
# TAB 1: SMS MESSAGE SCANNER
# ==========================================
with tab1:
    st.subheader("🔍 Interactive SMS / Message Scanner")
    st.markdown("Select a preset scenario or type any incoming suspicious message:")

    preset_choice = st.selectbox("Load Test Scenario:", ["-- Custom Input --"] + list(SAMPLE_PRESETS.keys()))
    default_text = SAMPLE_PRESETS[preset_choice] if preset_choice != "-- Custom Input --" else ""

    user_input = st.text_area(
        "Message Text to Inspect:",
        value=default_text,
        height=100,
        placeholder="e.g. URGENT: Your bank account will be frozen. Click link to verify..."
    )

    if st.button("🚀 Run Deep Scan", type="primary", key="btn_scan_sms"):
        if not user_input.strip():
            st.warning("Please enter a message.")
        else:
            with st.spinner("Analyzing message vectors and domain risk..."):
                res = pipeline.scan_message(user_input)

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("Risk Score", f"{res['risk_score']}%", res["risk_level"], delta_color="inverse" if res["is_scam"] else "normal")
            c2.metric("Classification", res["label"].upper(), res["category"].replace("_", " ").title())
            c3.metric("Scam Probability", f"{res['scam_probability'] * 100:.1f}%")

            st.progress(min(1.0, res["risk_score"] / 100.0))

            cd1, cd2 = st.columns(2)
            with cd1:
                st.markdown("#### 🚨 Social Engineering Tactics")
                if res["tactics_detected"]:
                    for tac in res["tactics_detected"]:
                        st.warning(f"**{tac['tactic']}**\n\n{tac['description']}")
                else:
                    st.success("No predatory social engineering detected.")

            with cd2:
                st.markdown("#### 🌐 Extracted URLs & Infrastructure Audit")
                if res["extracted_urls"]:
                    for u in res["extracted_urls"]:
                        st.info(f"**URL:** `{u['url']}`\n- Risk Score: **{u['url_risk_score']}/100**")
                else:
                    st.write("No external links found.")

            st.subheader("🛡️ Prescriptive Safety Checklist")
            for item in res["safety_advice"]:
                st.markdown(f"- {item}")

# ==========================================
# TAB 2: WHATSAPP NOTIFICATION GUARDIAN
# ==========================================
with tab2:
    st.subheader("📱 WhatsApp Spam & Notification Guardian")
    st.markdown(
        """
        Intercepts incoming WhatsApp notifications in real time, checks the sender against predatory
        patterns, flags group recruitment spam, and generates **instant user alert banners** and **automated warning replies**.
        """
    )

    col_wa_in, col_wa_phone = st.columns([3, 2])

    with col_wa_in:
        wa_sender_name = st.text_input("Sender Display Name:", value="Dave (Recruitment HR)")
        wa_sender_num = st.text_input("Sender Phone Number:", value="+65 8921 4452")
        wa_is_group = st.checkbox("Is Group Message?", value=True)
        wa_group_name = st.text_input("Group Name (if applicable):", value="Singapore Part-Time Job Seekers") if wa_is_group else None
        wa_body = st.text_area(
            "Incoming WhatsApp Message Body:",
            value="Hi all! Earn $300-$800 daily working from home! Simple task: like YouTube videos and review products. Daily payout via PayNow. Register: http://job-daily-income.xyz",
            height=110
        )

    with col_wa_phone:
        st.markdown("#### 📲 Simulated Mobile Notification")
        if st.button("⚡ Simulate Incoming WhatsApp Message", type="primary"):
            msg_obj = WhatsAppMessage(
                sender_name=wa_sender_name,
                sender_number=wa_sender_num,
                message_text=wa_body,
                is_group=wa_is_group,
                group_name=wa_group_name
            )
            alert = whatsapp_guardian.inspect_message(msg_obj)

            # Simulated WhatsApp Notification Card
            if alert["risk_score"] >= 50:
                st.error(
                    f"""
                    **{alert['notification_icon']} WHATSAPP INTERCEPT ALERT**  
                    **From:** {alert['sender']}  
                    **Group:** {alert.get('group_name') or 'Direct Message'}  
                    **Risk Score:** {alert['risk_score']}% ({alert['risk_level']})  
                    **Category:** {alert['category'].replace('_', ' ').title()}  
                    **Action Taken:** `{alert['action_taken']}`
                    """
                )
            else:
                st.success(
                    f"""
                    **{alert['notification_icon']} WHATSAPP NOTIFICATION (SAFE)**  
                    **From:** {alert['sender']}  
                    **Status:** Delivered normally.
                    """
                )

            if alert["auto_reply_warning"]:
                st.markdown("#### 🤖 Automated Safety Warning Response:")
                st.code(alert["auto_reply_warning"], language="text")

# ==========================================
# TAB 3: TELEGRAM GUARDIAN
# ==========================================
with tab3:
    st.subheader("✈️ Telegram Spam, Bot & Crypto Pump Guardian")
    st.markdown(
        "Monitors Telegram channel broadcasts, VIP group chats, and bot interactions for crypto manipulation and fake giveaways."
    )

    tg_col1, tg_col2 = st.columns(2)
    with tg_col1:
        tg_user = st.text_input("Telegram Username / Bot Handle:", value="@Binance_VIP_QuantBot")
        tg_is_bot = st.checkbox("Sender is Telegram Bot", value=True)
    with tg_col2:
        tg_chat = st.text_input("Channel / Group Title:", value="SG VIP Crypto Signals & Arbitrage")
        tg_is_channel = st.checkbox("Is Public Channel Broadcast", value=False)

    tg_text = st.text_area(
        "Telegram Message Body:",
        value="Exclusive VIP Crypto Signals! Guaranteed 300% to 500% returns in 7 days using automated AI quant bot. Join Telegram bot @binance_yield_bot or http://binance-vault-promo.live",
        height=100
    )

    if st.button("✈️ Inspect Telegram Message", type="primary", key="btn_tg"):
        msg = TelegramMessage(
            sender_username=tg_user,
            message_text=tg_text,
            chat_title=tg_chat,
            is_bot=tg_is_bot,
            is_channel=tg_is_channel
        )
        tg_alert = telegram_guardian.inspect_message(msg)

        tc1, tc2, tc3 = st.columns(3)
        tc1.metric("Risk Score", f"{tg_alert['risk_score']}%", tg_alert["risk_level"], delta_color="inverse" if tg_alert["risk_score"] >= 50 else "normal")
        tc2.metric("Typology", tg_alert["category"].replace("_", " ").title())
        tc3.metric("Action Taken", tg_alert["action_taken"])

        st.progress(min(1.0, tg_alert["risk_score"] / 100.0))

        if tg_alert["auto_reply_warning"]:
            st.markdown("#### 🤖 Automated Supergroup Safety Warning:")
            st.code(tg_alert["auto_reply_warning"], language="text")

# ==========================================
# TAB 4: EMAIL PHISHING SCANNER
# ==========================================
with tab4:
    st.subheader("📧 Email Phishing & Corporate Impersonation Scanner")
    st.markdown(
        "Detects Executive Spoofing (CEO Fraud), fake invoices, reply-to domain mismatches, and credential theft emails."
    )

    em_sender = st.text_input("Sender Email Address:", value="hr-payroll@dbs-corp-service.xyz")
    em_reply_to = st.text_input("Reply-To Header:", value="shadow-account@gmail.com")
    em_subject = st.text_input("Subject Line:", value="URGENT: Payroll Verification & IRAS Tax Settlement")
    em_body = st.text_area(
        "Email Body Content:",
        value="Dear Employee,\n\nOur annual IRAS audit detected an outstanding tax penalty of $1,420 under your account. Failure to verify and settle within 24 hours will result in salary freeze and court subpoena.\n\nSettle invoice immediately at: http://iras-tax-clearance.vip\n\nFinance Department",
        height=140
    )

    if st.button("🛡️ Inspect Email Security", type="primary"):
        em_res = email_scanner.scan_email(
            sender_email=em_sender,
            subject=em_subject,
            body=em_body,
            reply_to=em_reply_to
        )

        st.markdown("---")
        em_c1, em_c2, em_c3 = st.columns(3)
        em_c1.metric("Email Risk Score", f"{em_res['email_risk_score']}%", em_res["threat_tier"])
        em_c2.metric("Domain Mismatch", "YES (Spoofed)" if em_res["domain_mismatch"] else "NO")
        em_c3.metric("Phishing Verdict", "BLOCKED" if em_res["is_phishing"] else "CLEAN")

        if em_res["flags"]:
            st.error("🚨 **Specific Anomalies Identified:**")
            for flag in em_res["flags"]:
                st.markdown(f"- ⚠️ {flag}")

        if em_res["urls"]:
            st.warning("🌐 **Suspicious Embedded Links:**")
            for u in em_res["urls"]:
                st.markdown(f"- Link: `{u['url']}` (Risk: **{u['url_risk_score']}/100**)")

# ==========================================
# TAB 5: CLIPBOARD & BROWSER SHIELD
# ==========================================
with tab5:
    st.subheader("📋 Real-Time Clipboard & Browser Shield")
    st.markdown(
        """
        Monitors text or links copied from web browsers, WhatsApp Web, or Telegram.
        Automatically intercepts dangerous clipboard payloads before the user navigates or pastes.
        """
    )

    clip_input = st.text_area(
        "Test Clipboard Copy Action (Paste or type text copied from browser/chat):",
        value="SingPost: Your package is held at terminal hub due to unpaid customs fee of $2.50. Pay fee: http://singpost-tracking-fees.top",
        height=90
    )

    if st.button("⚡ Test Clipboard Intercept", type="primary"):
        clip_alert = clipboard_guard.inspect_clipboard_text(clip_input)
        if clip_alert:
            st.error(
                f"""
                ### 📋 CLIPBOARD GUARDIAN INTERCEPT!
                **Warning:** {clip_alert['warning']}  
                **Risk Score:** {clip_alert['risk_score']}% ({clip_alert['risk_level']})  
                **Category:** {clip_alert['category'].replace('_', ' ').title()}  
                
                🛑 **Recommendation:** DO NOT paste or open any embedded URLs in your web browser.
                """
            )
        else:
            st.success("✅ Clipboard content analyzed: No phishing or scam patterns detected.")

# ==========================================
# TAB 6: QUISHING (QR PHISHING) AUDIT
# ==========================================
with tab6:
    st.subheader("📷 Quishing (QR Code Phishing) & Visual Lure Scanner")
    st.markdown(
        "Audits physical and digital QR code payloads, payment stickers (PayNow / SGQR impersonation), and parking fee scams."
    )

    qr_col1, qr_col2 = st.columns(2)
    with qr_col1:
        qr_context = st.selectbox(
            "Source Context:",
            [
                "Tampered sticker over public parking ticket machine",
                "Physical mailer / Fake official utility bill",
                "Retail storefront PayNow / SGQR overlay sticker",
                "WhatsApp / Telegram image attachment",
                "Unsolicited parcel delivery note sticker"
            ]
        )
    with qr_col2:
        qr_loc = st.text_input("Incident Location Tag:", value="Tampines St 21 Public Carpark")

    qr_payload = st.text_area(
        "Decoded QR Code URL or Text Payload:",
        value="Scan to settle unpaid HDB parking fine of $12.00 immediately: http://hdb-parking-notice.top/paynow",
        height=90
    )

    if st.button("📷 Audit QR Code Payload", type="primary", key="btn_qr"):
        qr_report = quishing_scanner.scan_qr_payload(
            payload_text=qr_payload,
            source_context=qr_context,
            location_tag=qr_loc
        )

        qc1, qc2, qc3 = st.columns(3)
        qc1.metric("Risk Score", f"{qr_report['risk_score']}%", qr_report["threat_level"], delta_color="inverse" if qr_report["risk_score"] >= 50 else "normal")
        qc2.metric("Category", qr_report["category"].replace("_", " ").title())
        qc3.metric("Action Required", qr_report["action_recommendation"])

        st.progress(min(1.0, qr_report["risk_score"] / 100.0))

        if qr_report["url_security_audit"]:
            st.markdown("#### 🌐 Domain Security Audit:")
            for audit in qr_report["url_security_audit"]:
                st.error(f"**Domain:** `{audit['domain']}` | Risk Score: **{audit['url_risk_score']}/100**")
                for r in audit["reasons"]:
                    st.write(f"- ⚠️ {r}")

        st.subheader("🛡️ Quishing Prevention Safety Guidance:")
        for advice in qr_report["safety_checklist"]:
            st.info(f"• {advice}")

# ==========================================
# TAB 7: NLP CHALLENGE & LEADERBOARD
# ==========================================
with tab7:
    st.subheader("🏆 The ScamShield NLP Challenge & Live Leaderboard")
    st.markdown(
        """
        The **ScamShield NLP Challenge** is an open competitive benchmark to evaluate machine learning
        and deep learning architectures against real-world smishing, social engineering, and fraud typologies.
        """
    )

    c1, c2, c3 = st.columns(3)
    c1.info("🎯 **Task 1: Binary Classification**\n\nClassify `ham` vs `scam`.")
    c2.info("🏷️ **Task 2: Typology Classification**\n\nDetect 8 granular fraud vectors.")
    c3.info("📐 **Task 3: Probability Calibration**\n\nOutput calibrated Brier scores.")

    st.markdown("---")
    st.subheader("📄 IEEE Research Paper & Author Guidelines")
    col_doc1, col_doc2 = st.columns([2, 2])
    with col_doc1:
        ieee_doc_path = os.path.join(ROOT_DIR, "ScamShield_IEEE_Research_Paper.docx")
        if os.path.exists(ieee_doc_path):
            with open(ieee_doc_path, "rb") as f_doc:
                st.download_button(
                    "📥 Download IEEE Research Paper (.docx)",
                    data=f_doc.read(),
                    file_name="ScamShield_IEEE_Research_Paper.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
    with col_doc2:
        st.info("Formatted strictly in IEEE Conference format (Times New Roman, Roman headings, Table I, 15 citations).")

    st.markdown("---")
    st.subheader("📤 Submit Model Predictions to Official Leaderboard")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        team_input = st.text_input("Team / Researcher Name:", value="Alpha AI Researchers")
    with col_t2:
        model_input = st.text_input("Model Architecture:", value="Fine-Tuned DeBERTa-v3 + Heuristic Union")

    sub_file = st.file_uploader("Upload your submission.csv (or leave empty to evaluate baseline):", type=["csv"], key="uploader_sub_live")

    if st.button("🏅 Evaluate & Update Leaderboard", type="primary"):
        target_sub = None
        if sub_file is not None:
            temp_path = os.path.join(ROOT_DIR, "challenge", "temp_upload.csv")
            with open(temp_path, "wb") as f:
                f.write(sub_file.getvalue())
            target_sub = temp_path
        elif os.path.exists(os.path.join(ROOT_DIR, "challenge", "submission.csv")):
            target_sub = os.path.join(ROOT_DIR, "challenge", "submission.csv")

        if target_sub:
            gt_path = os.path.join(ROOT_DIR, "data", "test_ground_truth.csv")
            try:
                metrics = evaluate(target_sub, gt_path, team_name=team_input, model_name=model_input)
                st.success(f"🎉 Evaluation Complete! Composite Score: {metrics['composite_score']} / 100.00")
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Binary Macro F1", f"{metrics['binary_macro_f1'] * 100:.2f}%")
                m2.metric("Multiclass Macro F1", f"{metrics['multiclass_macro_f1'] * 100:.2f}%")
                m3.metric("Binary Accuracy", f"{metrics['binary_accuracy'] * 100:.2f}%")
                m4.metric("Brier Score", f"{metrics['brier_score']:.4f}")
            except Exception as ex:
                st.error(f"Evaluation error: {str(ex)}")

    st.markdown("---")
    st.subheader("🥇 Official Benchmark Leaderboard Rankings")
    leaderboard_df = get_leaderboard_dataframe()
    st.dataframe(leaderboard_df, use_container_width=True)

# ==========================================
# TAB 8: MULTI-CHANNEL API DOCS
# ==========================================
with tab8:
    st.subheader("🔌 Multi-Channel REST API Integration")
    st.markdown("Easily integrate ScamShield into WhatsApp Business, Telegram Bots, Email Gateways, or Quishing Scanners:")

    st.markdown("#### 1. WhatsApp Webhook Call (Python)")
    st.code(
        """import requests

payload = {
    "sender_name": "Unknown Recruiter",
    "sender_number": "+65 8921 4452",
    "message_text": "Earn $500 daily liking YouTube videos! Message HR now."
}

res = requests.post("http://localhost:8000/whatsapp/scan", json=payload)
data = res.json()
print("Action Taken:", data["action_taken"])
print("Auto-Reply:", data["auto_reply_warning"])
""",
        language="python"
    )

    st.markdown("#### 2. Telegram Bot Webhook Call (Python)")
    st.code(
        """import requests

payload = {
    "sender_username": "crypto_quant_bot",
    "message_text": "Exclusive VIP Crypto Signals! Guaranteed 500% ROI in 7 days: http://crypto-vault.xyz",
    "is_bot": True,
    "chat_title": "VIP Trading Group"
}

res = requests.post("http://localhost:8000/telegram/scan", json=payload)
data = res.json()
print("Risk Score:", data["risk_score"])
print("Action Taken:", data["action_taken"])
""",
        language="python"
    )

    st.markdown("#### 3. Quishing (QR Phishing) Audit Call (cURL)")
    st.code(
        """curl -X POST "http://localhost:8000/quishing/scan" \\
     -H "Content-Type: application/json" \\
     -d '{"payload_text": "Scan QR to pay parking fine: http://hdb-parking-notice.top/paynow", "source_context": "Physical parking meter sticker"}'
""",
        language="bash"
    )

    st.markdown("#### 4. Email Phishing Inspection Call (cURL)")
    st.code(
        """curl -X POST "http://localhost:8000/email/scan" \\
     -H "Content-Type: application/json" \\
     -d '{"sender_email": "hr@dbs-corp.xyz", "subject": "Urgent Tax Hold", "body": "Verify account: http://iras-tax.vip"}'
""",
        language="bash"
    )
