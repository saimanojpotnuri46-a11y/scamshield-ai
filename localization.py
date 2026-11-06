"""
ScamShield Localization and Language Preferences Engine
======================================================
Provides multi-language translation, language preference persistence,
language auto-detection, and localized defensive advisory templates
across English, Chinese (简体中文), Malay (Bahasa Melayu), Tamil (தமிழ்), and Hindi (हिन्दी).
"""

import os
import json
import re
from typing import Dict, List, Any, Optional

# Supported Languages Configuration
SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "flag": "🇬🇧",
        "region": "Singapore / Global",
        "description": "Standard English cybersecurity terminology"
    },
    "zh": {
        "code": "zh",
        "name": "Chinese (Simplified)",
        "native_name": "简体中文",
        "flag": "🇨🇳",
        "region": "Singapore (华语) / International",
        "description": "本地化反诈术语与预设案例 (Chinese Fraud Defense)"
    },
    "ms": {
        "code": "ms",
        "name": "Malay",
        "native_name": "Bahasa Melayu",
        "flag": "🇲🇾",
        "region": "Singapore (Melayu) / Malaysia",
        "description": "Terminologi pertahanan penipuan siber Bahasa Melayu"
    },
    "ta": {
        "code": "ta",
        "name": "Tamil",
        "native_name": "தமிழ்",
        "flag": "🇮🇳",
        "region": "Singapore (தமிழ்) / South Asia",
        "description": "மோசடி எதிர்ப்பு பாதுகாப்பு சொற்கள் (Tamil Cyber Defense)"
    },
    "hi": {
        "code": "hi",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "flag": "🇮🇳",
        "region": "South Asia / Global Diaspora",
        "description": "साइबर धोखाधड़ी रक्षा शब्दावली (Hindi Cyber Defense)"
    }
}

DEFAULT_LANGUAGE = "en"

# Path to persistent preferences storage
PREFERENCES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "preferences.json"
)

def load_user_preferences() -> Dict[str, Any]:
    """Loads saved language and localization preferences from disk."""
    default_prefs = {
        "preferred_language": DEFAULT_LANGUAGE,
        "auto_detect_language": True,
        "auto_reply_mode": "preferred",  # "preferred", "en", "bilingual"
        "alert_verbosity": "standard",
        "enable_sound_alerts": True
    }
    if os.path.exists(PREFERENCES_FILE):
        try:
            with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default_prefs.update(saved)
        except Exception:
            pass
    return default_prefs

def save_user_preferences(prefs: Dict[str, Any]) -> bool:
    """Saves language preferences persistently to disk."""
    try:
        os.makedirs(os.path.dirname(PREFERENCES_FILE), exist_ok=True)
        current = load_user_preferences()
        current.update(prefs)
        with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def get_current_language() -> str:
    """Returns currently selected preferred language code."""
    prefs = load_user_preferences()
    lang = prefs.get("preferred_language", DEFAULT_LANGUAGE)
    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

def set_current_language(lang_code: str) -> bool:
    """Updates preferred language setting."""
    if lang_code in SUPPORTED_LANGUAGES:
        return save_user_preferences({"preferred_language": lang_code})
    return False

def detect_language(text: str) -> str:
    """
    Lightweight heuristic language detector for incoming messages:
    Detects Chinese, Tamil, Hindi, Malay, or defaults to English.
    """
    if not text or not isinstance(text, str):
        return DEFAULT_LANGUAGE
    
    # Check for Chinese characters
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh"
    
    # Check for Tamil script
    if re.search(r"[\u0b80-\u0bff]", text):
        return "ta"
        
    # Check for Devanagari (Hindi) script
    if re.search(r"[\u0900-\u097f]", text):
        return "hi"
        
    # Check for distinct Malay vocabulary
    malay_keywords = [
        r"\bakaun\b", r"\bsegera\b", r"\btindakan\b", r"\bpenipuan\b",
        r"\bwaran\b", r"\bhadiah\b", r"\bbungkusan\b", r"\bdisahkan\b",
        r"\bperbankan\b", r"\bsemak\b", r"\bkastam\b", r"\bkemas\s*kini\b"
    ]
    text_lower = text.lower()
    malay_matches = sum(1 for kw in malay_keywords if re.search(kw, text_lower))
    if malay_matches >= 2:
        return "ms"
        
    return "en"

# ==============================================================================
# LOCALIZED PRESET SCENARIOS
# ==============================================================================

SAMPLE_PRESETS_BY_LANG: Dict[str, Dict[str, str]] = {
    "en": {
        "🏦 OCBC Bank Token Phishing": "OCBC Bank: Your digital token has expired today. Re-activate your access now at http://ocbc-auth-portal.online to avoid permanent account freeze.",
        "📦 SingPost Customs Fee Scam": "SingPost: Your package SG920192 is held at our distribution hub due to unpaid customs fee of $2.50. Pay fee to release: http://singpost-tracking-fees.top",
        "💼 WhatsApp Part-Time Job Scam": "Earn $200-$600 daily working from home! Simple task: like YouTube videos and review products. No experience needed. Contact WhatsApp: +65 8921 4452",
        "📈 Crypto Guaranteed 500% ROI": "Exclusive VIP Crypto Signals! Guaranteed 300% to 500% returns in 7 days using automated AI quant bot. Join Telegram @sg_crypto_admin or http://crypto-vault-multiplier.live",
        "⚖️ Police Arrest Warrant Threat": "Singapore Police Force Notice: An arrest warrant has been issued under your IC for transnational money laundering. Contact Inspector Tan immediately at +65 6712 9012",
        "💻 Microsoft Tech Support Alert": "Microsoft Security Alert: Critical Trojan virus detected on your Windows PC! Credit card details leaking. Call Toll-Free +1-800-419-0921 immediately.",
        "🟢 Genuine Bank OTP (Ham)": "Your OTP for login to OCBC Digital is 829104. Valid for 3 mins. Never share your OTP with anyone, including bank staff.",
        "🟢 Genuine Courier Delivery (Ham)": "Your package from Amazon order #112-9281928 is out for delivery today. Track in the official Amazon app.",
        "🟢 Genuine Personal SMS (Ham)": "Hey! Are we still meeting for lunch at 12:30pm tomorrow at Bugis Junction? Let me know!"
    },
    "zh": {
        "🏦 华侨银行 (OCBC) 电子令牌失效钓鱼": "华侨银行紧急通知：您的数字安全令牌已于今日失效。请立即登录 http://ocbc-auth-portal.online 重新激活，否则您的账户将在2小时内被永久冻结。",
        "📦 新加坡邮政 (SingPost) 关税未付诈骗": "新加坡邮政：您的包裹 SG920192 因欠付海关清关关税 $2.50 元已被暂扣。请立即点击支付以放行包裹：http://singpost-tracking-fees.top",
        "💼 WhatsApp 兼职点赞日赚$500诈骗": "居家兼职诚招人员！每天轻松点赞YouTube视频和评测商品，日赚$200-$600新币，当日PayNow结算。无需经验，立即添加WhatsApp: +65 8921 4452",
        "📈 虚拟货币量化保本高收益陷阱": "内部VIP加密货币投资！AI量化机器人交易，7天保证300%-500%无风险超高回报。立即加入Telegram官方频道 @sg_crypto_admin 或访问 http://crypto-vault-multiplier.live",
        "⚖️ 警察部队洗钱逮捕令威胁": "新加坡警察部队通知：因涉嫌特大跨国非法洗钱犯罪，已签发针对您身份证的紧急逮捕令。请立即致电陈警官接受调查：+65 6712 9012",
        "💻 微软安全中心电脑病毒警报": "微软紧急安全中心：检测到您的Windows电脑感染特洛伊木马，银行卡密码正在泄露！请立刻致电免费支持电话 +1-800-419-0921 进行修复。",
        "🟢 真实银行动态口令短信 (正常安全)": "您登录华侨银行数字账户的动态密码(OTP)为 829104。有效期3分钟。请勿向任何人透露此密码（包括银行工作人员）。",
        "🟢 真实电商包裹派送通知 (正常安全)": "您在亚马逊购买的订单 #112-9281928 正在派送中，预计今日送达。可通过亚马逊官方应用查看物流进度。",
        "🟢 真实朋友日常联络短信 (正常安全)": "嗨！我们明天中午12点半在武吉士白沙浮广场吃午饭的安排不变吧？收到请回复我哦！"
    },
    "ms": {
        "🏦 Phishing Token Bank OCBC Dinyahaktif": "Bank OCBC: Token digital anda telah tamat tempoh hari ini. Aktifkan semula akses anda sekarang di http://ocbc-auth-portal.online untuk mengelakkan akaun anda dibekukan serta-merta.",
        "📦 SingPost Bayaran Cukai Kastam Tertunggak": "SingPost: Bungkusan anda SG920192 ditahan di pusat agihan kerana cukai kastam belum dibayar sebanyak $2.50. Buat bayaran segera untuk pelepasan: http://singpost-tracking-fees.top",
        "💼 Tawaran Kerja Sambilan WhatsApp $300 Sehari": "Jana $200-$600 sehari bekerja dari rumah! Tugas mudah: tonton dan like video YouTube. Pembayaran harian melalui PayNow. Hubungi WhatsApp: +65 8921 4452",
        "📈 Isyarat Kripto Pulangan Dijamin 500%": "Isyarat Kripto VIP Eksklusif! Jaminan pulangan 300% hingga 500% dalam masa 7 hari menggunakan bot AI kuantitatif. Sertai Telegram @sg_crypto_admin atau http://crypto-vault-multiplier.live",
        "⚖️ Amaran Waran Tangkap Polis SPF": "Notis Pasukan Polis Singapura: Waran tangkap telah dikeluarkan atas nombor kad pengenalan anda kerana terlibat dalam penggubahan wang haram. Hubungi Inspektor Tan segera di +65 6712 9012",
        "💻 Amaran Sokongan Teknikal Microsoft": "Amaran Keselamatan Microsoft: Virus Trojan kritikal dikesan pada komputer anda! Maklumat kad kredit anda terdedah. Hubungi Talian Bebas Tol +1-800-419-0921 segera.",
        "🟢 SMS OTP Bank Yang Sah (Selamat)": "Nombor OTP anda untuk log masuk ke OCBC Digital ialah 829104. Sah selama 3 minit. Jangan sesekali berkongsi OTP ini dengan sesiapa pun.",
        "🟢 Penghantaran Bungkusan Pos Sah (Selamat)": "Bungkusan pesanan Amazon anda #112-9281928 sedang dihantar hari ini. Sila jejaki melalui aplikasi rasmi Amazon.",
        "🟢 Mesej Peribadi Sah (Selamat)": "Hai! Kita masih jumpa untuk makan tengah hari esok pukul 12:30 tengah hari di Bugis Junction kan? Beritahu saya ya!"
    },
    "ta": {
        "🏦 வங்கி டோக்கன் முடக்கம் & போலி இணைப்பு": "OCBC வங்கி: உங்கள் டிஜிட்டல் டோக்கன் காலாவதியாகிவிட்டது. கணக்கு முடக்கப்படுவதைத் தவிர்க்க http://ocbc-auth-portal.online இல் உடனே புதுப்பிக்கவும்.",
        "📦 பார்சல் சுங்க வரி செலுத்துதல் மோசடி": "SingPost: உங்கள் பார்சல் SG920192 க்கான சுங்க கட்டணம் $2.50 நிலுவையில் உள்ளதால் நிறுத்தி வைக்கப்பட்டுள்ளது. விடுவிக்க கட்டணம் செலுத்தவும்: http://singpost-tracking-fees.top",
        "💼 பகுதி நேர வேலை வாய்ப்பு தினசரி $500 மோசடி": "வீட்டிலிருந்தே தினமும் $200 முதல் $600 வரை சம்பாதிக்கலாம்! YouTube வீடியோக்களை லைக் செய்யவும். அனுபவம் தேவையில்லை. வாட்ஸ்அப்பில் தொடர்பு கொள்ளவும்: +65 8921 4452",
        "📈 கிரிப்டோ 500% உத்தரவாத லாப மோசடி": "விஐபி கிரிப்டோ சிக்னல்கள்! 7 நாட்களில் 300% முதல் 500% வரை உத்தரவாத லாபம். டெலிகிராமில் இணையுங்கள் @sg_crypto_admin அல்லது http://crypto-vault-multiplier.live",
        "⚖️ காவல்துறை கைது ஆணை மிரட்டல்": "சிங்கப்பூர் காவல்துறை அறிவிப்பு: பணமோசடி வழக்கில் உங்கள் மீது கைது ஆணை பிறப்பிக்கப்பட்டுள்ளது. உடனே ஆய்வாளர் டானை +65 6712 9012 இல் அழைக்கவும்.",
        "🟢 உண்மையான வங்கி OTP செய்தி (பாதுகாப்பானது)": "OCBC டிஜிட்டல் உள்நுழைவிற்கான உங்கள் OTP எண் 829104. 3 நிமிடங்கள் மட்டுமே செல்லும். யாருடனும் OTP-ஐ பகிர வேண்டாம்.",
        "🟢 உண்மையான கூரியர் விநியோக அறிவிப்பு (பாதுகாப்பானது)": "உங்கள் அமேசான் ஆர்டர் #112-9281928 இன்று விநியோகிக்கப்படும். அமேசான் செயலியில் கண்காணிக்கவும்."
    },
    "hi": {
        "🏦 बैंक डिजिटल टोकन सस्पेंशन व फर्जी लिंक": "OCBC बैंक: आपका डिजिटल सुरक्षा टोकन आज समाप्त हो गया है। स्थायी खाता ब्लॉक से बचने के लिए अभी http://ocbc-auth-portal.online पर लॉगिन कर पुनः सक्रिय करें।",
        "📦 सिंगपोस्ट कस्टम्स ड्यूटी बकाया पार्सल स्कैम": "SingPost: कस्टम शुल्क $2.50 बकाया होने के कारण आपका पार्सल SG920192 रोका गया है। पार्सल रिलीज कराने के लिए तुरंत भुगतान करें: http://singpost-tracking-fees.top",
        "💼 वर्क फ्रॉम होम पार्ट टाइम जॉब फर्जीवाड़ा": "घर बैठे रोजाना ₹15,000 - ₹30,000 कमाएं! केवल यूट्यूब वीडियो लाइक करें और रिव्यू दें। कोई अनुभव आवश्यक नहीं। व्हाट्सएप पर संपर्क करें: +65 8921 4452",
        "📈 क्रिप्टो गारंटीड 500% रिटर्न पोंजी स्कीम": "एक्सक्लूसिव वीआईपी क्रिप्टो सिग्नल्स! एआई बॉट द्वारा 7 दिनों में 300% से 500% गारंटीड रिटर्न। तुरंत टेलीग्राम चैनल @sg_crypto_admin या http://crypto-vault-multiplier.live पर जुड़ें।",
        "⚖️ पुलिस अरेस्ट वारंट व मनी लॉन्ड्रिंग धमकी": "सिंगापुर पुलिस बल नोटिस: मनी लॉन्ड्रिंग मामले में आपके पहचान पत्र पर गिरफ्तारी वारंट जारी हुआ है। तुरंत इंस्पेक्टर टैन से +65 6712 9012 पर संपर्क करें।",
        "💻 माइक्रोसॉफ्ट सुरक्षा चेतावनी ट्रोजन वायरस": "माइक्रोसॉफ्ट सिक्योरिटी: आपके कंप्यूटर में गंभीर ट्रोजन वायरस पाया गया है! पासवर्ड व कार्ड चोरी हो रहे हैं। तुरंत टोल-फ्री +1-800-419-0921 पर कॉल करें।",
        "🟢 वास्तविक बैंक ओटीपी संदेश (सुरक्षित)": "OCBC बैंक में लॉगिन के लिए आपका ओटीपी 829104 है। यह 3 मिनट तक वैध है। अपना ओटीपी कभी किसी के साथ साझा न करें।",
        "🟢 पार्सल डिलीवरी डिलीवरी ट्रैकिंग (सुरक्षित)": "आपका अमेज़न ऑर्डर #112-9281928 आज डिलीवरी के लिए निकल चुका है। आधिकारिक ऐप में ट्रैक करें।"
    }
}

# ==============================================================================
# UI TRANSLATION STRINGS
# ==============================================================================

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # App Header & Metadata
        "app_title": "🛡️ ScamShield Multi-Channel Fraud Defense System",
        "app_subtitle": "Detect, analyze, and intercept deceptive cyber-fraud in real time across mobile and desktop workflows.",
        "sidebar_title": "🛡️ ScamShield AI",
        "sidebar_desc": "**Autonomous Multi-Channel Defense**\nProtects citizens across SMS, WhatsApp Notifications, Telegram, Email Phishing, and Clipboard.",
        "core_engine": "Core Engine",
        "channels_protected": "Channels Protected:",
        "channel_sms": "💬 SMS / Smishing",
        "channel_wa": "📱 WhatsApp Notifications",
        "channel_tg": "✈️ Telegram Channel & Bot Guard",
        "channel_email": "📧 Email Phishing & BEC",
        "channel_clip": "📋 Clipboard / Link Guard",
        "channel_qr": "📷 Quishing (QR Code Phishing)",
        "sidebar_caption": "Inspired by Singapore ScamShield initiative. Built for cybersecurity engineers.",
        "lang_selector": "🌐 Language Preferences / 语言设置",
        
        # Tabs
        "tab_sms": "🔍 SMS Message Scanner",
        "tab_wa": "📱 WhatsApp Guardian",
        "tab_tg": "✈️ Telegram Guardian",
        "tab_email": "📧 Email Phishing Scanner",
        "tab_clip": "📋 Clipboard & Browser Shield",
        "tab_qr": "📷 Quishing (QR Phishing) Audit",
        "tab_prefs": "⚙️ Language & Localization Preferences",
        "tab_challenge": "🏆 NLP Challenge & Leaderboard",
        "tab_api": "🔌 Multi-Channel REST API",

        # Common Actions & Metrics
        "load_scenario": "Load Test Scenario:",
        "custom_input": "-- Custom Input --",
        "message_to_inspect": "Message Text to Inspect:",
        "run_deep_scan": "🚀 Run Deep Scan",
        "analyzing": "Analyzing message vectors and domain risk...",
        "risk_score": "Risk Score",
        "classification": "Classification",
        "scam_probability": "Scam Probability",
        "tactics_detected_header": "🚨 Social Engineering Tactics",
        "extracted_urls_header": "🌐 Extracted URLs & Infrastructure Audit",
        "safety_checklist_header": "🛡️ Prescriptive Safety Checklist",
        "no_tactics": "No predatory social engineering detected.",
        "no_urls": "No external links found.",
        "threat_level": "Threat Level",
        "typology": "Typology",
        "action_taken": "Action Taken",

        # WhatsApp Guardian Tab
        "wa_title": "📱 WhatsApp Spam & Notification Guardian",
        "wa_desc": "Intercepts incoming WhatsApp notifications in real time, checks the sender against predatory patterns, and generates instant alert banners and auto-reply warnings.",
        "wa_sender_name": "Sender Display Name:",
        "wa_sender_num": "Sender Phone Number:",
        "wa_is_group": "Is Group Message?",
        "wa_group_name": "Group Name (if applicable):",
        "wa_body": "Incoming WhatsApp Message Body:",
        "wa_sim_btn": "⚡ Simulate Incoming WhatsApp Message",
        "wa_sim_header": "📲 Simulated Mobile Notification",
        "wa_intercept_alert": "WHATSAPP INTERCEPT ALERT",
        "wa_safe_notice": "WHATSAPP NOTIFICATION (SAFE)",
        "wa_auto_reply_header": "🤖 Automated Safety Warning Response:",

        # Telegram Guardian Tab
        "tg_title": "✈️ Telegram Spam, Bot & Crypto Pump Guardian",
        "tg_desc": "Monitors Telegram channel broadcasts, VIP group chats, and bot interactions for crypto manipulation and fake giveaways.",
        "tg_user": "Telegram Username / Bot Handle:",
        "tg_is_bot": "Sender is Telegram Bot",
        "tg_chat": "Channel / Group Title:",
        "tg_is_channel": "Is Public Channel Broadcast",
        "tg_body": "Telegram Message Body:",
        "tg_btn": "✈️ Inspect Telegram Message",
        "tg_auto_reply_header": "🤖 Automated Supergroup Safety Warning:",

        # Email Phishing Scanner Tab
        "em_title": "📧 Email Phishing & Corporate Impersonation Scanner",
        "em_desc": "Detects Executive Spoofing (CEO Fraud), fake invoices, reply-to domain mismatches, and credential theft emails.",
        "em_sender": "Sender Email Address:",
        "em_reply_to": "Reply-To Header:",
        "em_subject": "Subject Line:",
        "em_body": "Email Body Content:",
        "em_btn": "🛡️ Inspect Email Security",
        "em_risk_score": "Email Risk Score",
        "em_domain_mismatch": "Domain Mismatch",
        "em_verdict": "Phishing Verdict",
        "em_anomalies": "🚨 Specific Anomalies Identified:",
        "em_urls": "🌐 Suspicious Embedded Links:",

        # Clipboard Guard Tab
        "clip_title": "📋 Real-Time Clipboard & Browser Shield",
        "clip_desc": "Monitors text or links copied from web browsers, WhatsApp Web, or Telegram. Intercepts dangerous payloads before navigation.",
        "clip_input": "Test Clipboard Copy Action (Paste or type text copied from browser/chat):",
        "clip_btn": "⚡ Test Clipboard Intercept",
        "clip_alert_header": "📋 CLIPBOARD GUARDIAN INTERCEPT!",
        "clip_safe": "✅ Clipboard content analyzed: No phishing or scam patterns detected.",
        "clip_recommendation": "🛑 Recommendation: DO NOT paste or open any embedded URLs in your web browser.",

        # Quishing Tab
        "qr_title": "📷 Quishing (QR Code Phishing) & Visual Lure Scanner",
        "qr_desc": "Audits physical and digital QR code payloads, payment stickers (PayNow / SGQR impersonation), and parking fee scams.",
        "qr_source": "Source Context:",
        "qr_loc": "Incident Location Tag:",
        "qr_payload": "Decoded QR Code URL or Text Payload:",
        "qr_btn": "📷 Audit QR Code Payload",
        "qr_action": "Action Required",
        "qr_domain_audit": "🌐 Domain Security Audit:",
        "qr_prevention": "🛡️ Quishing Prevention Safety Guidance:",

        # Preferences Tab
        "pref_title": "⚙️ Language & Localization Preferences",
        "pref_desc": "Customize system language, notification translations, automated reply behavior, and regional defense preferences.",
        "pref_ui_lang": "Active UI & Display Language:",
        "pref_auto_detect": "Automatic Incoming Language Detection (AI heuristic)",
        "pref_auto_detect_help": "When enabled, ScamShield automatically infers the incoming message's language and applies matched heuristics.",
        "pref_reply_mode": "Guardian Automated Warning Response Language:",
        "pref_reply_opt_preferred": "Match Active Display Language",
        "pref_reply_opt_en": "Always English (Global Default)",
        "pref_reply_opt_bilingual": "Bilingual (English + Selected Language)",
        "pref_save_btn": "💾 Save & Apply Language Preferences",
        "pref_saved_msg": "✅ Language preferences successfully saved to disk!",
        "pref_preview_header": "🔍 Live Multi-Language Alert Preview",
        "pref_preview_text": "Sample ScamShield Intercept Warning across all supported regional languages:"
    },

    "zh": {
        # App Header & Metadata
        "app_title": "🛡️ ScamShield 全方位多渠道网络反诈防御系统",
        "app_subtitle": "实时监测、智能剖析并拦截跨短信、WhatsApp、Telegram、钓鱼邮件及剪贴板的欺诈攻击。",
        "sidebar_title": "🛡️ ScamShield AI 卫士",
        "sidebar_desc": "**自主多通道反诈中枢**\n全天候防护公民免受短信钓鱼、WhatsApp 欺诈群发、钓鱼邮件与恶意剪贴板威胁。",
        "core_engine": "核心引擎状态",
        "channels_protected": "已受保护渠道：",
        "channel_sms": "💬 短信与伪基站拦截 (Smishing)",
        "channel_wa": "📱 WhatsApp 通知拦截护卫",
        "channel_tg": "✈️ Telegram 频道与机器人监控",
        "channel_email": "📧 钓鱼邮件与商业欺诈 (BEC)",
        "channel_clip": "📋 剪贴板与恶意链接预警",
        "channel_qr": "📷 二维码钓鱼 (Quishing) 审计",
        "sidebar_caption": "灵感源自新加坡 ScamShield 反诈倡议。专为网络安全工程师打造。",
        "lang_selector": "🌐 语言偏好设置 / Language Preferences",

        # Tabs
        "tab_sms": "🔍 短信风险扫描器",
        "tab_wa": "📱 WhatsApp 拦截防护",
        "tab_tg": "✈️ Telegram 监控卫士",
        "tab_email": "📧 钓鱼邮件深度扫描",
        "tab_clip": "📋 剪贴板实时拦截护盾",
        "tab_qr": "📷 二维码钓鱼 (Quishing) 审计",
        "tab_prefs": "⚙️ 语言与本地化偏好设置",
        "tab_challenge": "🏆 NLP 挑战赛与排行榜",
        "tab_api": "🔌 多通道 REST API 文档",

        # Common Actions & Metrics
        "load_scenario": "加载测试案例：",
        "custom_input": "-- 自定义输入 --",
        "message_to_inspect": "待分析的消息文本：",
        "run_deep_scan": "🚀 执行深度威胁扫描",
        "analyzing": "正在分析特征向量与欺诈域名基础设施...",
        "risk_score": "风险评分",
        "classification": "研判分类",
        "scam_probability": "欺诈概率",
        "tactics_detected_header": "🚨 诱导欺诈心理手段 (社会工程学)",
        "extracted_urls_header": "🌐 提取的网址与基础设施风险审查",
        "safety_checklist_header": "🛡️ 权威防诈安全指导指引",
        "no_tactics": "未检测到掠夺性社会工程诱骗手段。",
        "no_urls": "未发现外部可疑链接。",
        "threat_level": "威胁等级",
        "typology": "诈骗类型",
        "action_taken": "处置策略",

        # WhatsApp Guardian Tab
        "wa_title": "📱 WhatsApp 垃圾通知与诈骗群拦截卫士",
        "wa_desc": "实时拦截 WhatsApp 传入通知，核验发件人号码与话术特征，生成高危告警卡片并自动构建警告回复。",
        "wa_sender_name": "发件人显示昵称：",
        "wa_sender_num": "发件人电话号码：",
        "wa_is_group": "是否为群聊消息？",
        "wa_group_name": "群组名称（如适用）：",
        "wa_body": "收到的 WhatsApp 消息正文：",
        "wa_sim_btn": "⚡ 模拟接收 WhatsApp 消息",
        "wa_sim_header": "📲 模拟手机端实时通知",
        "wa_intercept_alert": "WHATSAPP 威胁拦截警报",
        "wa_safe_notice": "WHATSAPP 通知（安全正常）",
        "wa_auto_reply_header": "🤖 自动生成的安全警告回复：",

        # Telegram Guardian Tab
        "tg_title": "✈️ Telegram 垃圾群发、假冒机器人与拉盘骗局监控",
        "tg_desc": "监控 Telegram 频道广播、VIP 投资群组以及机器人对话，防御虚假加密货币拉盘与赠送陷阱。",
        "tg_user": "Telegram 用户名 / 机器人账号：",
        "tg_is_bot": "发件人属于 Telegram 机器人",
        "tg_chat": "群聊 / 频道标题：",
        "tg_is_channel": "属于公开频道广播",
        "tg_body": "Telegram 消息正文：",
        "tg_btn": "✈️ 深度研判 Telegram 消息",
        "tg_auto_reply_header": "🤖 超级群组自动化预警提示：",

        # Email Phishing Scanner Tab
        "em_title": "📧 钓鱼邮件与企业高管冒充 (BEC) 扫描器",
        "em_desc": "精准识别 CEO 伪造欺诈、虚假发票、发件人与回复域名不一致及凭证窃取邮件。",
        "em_sender": "发件人邮箱地址：",
        "em_reply_to": "回复邮箱 (Reply-To) 标头：",
        "em_subject": "邮件主题：",
        "em_body": "邮件正文内容：",
        "em_btn": "🛡️ 执行邮件安全性审计",
        "em_risk_score": "邮件综合风险分",
        "em_domain_mismatch": "域名标头伪造",
        "em_verdict": "邮件判定结论",
        "em_anomalies": "🚨 检测到的具体异常项：",
        "em_urls": "🌐 邮件内嵌可疑超链接：",

        # Clipboard Guard Tab
        "clip_title": "📋 剪贴板与浏览器实时防钓鱼护盾",
        "clip_desc": "监控从浏览器或聊天工具复制的文本与网址，在用户误点击或粘贴前抢先阻断欺诈行为。",
        "clip_input": "测试剪贴板捕获动作（粘贴或输入从浏览器/聊天复制的文字）：",
        "clip_btn": "⚡ 测试剪贴板实时拦截",
        "clip_alert_header": "📋 剪贴板卫士紧急拦截！",
        "clip_safe": "✅ 剪贴板内容分析完成：未发现已知钓鱼或网络诈骗模式。",
        "clip_recommendation": "🛑 安全建议：严禁在浏览器中打开或粘贴此内容中的任何网址链接。",

        # Quishing Tab
        "qr_title": "📷 二维码钓鱼 (Quishing) 与视觉诱饵扫描器",
        "qr_desc": "审查公共停车收费桩覆盖贴纸、假冒公用事业账单、以及伪造的 PayNow / SGQR 二维码。",
        "qr_source": "来源场景环境：",
        "qr_loc": "案发地理标签：",
        "qr_payload": "解码后的二维码网址或文字载荷：",
        "qr_btn": "📷 审计二维码有效载荷",
        "qr_action": "处置指导",
        "qr_domain_audit": "🌐 域名网络安全审计：",
        "qr_prevention": "🛡️ 二维码钓鱼防御权威指引：",

        # Preferences Tab
        "pref_title": "⚙️ 语言与本地化偏好设置",
        "pref_desc": "定制系统显示语言、预设测试案例、多语言告警模版与自动语言侦测功能。",
        "pref_ui_lang": "当前系统显示语言：",
        "pref_auto_detect": "启用输入消息语言自适应侦测 (AI Heuristic)",
        "pref_auto_detect_help": "开启后，ScamShield 将自动判断传入消息的语言类型（中/英/马/泰米尔/印地语）并适配匹配的防诈逻辑。",
        "pref_reply_mode": "防御卫士自动回复警告语言模式：",
        "pref_reply_opt_preferred": "匹配当前显示语言",
        "pref_reply_opt_en": "始终为英语 (国际通用标准)",
        "pref_reply_opt_bilingual": "双语对照模式 (英语 + 当前所选语言)",
        "pref_save_btn": "💾 保存并应用语言偏好设置",
        "pref_saved_msg": "✅ 语言偏好设置已成功持久化保存！",
        "pref_preview_header": "🔍 实时多语言告警卡片预览",
        "pref_preview_text": "ScamShield 针对各区域语言生成的统一拦截警告展示："
    },

    "ms": {
        # App Header & Metadata
        "app_title": "🛡️ ScamShield AI: Sistem Pertahanan Penipuan Siber Berbilang Saluran",
        "app_subtitle": "Kesan, analisa, dan sekat penipuan siber dalam masa nyata merentasi SMS, WhatsApp, Telegram, dan E-mel.",
        "sidebar_title": "🛡️ ScamShield AI",
        "sidebar_desc": "**Pertahanan Berbilang Saluran Autonomi**\nMelindungi pengguna daripada penipuan SMS, WhatsApp, Telegram, dan pancingan data e-mel.",
        "core_engine": "Status Enjin Utama",
        "channels_protected": "Saluran Dilindungi:",
        "channel_sms": "💬 SMS / Smishing",
        "channel_wa": "📱 Pemberitahuan WhatsApp",
        "channel_tg": "✈️ Saluran & Bot Telegram",
        "channel_email": "📧 Phishing E-mel & BEC",
        "channel_clip": "📋 Papan Keratan & Pautan",
        "channel_qr": "📷 Quishing (Kod QR Palsu)",
        "sidebar_caption": "Diilhamkan oleh inisiatif ScamShield Singapura. Dibina untuk pakar keselamatan siber.",
        "lang_selector": "🌐 Pilihan Bahasa / Language Preferences",

        # Tabs
        "tab_sms": "🔍 Pengimbas Mesej SMS",
        "tab_wa": "📱 Penjaga WhatsApp",
        "tab_tg": "✈️ Penjaga Telegram",
        "tab_email": "📧 Pengimbas Phishing E-mel",
        "tab_clip": "📋 Perisai Papan Keratan",
        "tab_qr": "📷 Audit Quishing (QR Phishing)",
        "tab_prefs": "⚙️ Keutamaan Bahasa & Tetapan",
        "tab_challenge": "🏆 Cabaran NLP & Papan Pendahulu",
        "tab_api": "🔌 REST API Berbilang Saluran",

        # Common Actions & Metrics
        "load_scenario": "Muat Senario Ujian:",
        "custom_input": "-- Input Tersuai --",
        "message_to_inspect": "Teks Mesej Untuk Diperiksa:",
        "run_deep_scan": "🚀 Jalankan Imbasan Mendalam",
        "analyzing": "Menganalisis vektor mesej dan risiko domain...",
        "risk_score": "Skor Risiko",
        "classification": "Klasifikasi",
        "scam_probability": "Kebarangkalian Penipuan",
        "tactics_detected_header": "🚨 Taktik Kejuruteraan Sosial Dikesan",
        "extracted_urls_header": "🌐 Pautan URL & Audit Infrastruktur",
        "safety_checklist_header": "🛡️ Senarai Semak Keselamatan",
        "no_tactics": "Tiada taktik manipulasi sosial dikesan.",
        "no_urls": "Tiada pautan luar ditemui.",
        "threat_level": "Tahap Ancaman",
        "typology": "Tipologi",
        "action_taken": "Tindakan Diambil",

        # WhatsApp Tab
        "wa_title": "📱 Penjaga Spam & Pemberitahuan WhatsApp",
        "wa_desc": "Menyekat pemberitahuan WhatsApp secara langsung, memeriksa penghantar, dan menjana amaran automatik.",
        "wa_sender_name": "Nama Paparan Penghantar:",
        "wa_sender_num": "Nombor Telefon Penghantar:",
        "wa_is_group": "Mesej Kumpulan?",
        "wa_group_name": "Nama Kumpulan (jika ada):",
        "wa_body": "Kandungan Mesej WhatsApp:",
        "wa_sim_btn": "⚡ Simulasikan Mesej Masuk WhatsApp",
        "wa_sim_header": "📲 Simulasi Pemberitahuan Telefon",
        "wa_intercept_alert": "AMARAN SEKATAN WHATSAPP",
        "wa_safe_notice": "PEMBERITAHUAN WHATSAPP (SELAMAT)",
        "wa_auto_reply_header": "🤖 Respons Amaran Keselamatan Automatik:",

        # Preferences Tab
        "pref_title": "⚙️ Keutamaan Bahasa & Tetapan Penyetempatan",
        "pref_desc": "Sesuaikan pilihan bahasa paparan, templat amaran, dan pengesanan automatik bahasa.",
        "pref_ui_lang": "Bahasa Paparan Aktif:",
        "pref_auto_detect": "Pengesanan Bahasa Automatik (Heuristik AI)",
        "pref_auto_detect_help": "Apabila diaktifkan, ScamShield mengesan bahasa mesej masuk secara automatik.",
        "pref_reply_mode": "Mod Bahasa Respons Amaran Automatik:",
        "pref_reply_opt_preferred": "Ikut Bahasa Paparan",
        "pref_reply_opt_en": "Sentiasa Bahasa Inggeris",
        "pref_reply_opt_bilingual": "Dwibahasa (Bahasa Inggeris + Bahasa Pilihan)",
        "pref_save_btn": "💾 Simpan Keutamaan Bahasa",
        "pref_saved_msg": "✅ Keutamaan bahasa berjaya disimpan!",
        "pref_preview_header": "🔍 Pratonton Amaran Berbilang Bahasa",
        "pref_preview_text": "Contoh amaran amaran pintasan ScamShield merentasi pelbagai bahasa serantau:"
    },

    "ta": {
        # App Header & Metadata
        "app_title": "🛡️ ScamShield AI: பல சேனல் மோசடி எதிர்ப்பு பாதுகாப்பு அமைப்பு",
        "app_subtitle": "SMS, வாட்ஸ்அப், டெலிகிராம் மற்றும் மின்னஞ்சல் வாயிலாக வரும் சைபர் மோசடிகளை உடனுக்குடன் கண்டறிந்து தடுக்கும் அமைப்பு.",
        "sidebar_title": "🛡️ ScamShield AI",
        "sidebar_desc": "**தானியங்கி பல சேனல் பாதுகாப்பு**\nஎஸ்எம்எஸ், வாட்ஸ்அப் அறிவிப்புகள் மற்றும் மின்னஞ்சல் ஃபிஷிங் ஆகியவற்றிலிருந்து பயனர்களைப் பாதுகாக்கிறது.",
        "core_engine": "முதன்மை என்ஜின் நிலை",
        "channels_protected": "பாதுகாக்கப்பட்ட சேனல்கள்:",
        "channel_sms": "💬 SMS / குறுஞ்செய்தி பாதுகாப்பு",
        "channel_wa": "📱 வாட்ஸ்அப் அறிவிப்பு பாதுகாப்பு",
        "channel_tg": "✈️ டெலிகிராம் பாதுகாப்பு",
        "channel_email": "📧 மின்னஞ்சல் ஃபிஷிங் ஸ்கேனர்",
        "channel_clip": "📋 கிளிப்போர்டு பாதுகாப்பு",
        "channel_qr": "📷 QR குறியீடு தணிக்கை",
        "sidebar_caption": "சிங்கப்பூர் ScamShield முயற்சியால் ஈர்க்கப்பட்டது.",
        "lang_selector": "🌐 மொழி விருப்பத்தேர்வுகள் / Language Preferences",

        # Tabs
        "tab_sms": "🔍 SMS செய்தி ஸ்கேனர்",
        "tab_wa": "📱 வாட்ஸ்அப் பாதுகாப்பு",
        "tab_tg": "✈️ டெலிகிராம் பாதுகாப்பு",
        "tab_email": "📧 மின்னஞ்சல் ஃபிஷிங் ஸ்கேனர்",
        "tab_clip": "📋 கிளிப்போர்டு பாதுகாப்பு",
        "tab_qr": "📷 QR குறியீடு தணிக்கை",
        "tab_prefs": "⚙️ மொழி விருப்பத்தேர்வுகள்",
        "tab_challenge": "🏆 NLP சவால் & தரவரிசை",
        "tab_api": "🔌 பல சேனல் REST API",

        # Common Actions
        "load_scenario": "சோதனை உதாரணத்தைத் தேர்ந்தெடுக்கவும்:",
        "custom_input": "-- சொந்த உரை --",
        "message_to_inspect": "ஆய்வு செய்ய வேண்டிய செய்தி:",
        "run_deep_scan": "🚀 தீவிர சோதனை செய்க",
        "analyzing": "செய்தி மற்றும் வலைத்தள ஆபத்து பகுப்பாய்வு செய்யப்படுகிறது...",
        "risk_score": "ஆபத்து மதிப்பீடு",
        "classification": "வகைப்பாடு",
        "scam_probability": "மோசடி நிகழ்தகவு",
        "tactics_detected_header": "🚨 சமூக பொறியியல் உத்திகள்",
        "extracted_urls_header": "🌐 கண்டறியப்பட்ட வலைத்தள இணைப்புகள்",
        "safety_checklist_header": "🛡️ பாதுகாப்பு வழிகாட்டுதல்கள்",
        "no_tactics": "ஏமாற்று உத்திகள் எதுவும் கண்டறியப்படவில்லை.",
        "no_urls": "வெளிப்புற இணைப்புகள் எதுவும் இல்லை.",
        "threat_level": "அச்சுறுத்தல் நிலை",
        "typology": "மோசடி வகை",
        "action_taken": "எடுக்கப்பட்ட நடவடிக்கை",

        # Preferences
        "pref_title": "⚙️ மொழி விருப்பத்தேர்வுகள் & அமைப்புகள்",
        "pref_desc": "கணினி மொழி, அறிவிப்புகள் மற்றும் தானியங்கி பதில் விருப்பங்களைத் தனிப்பயனாக்குங்கள்.",
        "pref_ui_lang": "செயலில் உள்ள காட்சி மொழி:",
        "pref_auto_detect": "தானியங்கி மொழி கண்டறிதல் (AI Heuristic)",
        "pref_auto_detect_help": "இயக்கப்பட்டால், உள்வரும் செய்தியின் மொழியை ScamShield தானாகவே கண்டறியும்.",
        "pref_reply_mode": "தானியங்கி எச்சரிக்கை பதில் மொழி முறை:",
        "pref_reply_opt_preferred": "காட்சி மொழியுடன் பொருத்து",
        "pref_reply_opt_en": "எப்போதும் ஆங்கிலம்",
        "pref_reply_opt_bilingual": "இருமொழி (ஆங்கிலம் + தேர்ந்தெடுக்கப்பட்ட மொழி)",
        "pref_save_btn": "💾 மொழி விருப்பங்களைச் சேமிக்கவும்",
        "pref_saved_msg": "✅ மொழி விருப்பத்தேர்வுகள் வெற்றிகரமாக சேமிக்கப்பட்டன!",
        "pref_preview_header": "🔍 நேரடி மொழி எச்சரிக்கை முன்னோட்டம்",
        "pref_preview_text": "பல்வேறு மொழிகளில் ScamShield வழங்கும் எச்சரிக்கை செய்தி முன்னோட்டம்:"
    },

    "hi": {
        # App Header & Metadata
        "app_title": "🛡️ ScamShield AI: मल्टी-चैनल साइबर धोखाधड़ी रक्षा प्रणाली",
        "app_subtitle": "एसएमएस, व्हाट्सएप, टेलीग्राम और ईमेल पर होने वाले ऑनलाइन फ्रॉड का रीयल-टाइम विश्लेषण और रोकथाम।",
        "sidebar_title": "🛡️ ScamShield AI",
        "sidebar_desc": "**स्वायत्त मल्टी-चैनल साइबर सुरक्षा**\nएसएमएस, व्हाट्सएप नोटिफिकेशन, टेलीग्राम और फिशिंग ईमेल से नागरिकों की सुरक्षा।",
        "core_engine": "कोर इंजन स्थिति",
        "channels_protected": "सुरक्षित चैनल:",
        "channel_sms": "💬 एसएमएस / स्मिशिंग रक्षा",
        "channel_wa": "📱 व्हाट्सएप नोटिफिकेशन गार्डियन",
        "channel_tg": "✈️ टेलीग्राम चैनल व बॉट गार्ड",
        "channel_email": "📧 ईमेल फिशिंग व बीईसी स्कैनर",
        "channel_clip": "📋 क्लिपबोर्ड लिंक गार्ड",
        "channel_qr": "📷 क्विशिंग (क्यूआर कोड) ऑडिट",
        "sidebar_caption": "सिंगापुर ScamShield पहल से प्रेरित। साइबर सुरक्षा इंजीनियरों के लिए निर्मित।",
        "lang_selector": "🌐 भाषा प्राथमिकताएं / Language Preferences",

        # Tabs
        "tab_sms": "🔍 एसएमएस संदेश स्कैनर",
        "tab_wa": "📱 व्हाट्सएप गार्डियन",
        "tab_tg": "✈️ टेलीग्राम गार्डियन",
        "tab_email": "📧 ईमेल फ़िशिंग स्कैनर",
        "tab_clip": "📋 क्लिपबोर्ड व ब्राउज़र शील्ड",
        "tab_qr": "📷 क्विशिंग (क्यूआर कोड) ऑडिट",
        "tab_prefs": "⚙️ भाषा और स्थानीयकरण प्राथमिकताएं",
        "tab_challenge": "🏆 एनएलपी चैलेंज व लीडरबोर्ड",
        "tab_api": "🔌 मल्टी-चैनल रेस्ट एपीआई",

        # Common Actions
        "load_scenario": "परीक्षण परिदृश्य चुनें:",
        "custom_input": "-- कस्टम इनपुट लिखें --",
        "message_to_inspect": "जांच हेतु संदेश का टेक्स्ट:",
        "run_deep_scan": "🚀 गहन विश्लेषण करें",
        "analyzing": "संदेश और डोमेन इन्फ्रास्ट्रक्चर का सुरक्षा विश्लेषण जारी है...",
        "risk_score": "जोखिम स्कोर",
        "classification": "वर्गीकरण",
        "scam_probability": "धोखाधड़ी संभावना",
        "tactics_detected_header": "🚨 पहचानी गई सोशल इंजीनियरिंग रणनीतियां",
        "extracted_urls_header": "🌐 निकाले गए यूआरएल व डोमेन ऑडिट",
        "safety_checklist_header": "🛡️ सुरक्षा चेकलिस्ट व सावधानियां",
        "no_tactics": "कोई दुर्भावनापूर्ण सोशल इंजीनियरिंग नहीं मिली।",
        "no_urls": "संदेश में कोई बाहरी लिंक नहीं मिला।",
        "threat_level": "खतरे का स्तर",
        "typology": "स्कैम प्रकार",
        "action_taken": "की गई कार्रवाई",

        # Preferences
        "pref_title": "⚙️ भाषा और स्थानीयकरण प्राथमिकताएं",
        "pref_desc": "सिस्टम की भाषा, चेतावनी संदेश, ऑटो-रिप्लाई और क्षेत्रीय सुरक्षा प्राथमिकताओं को कस्टमाइज़ करें।",
        "pref_ui_lang": "सक्रिय डिस्प्ले भाषा:",
        "pref_auto_detect": "आने वाले संदेशों की स्वचालित भाषा पहचान (AI Heuristic)",
        "pref_auto_detect_help": "सक्रिय होने पर, ScamShield प्राप्त संदेश की भाषा पहचानकर उसी अनुसार सुरक्षा नियम लागू करेगा।",
        "pref_reply_mode": "गार्डियन ऑटोमैटिक चेतावनी उत्तर की भाषा:",
        "pref_reply_opt_preferred": "सक्रिय डिस्प्ले भाषा के अनुसार",
        "pref_reply_opt_en": "हमेशा अंग्रेजी (अंतर्राष्ट्रीय मानक)",
        "pref_reply_opt_bilingual": "द्विभाषी (अंग्रेजी + चुनी गई भाषा)",
        "pref_save_btn": "💾 भाषा प्राथमिकताएं सहेजें",
        "pref_saved_msg": "✅ भाषा प्राथमिकताएं सफलतापूर्वक सहेज ली गईं!",
        "pref_preview_header": "🔍 रीयल-टाइम मल्टी-लैंग्वेज चेतावनी पूर्वावलोकन",
        "pref_preview_text": "विभिन्न क्षेत्रीय भाषाओं में ScamShield द्वारा जारी अलर्ट का उदाहरण:"
    }
}

# ==============================================================================
# LOCALIZED TYPOLOGIES & TACTICS
# ==============================================================================

CATEGORY_LABELS: Dict[str, Dict[str, str]] = {
    "bank_impersonation": {
        "en": "Bank Impersonation",
        "zh": "银行冒充钓鱼诈骗",
        "ms": "Penyamaran Bank",
        "ta": "வங்கி ஆள்மாறாட்டம்",
        "hi": "बैंक प्रतिरूपण धोखाधड़ी"
    },
    "parcel_delivery": {
        "en": "Parcel Delivery Fraud",
        "zh": "包裹快递关税诈骗",
        "ms": "Penipuan Penghantaran Bungkusan",
        "ta": "பார்சல் விநியோக மோசடி",
        "hi": "पार्सल डिलीवरी फ्रॉड"
    },
    "recruitment_job": {
        "en": "Fake Job Recruitment",
        "zh": "兼职刷单虚假招聘",
        "ms": "Penipuan Kerja Sambilan",
        "ta": "போலி வேலைவாய்ப்பு மோசடி",
        "hi": "फर्जी नौकरी घोटाला"
    },
    "investment_crypto": {
        "en": "Crypto / Investment Scheme",
        "zh": "高利虚拟货币投资陷阱",
        "ms": "Penipuan Pelaburan Kripto",
        "ta": "கிரிப்டோ முதலீட்டு மோசடி",
        "hi": "क्रिप्टो व निवेश पोंजी स्कीम"
    },
    "government_police": {
        "en": "Government / Police Threat",
        "zh": "假冒公检法洗钱威胁",
        "ms": "Penyamaran Polis / Kerajaan",
        "ta": "அரசு / காவல்துறை மிரட்டல்",
        "hi": "पुलिस / सरकारी प्रतिरूपण"
    },
    "tech_support": {
        "en": "Tech Support Scam",
        "zh": "假冒电脑技术支持",
        "ms": "Penipuan Sokongan Teknikal",
        "ta": "தொழில்நுட்ப ஆதரவு மோசடி",
        "hi": "टेक सपोर्ट फ्रॉड"
    },
    "lottery_prize": {
        "en": "Lottery / Prize Scam",
        "zh": "虚假抽奖中奖陷阱",
        "ms": "Penipuan Hadiah Loteri",
        "ta": "லாட்டரி / பரிசு மோசடி",
        "hi": "लॉटरी / इनाम घोटाला"
    },
    "legitimate": {
        "en": "Legitimate / Ham",
        "zh": "安全正常通讯 (Ham)",
        "ms": "Mesej Sah / Selamat",
        "ta": "முறையான செய்தி (பாதுகாப்பானது)",
        "hi": "वैध संदेश (सुरक्षित)"
    }
}

TACTICS_TRANSLATIONS: Dict[str, Dict[str, Dict[str, str]]] = {
    "Artificial Urgency & Coercion": {
        "zh": {
            "name": "人为制造紧迫感与强迫恐吓",
            "desc": "利用时间紧迫感或法律/账户冻结威胁，迫使受害者在未经审慎思考的情况下仓促行事。"
        },
        "ms": {
            "name": "Tekanan Masa & Paksaan Palsu",
            "desc": "Menggunakan tekanan masa atau ancaman tindakan undang-undang/pembekuan akaun untuk memaksa mangsa bertindak terburu-buru."
        },
        "ta": {
            "name": "செயற்கை அவசரம் & அச்சுறுத்தல்",
            "desc": "பாதிக்கப்பட்டவரை அவசரமாக செயல்பட வைக்க கால அழுத்தம் அல்லது கணக்கு முடக்க மிரட்டலைப் பயன்படுத்துகிறது."
        },
        "hi": {
            "name": "झूठी तात्कालिकता व भय पैदा करना",
            "desc": "खाता ब्लॉक या कानूनी कार्रवाई का डर दिखाकर पीड़ित को बिना सोचे-समझे जल्दबाजी में कदम उठाने पर मजबूर करना।"
        }
    },
    "Financial Bait / Greed Trap": {
        "zh": {
            "name": "高额经济利益诱饵 / 贪婪陷阱",
            "desc": "承诺不切实际的丰厚报酬、保本高收益或虚假大奖，诱骗受害者上钩。"
        },
        "ms": {
            "name": "Umpan Kewangan / Perangkap Tamak",
            "desc": "Menjanjikan pulangan wang lumayan yang tidak realistik atau hadiah besar untuk memerangkap mangsa."
        },
        "ta": {
            "name": "நிதி தூண்டில் / பேராசை வலை",
            "desc": "எதார்த்தமற்ற நிதி ஆதாயங்கள் அல்லது பரிசுகளை உறுதியளித்து ஏமாற்றுகிறது."
        },
        "hi": {
            "name": "वित्तीय प्रलोभन व भारी मुनाफे का लालच",
            "desc": "अवास्तविक दैनिक कमाई, लॉटरी या गारंटीड रिटर्न का झांसा देकर पीड़ित को फंसाना।"
        }
    },
    "Credential & Fee Harvesting": {
        "zh": {
            "name": "个人身份凭据与资金索要",
            "desc": "索取受害者的银行动态口令(OTP)、登录密码、身份识别信息或要求垫付各类清关手续费。"
        },
        "ms": {
            "name": "Pencurian Kredensial & Bayaran Palsu",
            "desc": "Meminta kata laluan perbankan, nombor OTP, atau bayaran pendahuluan untuk melepaskan barangan/akaun."
        },
        "ta": {
            "name": "கடவுச்சொல் & கட்டண பறிப்பு",
            "desc": "வங்கி உள்நுழைவு, OTP அல்லது முன்கூட்டியே கட்டணம் செலுத்த கோருகிறது."
        },
        "hi": {
            "name": "क्रेडेंशियल, ओटीपी व शुल्क उगाही",
            "desc": "व्यक्तिगत क्रेडेंशियल, पासवर्ड, बैंक ओटीपी या अनपेक्षित फीस/कस्टम शुल्क की मांग करना।"
        }
    },
    "Deceptive Infrastructure": {
        "zh": {
            "name": "欺诈性网络域名与仿冒基础设施",
            "desc": "使用仿冒知名品牌的虚假域名、恶意顶级后缀或直接IP地址伪装成正规官方门户。"
        },
        "ms": {
            "name": "Infrastruktur Domain Menipu",
            "desc": "Menggunakan domain yang menyerupai jenama rasmi, TLD mencurigakan, atau alamat IP langsung."
        },
        "ta": {
            "name": "ஏமாற்று வலைத்தள உள்கட்டமைப்பு",
            "desc": "உண்மையான நிறுவனங்களை ஆள்மாறாட்டம் செய்யும் போலி டொமைன்கள் அல்லது சந்தேகத்திற்கிடமான இணைப்புகள்."
        },
        "hi": {
            "name": "धोखेबाज डोमेन व फर्जी इन्फ्रास्ट्रक्चर",
            "desc": "असली बैंक या सरकारी ब्रांड की नकल करने वाले फर्जी डोमेन, डायरेक्ट आईपी या संदिग्ध लिंक का उपयोग।"
        }
    }
}

# ==============================================================================
# LOCALIZED SAFETY ADVICE
# ==============================================================================

LOCALIZED_SAFETY_ADVICE: Dict[str, Dict[str, List[str]]] = {
    "en": {
        "scam_general": [
            "⚠️ DO NOT click on any links in this message or open any attachments.",
            "🚫 NEVER provide your OTP, banking login, Singpass, or card PIN to unverified links.",
            "📢 Report this message via the official ScamShield app or scamshield.gov.sg."
        ],
        "bank": [
            "🏦 Verify your account status by logging directly into the official bank mobile application, never through links."
        ],
        "parcel": [
            "📦 Check delivery status inside the official courier app or website using your original tracking number."
        ],
        "police": [
            "🛡️ Government and police agencies will NEVER demand payments or transfer of funds over phone or SMS."
        ],
        "job": [
            "💼 Legitimate companies will never hire via Telegram/WhatsApp to perform paid video likes or review tasks."
        ],
        "safe": [
            "✅ This message appears legitimate, but always exercise standard vigilance with incoming messages."
        ]
    },
    "zh": {
        "scam_general": [
            "⚠️ 严禁点击此消息中的任何外部网址链接，切勿下载或打开任何附件。",
            "🚫 绝不在任何非官方网页输入您的银行动态口令(OTP)、网银密码、Singpass 或信用卡卡号。",
            "📢 请立即通过新加坡官方 ScamShield 应用程序或 scamshield.gov.sg 举报此诈骗消息。"
        ],
        "bank": [
            "🏦 如需核实银行账户状态，请直接打开手机官方银行 App 进行查验，切勿信任短信内的重置或激活链接。"
        ],
        "parcel": [
            "📦 查验包裹物流进度时，请直接访问邮政快递官方网站或 App，使用原始快递运单号查询。"
        ],
        "police": [
            "🛡️ 新加坡警方、公检法或任何政府机关绝不会通过电话、短信或社交软件向公民索取资金转账或在线办案。"
        ],
        "job": [
            "💼 正规企业绝不会通过 WhatsApp 或 Telegram 招募所谓“点赞视频”、“刷单返利”的高薪兼职人员。"
        ],
        "safe": [
            "✅ 经分析此消息符合正常安全通讯特征，但对于包含支付或个人信息的请求仍应保持审慎核实。"
        ]
    },
    "ms": {
        "scam_general": [
            "⚠️ JANGAN klik sebarang pautan dalam mesej ini atau buka sebarang lampiran.",
            "🚫 JANGAN sesekali berikan kod OTP, kata laluan bank, atau nombor PIN kad anda pada pautan tidak sah.",
            "📢 Laporkan mesej ini melalui aplikasi rasmi ScamShield atau laman sesawang rasmi."
        ],
        "bank": [
            "🏦 Sahkan status akaun dengan log masuk terus ke aplikasi perbankan mudah alih rasmi anda."
        ],
        "parcel": [
            "📦 Semak status penghantaran dalam aplikasi kurier rasmi menggunakan nombor penjejakan asal anda."
        ],
        "police": [
            "🛡️ Agensi kerajaan dan pihak polis TIDAK AKAN meminta pemindahan wang melalui telefon atau SMS."
        ],
        "job": [
            "💼 Syarikat sah tidak akan mengambil pekerja melalui WhatsApp untuk tugas seperti 'like video' berbayar."
        ],
        "safe": [
            "✅ Mesej ini kelihatan sah, tetapi sentiasa berwaspada dengan mesej yang meminta tindakan kewangan."
        ]
    },
    "ta": {
        "scam_general": [
            "⚠️ இந்தச் செய்தியில் உள்ள எந்தவொரு இணைப்பையும் கிளிக் செய்ய வேண்டாம்.",
            "🚫 உங்கள் வங்கி OTP, கடவுச்சொல் அல்லது கார்டு பின் எண்ணை ஒருபோதும் பகிர வேண்டாம்.",
            "📢 அதிகாரப்பூர்வ ScamShield செயலி மூலம் இந்தச் செய்தியைப் புகாரளிக்கவும்."
        ],
        "bank": [
            "🏦 வங்கி கணக்கு நிலையை அதிகாரப்பூர்வ வங்கி செயலி மூலம் மட்டுமே சரிபார்க்கவும்."
        ],
        "parcel": [
            "📦 அஞ்சல் விநியோக நிலையை அதிகாரப்பூர்வ கூரியர் தளம் மூலம் சரிபார்க்கவும்."
        ],
        "police": [
            "🛡️ காவல்துறையோ அல்லது அரசு அதிகாரிகளோ ஒருபோதும் தொலைபேசி மூலம் பணம் கோர மாட்டார்கள்."
        ],
        "job": [
            "💼 முறையான நிறுவனங்கள் வாட்ஸ்அப் மூலம் வீடியோ லைக் பணிகளை வழங்காது."
        ],
        "safe": [
            "✅ இந்தச் செய்தி பாதுகாப்பானது எனத் தெரிகிறது, இருப்பினும் விழிப்புடன் இருக்கவும்."
        ]
    },
    "hi": {
        "scam_general": [
            "⚠️ इस संदेश में दिए गए किसी भी लिंक पर क्लिक न करें और न ही कोई अटैचमेंट डाउनलोड करें।",
            "🚫 किसी भी अज्ञात लिंक पर अपना बैंक पासवर्ड, ओटीपी, सीवीवी या व्यक्तिगत जानकारी दर्ज न करें।",
            "📢 आधिकारिक साइबर सेल या ScamShield पोर्टल पर इस धोखाधड़ी संदेश की रिपोर्ट करें।"
        ],
        "bank": [
            "🏦 अपने बैंक खाते की स्थिति जांचने के लिए सीधे आधिकारिक बैंक मोबाइल ऐप में लॉगिन करें, किसी लिंक से नहीं।"
        ],
        "parcel": [
            "📦 पार्सल डिलीवरी स्टेटस केवल आधिकारिक कूरियर वेबसाइट या ऐप पर ओरिजिनल ट्रैकिंग नंबर से देखें।"
        ],
        "police": [
            "🛡️ पुलिस या कोई भी सरकारी जांच एजेंसी फोन या एसएमएस पर पैसे ट्रांसफर या डिजिटल गिरफ्तारी नहीं करती।"
        ],
        "job": [
            "💼 वैध कंपनियां व्हाट्सएप या टेलीग्राम पर वीडियो लाइक करने के नाम पर घर बैठे कमाई का ऑफर नहीं देतीं।"
        ],
        "safe": [
            "✅ यह संदेश सुरक्षित प्रतीत होता है, फिर भी व्यक्तिगत जानकारी साझा करते समय सतर्कता बरतें।"
        ]
    }
}

# ==============================================================================
# LOCALIZED AUTO-REPLY GENERATORS
# ==============================================================================

AUTO_REPLY_TEMPLATES: Dict[str, Dict[str, str]] = {
    "en": (
        "🛡️ [SCAMSHIELD NOTIFICATION INTERCEPT]\n"
        "WARNING: This message was detected as a potential {category} (Risk: {risk_score}%).\n"
        "DO NOT click external links, provide 2FA OTPs, or transfer money."
    ),
    "zh": (
        "🛡️【ScamShield 智能反诈自动预警】\n"
        "警报：此消息已被系统研判为可疑的【{category}】（风险等级：{risk_score}%）。\n"
        "请注意：严禁点击外部未知链接，切勿提供网银动态密码 (OTP) 或进行任何资金转账！"
    ),
    "ms": (
        "🛡️ [PINTASAN KESELAMATAN SCAMSHIELD]\n"
        "AMARAN: Mesej ini dikesan sebagai potensi {category} (Risiko: {risk_score}%).\n"
        "JANGAN klik pautan luar, jangan berikan OTP, dan jangan buat sebarang pemindahan wang."
    ),
    "ta": (
        "🛡️ [SCAMSHIELD பாதுகாப்பு எச்சரிக்கை]\n"
        "எச்சரிக்கை: இந்தச் செய்தி சாத்தியமான {category} என கண்டறியப்பட்டுள்ளது (ஆபத்து: {risk_score}%).\n"
        "வெளிப்புற இணைப்புகளைத் திறக்க வேண்டாம்; OTP அல்லது பணப் பரிமாற்றம் செய்ய வேண்டாம்."
    ),
    "hi": (
        "🛡️ [SCAMSHIELD साइबर सुरक्षा चेतावनी]\n"
        "सावधान: यह संदेश संभावित 【{category}】के रूप में चिन्हित किया गया है (जोखिम स्कोर: {risk_score}%)।\n"
        "अज्ञात लिंक पर क्लिक न करें, अपना बैंक ओटीपी साझा न करें और पैसे ट्रांसफर न करें।"
    )
}

# ==============================================================================
# PUBLIC API FUNCTIONS
# ==============================================================================

def t(key: str, lang: Optional[str] = None) -> str:
    """
    Translates a UI key according to the given or active language preference.
    Falls back to English if the key is missing in the target language.
    """
    active_lang = lang or get_current_language()
    if active_lang not in TRANSLATIONS:
        active_lang = DEFAULT_LANGUAGE
        
    lang_dict = TRANSLATIONS.get(active_lang, {})
    if key in lang_dict:
        return lang_dict[key]
        
    # Fallback to English
    return TRANSLATIONS.get(DEFAULT_LANGUAGE, {}).get(key, key)

def get_category_label(category: str, lang: Optional[str] = None) -> str:
    """Returns the localized display name for a fraud category."""
    active_lang = lang or get_current_language()
    cat_info = CATEGORY_LABELS.get(category, {})
    if active_lang in cat_info:
        return cat_info[active_lang]
    return cat_info.get(DEFAULT_LANGUAGE, category.replace("_", " ").title())

def get_localized_tactics(tactics_list: List[Dict[str, Any]], lang: Optional[str] = None) -> List[Dict[str, Any]]:
    """Translates detected tactics into user's preferred language."""
    active_lang = lang or get_current_language()
    if active_lang == "en":
        return tactics_list

    localized = []
    for tac in tactics_list:
        tac_name = tac.get("tactic", "")
        trans_info = TACTICS_TRANSLATIONS.get(tac_name, {}).get(active_lang)
        if trans_info:
            localized.append({
                "tactic": trans_info["name"],
                "description": trans_info["desc"],
                "evidence": tac.get("evidence", [])
            })
        else:
            localized.append(tac)
    return localized

def get_localized_safety_advice(category: str, is_scam: bool, risk_score: float, lang: Optional[str] = None) -> List[str]:
    """Builds localized prescriptive safety checklist."""
    active_lang = lang or get_current_language()
    if active_lang not in LOCALIZED_SAFETY_ADVICE:
        active_lang = DEFAULT_LANGUAGE

    advice_dict = LOCALIZED_SAFETY_ADVICE[active_lang]
    advice = []

    if is_scam or risk_score >= 50:
        advice.extend(advice_dict.get("scam_general", []))
        if "bank" in category:
            advice.extend(advice_dict.get("bank", []))
        elif "parcel" in category or "delivery" in category:
            advice.extend(advice_dict.get("parcel", []))
        elif "police" in category or "government" in category:
            advice.extend(advice_dict.get("police", []))
        elif "job" in category or "recruitment" in category:
            advice.extend(advice_dict.get("job", []))
    else:
        advice.extend(advice_dict.get("safe", []))

    return advice

def generate_auto_reply_warning(category: str, risk_score: float, lang: Optional[str] = None, mode: Optional[str] = None) -> str:
    """Generates localized auto-reply text with optional bilingual mode."""
    prefs = load_user_preferences()
    active_lang = lang or get_current_language()
    reply_mode = mode or prefs.get("auto_reply_mode", "preferred")

    cat_label = get_category_label(category, active_lang)
    template = AUTO_REPLY_TEMPLATES.get(active_lang, AUTO_REPLY_TEMPLATES["en"])
    local_reply = template.format(category=cat_label.upper(), risk_score=risk_score)

    if reply_mode == "bilingual" and active_lang != "en":
        en_template = AUTO_REPLY_TEMPLATES["en"]
        en_reply = en_template.format(category=category.replace("_", " ").upper(), risk_score=risk_score)
        return f"{en_reply}\n\n---\n{local_reply}"
    elif reply_mode == "en":
        en_template = AUTO_REPLY_TEMPLATES["en"]
        return en_template.format(category=category.replace("_", " ").upper(), risk_score=risk_score)
    else:
        return local_reply

def get_localized_presets(lang: Optional[str] = None) -> Dict[str, str]:
    """Returns preset test scenarios in user's selected language."""
    active_lang = lang or get_current_language()
    return SAMPLE_PRESETS_BY_LANG.get(active_lang, SAMPLE_PRESETS_BY_LANG["en"])
