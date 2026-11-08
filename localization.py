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
        "region": "India / Global",
        "description": "Standard English cybersecurity terminology"
    },
    "te": {
        "code": "te",
        "name": "Telugu",
        "native_name": "తెలుగు",
        "flag": "🇮🇳",
        "region": "Andhra Pradesh / Telangana / India",
        "description": "సైబర్ మోసాల నిరోధక రక్షణ పదజాలం (Telugu Cyber Defense)"
    },
    "hi": {
        "code": "hi",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "flag": "🇮🇳",
        "region": "India / South Asia",
        "description": "साइबर धोखाधड़ी रक्षा शब्दावली (Hindi Cyber Defense)"
    },
    "ta": {
        "code": "ta",
        "name": "Tamil",
        "native_name": "தமிழ்",
        "flag": "🇮🇳",
        "region": "Tamil Nadu / South Asia",
        "description": "மோசடி எதிர்ப்பு பாதுகாப்பு சொற்கள் (Tamil Cyber Defense)"
    },
    "ms": {
        "code": "ms",
        "name": "Malay",
        "native_name": "Bahasa Melayu",
        "flag": "🇲🇾",
        "region": "Malaysia / Singapore",
        "description": "Terminologi pertahanan penipuan siber Bahasa Melayu"
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
    Detects Telugu, Hindi, Tamil, Malay, or defaults to English.
    """
    if not text or not isinstance(text, str):
        return DEFAULT_LANGUAGE
    
    # Check for Telugu script or common romanized Telugu
    if re.search(r"[\u0c00-\u0c7f]", text) or re.search(r"\b(nenu|cheyandi|vachayi|dabbulu|nijamgane|avunura|kavali)\b", text, re.I):
        return "te"
        
    # Check for Devanagari (Hindi) script
    if re.search(r"[\u0900-\u097f]", text):
        return "hi"
        
    # Check for Tamil script
    if re.search(r"[\u0b80-\u0bff]", text):
        return "ta"
        
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
        "💸 Fake Loan / Money Transfer Scam": "Fast Cash Loan Approved! You have been pre-approved for SGD 10,00,0 personal loan at 1.2% interest. Transfer SGD 150 processing fee to release money immediately: http://fast-loan-disbursement.vip",
        "💼 WhatsApp Part-Time Job Scam": "Earn $200-$600 daily working from home! Simple task: like YouTube videos and review products. No experience needed. Contact WhatsApp: +65 8921 4452",
        "📈 Crypto Guaranteed 500% ROI": "Exclusive VIP Crypto Signals! Guaranteed 300% to 500% returns in 7 days using automated AI quant bot. Join Telegram @sg_crypto_admin or http://crypto-vault-multiplier.live",
        "⚖️ Police Arrest Warrant Threat": "Singapore Police Force Notice: An arrest warrant has been issued under your IC for transnational money laundering. Contact Inspector Tan immediately at +65 6712 9012",
        "💻 Microsoft Tech Support Alert": "Microsoft Security Alert: Critical Trojan virus detected on your Windows PC! Credit card details leaking. Call Toll-Free +1-800-419-0921 immediately.",
        "🟢 Genuine Bank OTP (Ham)": "Your OTP for login to OCBC Digital is 829104. Valid for 3 mins. Never share your OTP with anyone, including bank staff.",
        "🟢 Genuine Courier Delivery (Ham)": "Your package from Amazon order #112-9281928 is out for delivery today. Track in the official Amazon app.",
        "🟢 Genuine Personal SMS (Ham)": "Hey! Are we still meeting for lunch at 12:30pm tomorrow at Bugis Junction? Let me know!"
    },
    "te": {
        "🏦 బ్యాంక్ ఖాతా బ్లాక్ & డిజిటల్ టోకెన్ ఫిషింగ్": "SBI / HDFC బ్యాంక్: మీ డిజిటల్ సెక్యూరిటీ టోకెన్ గడువు నేటితో ముగిసింది. ఖాతా శాశ్వతంగా బ్లాక్ అవ్వకుండా ఉండటానికి వెంటనే http://sbi-token-kyc.online లో లాగిన్ అయి యాక్టివేట్ చేయండి.",
        "📦 పోస్టల్ పార్సెల్ కస్టమ్స్ డ్యూటీ మోసం": "ఇండియా పోస్ట్: కస్టమ్స్ డ్యూటీ ఫీజు ₹145 చెల్లించనందున మీ పార్సెల్ IN829102 నిలిపివేయబడింది. పార్సెల్ విడుదల చేయడానికి వెంటనే చెల్లించండి: http://indiapost-customs-track.top",
        "💸 నకిలీ పర్సనల్ లోన్ & మనీ ట్రాన్స్‌ఫర్ మోసం": "తక్షణ పర్సనల్ లోన్ మంజూరైంది! మీ పేరుపై ₹1,00,000 లోన్ 1% వడ్డీతో ఆమోదించబడింది. వెంటనే లోన్ మొత్తం పొందడానికి ₹1,500 ప్రాసెసింగ్ ఫీజు చెల్లించండి: http://fast-loan-disbursement.vip",
        "💼 వర్క్ ఫ్రమ్ హోమ్ పార్ట్ టైమ్ జాబ్ ఫ్రాడ్": "ఇంటి నుండే రోజుకు ₹5,000 - ₹15,000 సంపాదించండి! యూట్యూబ్ వీడియోలు లైక్ చేయండి & రేటింగ్ ఇవ్వండి. ఎటువంటి అనుభవం అవసరం లేదు. వెంటనే వాట్సాప్ చేయండి: +91 98214 44521",
        "📈 క్రిప్టో 500% గ్యారెంటీడ్ రిటర్న్ పోంజీ స్కీమ్": "ప్రత్యేక VIP క్రిప్టో సిగ్నల్స్! AI ఆటోమేటెడ్ బాట్ ద్వారా 7 రోజుల్లో 300% నుండి 500% వరకు ఖచ్చితమైన లాభాలు. టెలిగ్రామ్ @in_crypto_vip లేదా http://crypto-vault-multiplier.live లో చేరండి.",
        "⚖️ పోలీస్ అరెస్ట్ వారెంట్ & మనీలాండరింగ్ బెదిరింపు": "పోలీస్ హెడ్‌క్వార్టర్స్ నోటీసు: మనీలాండరింగ్ కేసులో మీ ఆధార్ నంబర్‌పై అరెస్ట్ వారెంట్ జారీ చేయబడింది. వెంటనే ఇన్‌స్పెక్టర్ వర్మతో +91 80212 90123 లో మాట్లాడండి.",
        "💻 మైక్రోసాఫ్ట్ సెక్యూరిటీ వైరస్ అలర్ట్": "మైక్రోసాఫ్ట్ సెక్యూరిటీ హెచ్చరిక: మీ కంప్యూటర్‌లో ప్రమాదకరమైన ట్రోజన్ వైరస్ గుర్తించబడింది! మీ బ్యాంక్ వివరాలు లీక్ అవుతున్నాయి. వెంటనే టోల్-ఫ్రీ నంబర్ +1-800-419-0921 కి కాల్ చేయండి.",
        "🟢 నిజమైన బ్యాంక్ ఓటీపీ (సురక్షితం)": "మీ నెట్ బ్యాంకింగ్ లాగిన్ కోసం ఓటీపీ (OTP) 829104. ఇది 3 నిమిషాల వరకు మాత్రమే చెల్లుబాటు అవుతుంది. మీ ఓటీపీని ఎవరితోనూ (బ్యాంక్ అధికారులతో సహా) పంచుకోవద్దు.",
        "🟢 నిజమైన కొరియర్ డెలివరీ సందేశం (సురక్షితం)": "మీ అమెజాన్ ఆర్డర్ #402-9182918 ఈరోజు డెలివరీ చేయబడుతుంది. అధికారిక అమెజాన్ యాప్‌లో ట్రాక్ చేయండి.",
        "🟢 వ్యక్తిగత సాధారణ సందేశం (సురక్షితం)": "హలో! రేపు మధ్యాహ్నం 1:00 గంటకు లంచ్ కోసం కలుస్తున్నామా? నాకు మెసేజ్ చేయి."
    },
    "ms": {
        "🏦 Phishing Token Bank OCBC Dinyahaktif": "Bank OCBC: Token digital anda telah tamat tempoh hari ini. Aktifkan semula akses anda sekarang di http://ocbc-auth-portal.online untuk mengelakkan akaun anda dibekukan serta-merta.",
        "📦 SingPost Bayaran Cukai Kastam Tertunggak": "SingPost: Bungkusan anda SG920192 ditahan di pusat agihan kerana cukai kastam belum dibayar sebanyak $2.50. Buat bayaran segera untuk pelepasan: http://singpost-tracking-fees.top",
        "💸 Penipuan Pinjaman Wang Segera": "Pinjaman Wang Segera Diluluskan! Anda layak untuk pinjaman peribadi sebanyak SGD 10,000. Pindahkan yuran pemprosesan SGD 150 untuk melepaskan wang serta-merta: http://fast-loan-disbursement.vip",
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
        "💸 போலி உடனடி கடன் & பண மோசடி": "உடனடி கடன் ஒப்புதல்! உங்களுக்கு SGD 10,000 தனிநபர் கடன் அங்கீகரிக்கப்பட்டுள்ளது. பணத்தை உடனே பெற SGD 150 செயலாக்க கட்டணம் செலுத்தவும்: http://fast-loan-disbursement.vip",
        "💼 பகுதி நேர வேலை வாய்ப்பு தினசரி $500 மோசடி": "வீட்டிலிருந்தே தினமும் $200 முதல் $600 வரை சம்பாதிக்கலாம்! YouTube வீடியோக்களை லைக் செய்யவும். அனுபவம் தேவையில்லை. வாட்ஸ்அப்பில் தொடர்பு கொள்ளவும்: +65 8921 4452",
        "📈 கிரிப்டோ 500% உத்தரவாத லாப மோசடி": "விஐபி கிரிப்டோ சிக்னல்கள்! 7 நாட்களில் 300% முதல் 500% வரை உத்தரவாத லாபம். டெலிகிராமில் இணையுங்கள் @sg_crypto_admin அல்லது http://crypto-vault-multiplier.live",
        "⚖️ காவல்துறை கைது ஆணை மிரட்டல்": "சிங்கப்பூர் காவல்துறை அறிவிப்பு: பணமோசடி வழக்கில் உங்கள் மீது கைது ஆணை பிறப்பிக்கப்பட்டுள்ளது. உடனே ஆய்வாளர் டானை +65 6712 9012 இல் அழைக்கவும்.",
        "🟢 உண்மையான வங்கி OTP செய்தி (பாதுகாப்பானது)": "OCBC டிஜிட்டல் உள்நுழைவிற்கான உங்கள் OTP எண் 829104. 3 நிமிடங்கள் மட்டுமே செல்லும். யாருடனும் OTP-ஐ பகிர வேண்டாம்.",
        "🟢 உண்மையான கூரியர் விநியோக அறிவிப்பு (பாதுகாப்பானது)": "உங்கள் அமேசான் ஆர்டர் #112-9281928 இன்று விநியோகிக்கப்படும். அமேசான் செயலியில் கண்காணிக்கவும்."
    },
    "hi": {
        "🏦 बैंक डिजिटल टोकन सस्पेंशन व फर्जी लिंक": "OCBC बैंक: आपका डिजिटल सुरक्षा टोकन आज समाप्त हो गया है। स्थायी खाता ब्लॉक से बचने के लिए अभी http://ocbc-auth-portal.online पर लॉगिन कर पुनः सक्रिय करें।",
        "📦 सिंगपोस्ट कस्टम्स ड्यूटी बकाया पार्सल स्कैम": "SingPost: कस्टम शुल्क $2.50 बकाया होने के कारण आपका पार्सल SG920192 रोका गया है। पार्सल रिलीज कराने के लिए तुरंत भुगतान करें: http://singpost-tracking-fees.top",
        "💸 फर्जी इंस्टेंट लोन व मनी ट्रांसफर फ्रॉड": "तत्काल पर्सनल लोन स्वीकृत! आपके नाम ₹1,00,000 का पर्सनल लोन 1% ब्याज दर पर मंजूर हुआ है। राशि तुरंत खाते में पाने के लिए ₹1,500 प्रोसेसिंग फीस ट्रांसफर करें: http://fast-loan-disbursement.vip",
        "💼 वर्क फ्रॉम होम पार्ट टाइम जॉब फर्जीवाड़ा": "घर बैठे रोजाना ₹15,000 - ₹30,000 कमाएं! केवल यूट्यूब वीडियो लाइक करें और रिव्यू दें। कोई अनुभव आवश्यक नहीं। व्हाट्सएप पर संपर्क करें: +65 8921 4452",
        "📈 क्रिप्टो गारंटीड 500% रिटर्न पोंजी स्कीम": "एक्सक्लूसिव वीआईपी क्रिप्टो सिग्नल्स! एआई बॉट द्वारा 7 दिनों में 300% से 500% गारंटीड रिटर्न। तुरंत टेलीग्राम चैनल @sg_crypto_admin या http://crypto-vault-multiplier.live पर जुड़ें।",
        "⚖️ पुलिस अरेस्ट वारंट व मनी लॉन्ड्रिंग धमकी": "सिंगापुर पुलिस बल नोटिस: मनी लॉन्ड्रिंग मामले में आपके पहचान पत्र पर गिरफ्तारी वारंट जारी हुआ है। तुरंत इंस्पेक्टर टैन से +65 6712 9012 पर संपर्क करें।",
        "💻 माइक्रोसॉफ्ट सुरक्षा चेतावनी ट्रोजन वायरस": "माइक्रोसॉफ्ट सिक्योरिटी: आपके कंप्यूटर में गंभीर ट्रोजन वायरस पाया गया है! पासवर्ड व कार्ड चोरी हो रहे हैं। तुरंत टोल-फ्री +1-800-419-0921 पर कॉल करें।",
        "🟢 वास्तविक बैंक ओटीपी संदेश (सुरक्षित)": "OCBC बैंक में लॉगिन के लिए आपका ओटीपी 829104 है। यह 3 मिनट तक वैध है। अपना ओटीपी कभी किसी के साथ साझा न करें।",
        "🟢 पार्सल डिलीवरी डिलीवरी ट्रैकिंग (सुरक्षित)": "आपका अमेज़न ऑर्डर #112-9281928 आज डिलीवरी के लिए निकल चुका है। आधिकारिक ऐप में ट्रैक करें।"
    },
    "te": {
        "🏦 బ్యాంక్ ఖాతా బ్లాక్ & డిజిటల్ టోకెన్ ఫిషింగ్": "SBI / HDFC బ్యాంక్: మీ డిజిటల్ సెక్యూరిటీ టోకెన్ గడువు నేటితో ముగిసింది. ఖాతా శాశ్వతంగా బ్లాక్ అవ్వకుండా ఉండటానికి వెంటనే http://sbi-token-kyc.online లో లాగిన్ అయి యాక్టివేట్ చేయండి.",
        "📦 పోస్టల్ పార్సెల్ కస్టమ్స్ డ్యూటీ మోసం": "ఇండియా పోస్ట్: కస్టమ్స్ డ్యూటీ ఫీజు ₹145 చెల్లించనందున మీ పార్సెల్ IN829102 నిలిపివేయబడింది. పార్సెల్ విడుదల చేయడానికి వెంటనే చెల్లించండి: http://indiapost-customs-track.top",
        "💸 నకిలీ పర్సనల్ లోన్ & మనీ ట్రాన్స్‌ఫర్ మోసం": "తక్షణ పర్సనల్ లోన్ మంజూరైంది! మీ పేరుపై ₹1,00,000 లోన్ 1% వడ్డీతో ఆమోదించబడింది. వెంటనే లోన్ మొత్తం పొందడానికి ₹1,500 ప్రాసెసింగ్ ఫీజు చెల్లించండి: http://fast-loan-disbursement.vip",
        "💼 వర్క్ ఫ్రమ్ హోమ్ పార్ట్ టైమ్ జాబ్ ఫ్రాడ్": "ఇంటి నుండే రోజుకు ₹5,000 - ₹15,000 సంపాదించండి! యూట్యూబ్ వీడియోలు లైక్ చేయండి & రేటింగ్ ఇవ్వండి. ఎటువంటి అనుభవం అవసరం లేదు. వెంటనే వాట్సాప్ చేయండి: +91 98214 44521",
        "📈 క్రిప్టో 500% గ్యారెంటీడ్ రిటర్న్ పోంజీ స్కీమ్": "ప్రత్యేక VIP క్రిప్టో సిగ్నల్స్! AI ఆటోమేటెడ్ బాట్ ద్వారా 7 రోజుల్లో 300% నుండి 500% వరకు ఖచ్చితమైన లాభాలు. టెలిగ్రామ్ @in_crypto_vip లేదా http://crypto-vault-multiplier.live లో చేరండి.",
        "⚖️ పోలీస్ అరెస్ట్ వారెంట్ & మనీలాండరింగ్ బెదిరింపు": "పోలీస్ హెడ్‌క్వార్టర్స్ నోటీసు: మనీలాండరింగ్ కేసులో మీ ఆధార్ నంబర్‌పై అరెస్ట్ వారెంట్ జారీ చేయబడింది. వెంటనే ఇన్‌స్పెక్టర్ వర్మతో +91 80212 90123 లో మాట్లాడండి.",
        "💻 మైక్రోసాఫ్ట్ సెక్యూరిటీ వైరస్ అలర్ట్": "మైక్రోసాఫ్ట్ సెక్యూరిటీ హెచ్చరిక: మీ కంప్యూటర్‌లో ప్రమాదకరమైన ట్రోజన్ వైరస్ గుర్తించబడింది! మీ బ్యాంక్ వివరాలు లీక్ అవుతున్నాయి. వెంటనే టోల్-ఫ్రీ నంబర్ +1-800-419-0921 కి కాల్ చేయండి.",
        "🟢 నిజమైన బ్యాంక్ ఓటీపీ (సురక్షితం)": "మీ నెట్ బ్యాంకింగ్ లాగిన్ కోసం ఓటీపీ (OTP) 829104. ఇది 3 నిమిషాల వరకు మాత్రమే చెల్లుబాటు అవుతుంది. మీ ఓటీపీని ఎవరితోనూ (బ్యాంక్ అధికారులతో సహా) పంచుకోవద్దు.",
        "🟢 నిజమైన కొరియర్ డెలివరీ సందేశం (సురక్షితం)": "మీ అమెజాన్ ఆర్డర్ #402-9182918 ఈరోజు డెలివరీ చేయబడుతుంది. అధికారిక అమెజాన్ యాప్‌లో ట్రాక్ చేయండి.",
        "🟢 వ్యక్తిగత సాధారణ సందేశం (సురక్షితం)": "హలో! రేపు మధ్యాహ్నం 1:00 గంటకు లంచ్ కోసం కలుస్తున్నామా? నాకు మెసేజ్ చేయి."
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
    },
    "te": {
        # App Header & Metadata
        "app_title": "🛡️ ScamShield బహుళ-మార్గాల సైబర్ మోసాల రక్షణ వ్యవస్థ",
        "app_subtitle": "ఎస్ఎంఎస్, వాట్సాప్, టెలిగ్రామ్ మరియు ఈమెయిల్ ద్వారా వచ్చే సైబర్ మోసాలను రియల్-టైమ్‌లో గుర్తించి నిరోధించండి.",
        "sidebar_title": "🛡️ ScamShield AI రక్షకుడు",
        "sidebar_desc": "**స్వయంప్రతిపత్తి గల బహుళ-మార్గాల సైబర్ రక్షణ**\nఎస్ఎంఎస్, వాట్సాప్ నోటిఫికేషన్లు, టెలిగ్రామ్ మరియు ఫిషింగ్ ఈమెయిళ్ల నుండి పౌరులకు రక్షణ.",
        "core_engine": "కోర్ ఇంజిన్ స్థితి",
        "channels_protected": "రక్షించబడుతున్న మార్గాలు:",
        "channel_sms": "💬 ఎస్ఎంఎస్ / స్మిషింగ్ రక్షణ",
        "channel_wa": "📱 వాట్సాప్ నోటిఫికేషన్ గార్డియన్",
        "channel_tg": "✈️ టెలిగ్రామ్ ఛానల్ & బాట్ గార్డ్",
        "channel_email": "📧 ఈమెయిల్ ఫిషింగ్ & BEC స్కానర్",
        "channel_clip": "📋 క్లిప్‌బోర్డ్ లింక్ గార్డ్",
        "channel_qr": "📷 క్విషింగ్ (QR కోడ్) ఆడిట్",
        "sidebar_caption": "సైబర్ భద్రతా ఇంజనీర్ల కోసం రూపొందించబడింది.",
        "lang_selector": "🌐 భాషా ప్రాధాన్యతలు / Language Preferences",

        # Tabs
        "tab_sms": "🔍 ఎస్ఎంఎస్ సందేశాల స్కానర్",
        "tab_wa": "📱 వాట్సాప్ గార్డియన్",
        "tab_tg": "✈️ టెలిగ్రామ్ గార్డియన్",
        "tab_email": "📧 ఈమెయిల్ ఫిషింగ్ స్కానర్",
        "tab_clip": "📋 క్లిప్‌బోర్డ్ & బ్రౌజర్ షీల్డ్",
        "tab_qr": "📷 క్విషింగ్ (QR కోడ్) ఆడిట్",
        "tab_prefs": "⚙️ భాష & స్థానికీకరణ ప్రాధాన్యతలు",
        "tab_challenge": "🏆 NLP ఛాలెంజ్ & లీడర్‌బోర్డ్",
        "tab_api": "🔌 బహుళ-మార్గాల REST API",

        # Common Actions & Metrics
        "load_scenario": "పరీక్ష దృష్టాంతాన్ని ఎంచుకోండి:",
        "custom_input": "-- సొంత ఇన్పుట్ రాయండి --",
        "message_to_inspect": "తనిఖీ చేయవలసిన సందేశం టెక్స్ట్:",
        "run_deep_scan": "🚀 లోతైన విశ్లేషణ ప్రారంభించండి",
        "analyzing": "సందేశం మరియు డొమైన్ భద్రతను విశ్లేషిస్తోంది...",
        "risk_score": "ప్రమాద స్కోరు",
        "classification": "వర్గీకరణ",
        "scam_probability": "మోసం సంభావ్యత",
        "tactics_detected_header": "🚨 గుర్తించబడిన సోషల్ ఇంజనీరింగ్ వ్యూహాలు",
        "extracted_urls_header": "🌐 వెలికితీసిన లింకులు & డొమైన్ ఆడిట్",
        "safety_checklist_header": "🛡️ భద్రతా మార్గదర్శకాలు & చెక్‌లిస్ట్",
        "no_tactics": "ఎటువంటి దురుద్దేశపూరిత సోషల్ ఇంజనీరింగ్ వ్యూహాలు గుర్తించబడలేదు.",
        "no_urls": "ఎటువంటి బాహ్య లింకులు కనుగొనబడలేదు.",
        "threat_level": "ప్రమాద స్థాయి",
        "typology": "మోసం రకం",
        "action_taken": "తీసుకున్న చర్య",

        # WhatsApp Guardian Tab
        "wa_title": "📱 వాట్సాప్ స్పామ్ & నోటిఫికేషన్ గార్డియన్",
        "wa_desc": "వాట్సాప్ సందేశాలను రియల్-టైమ్‌లో తనిఖీ చేసి, మోసపూరిత లింకులను హెచ్చరించి, ఆటోమేటిక్ వార్నింగ్ మెసేజ్ రూపొందిస్తుంది.",
        "wa_sender_name": "పంపినవారి పేరు:",
        "wa_sender_num": "ఫోన్ నంబర్:",
        "wa_is_group": "గ్రూప్ సందేశమా?",
        "wa_group_name": "గ్రూప్ పేరు (ఉంటే):",
        "wa_body": "వాట్సాప్ సందేశం టెక్స్ట్:",
        "wa_sim_btn": "⚡ వాట్సాప్ సందేశాన్ని అనుకరించండి",
        "wa_sim_header": "📲 మొబైల్ నోటిఫికేషన్ ప్రివ్యూ",
        "wa_intercept_alert": "వాట్సాప్ ముప్పు హెచ్చరిక",
        "wa_safe_notice": "వాట్సాప్ నోటిఫికేషన్ (సురక్షితం)",
        "wa_auto_reply_header": "🤖 ఆటోమేటిక్ భద్రతా హెచ్చరిక సమాధానం:",

        # Telegram Guardian Tab
        "tg_title": "✈️ టెలిగ్రామ్ స్పామ్, బాట్ & క్రిప్టో మోసాల గార్డియన్",
        "tg_desc": "టెలిగ్రామ్ ఛానళ్లు, బాట్‌లు మరియు క్రిప్టో ఇన్వెస్ట్‌మెంట్ సందేశాలను నిరంతరం పర్యవేక్షిస్తుంది.",
        "tg_user": "టెలిగ్రామ్ యూజర్‌నేమ్ / బాట్ హ్యాండిల్:",
        "tg_is_bot": "పంపినవారు టెలిగ్రామ్ బాట్",
        "tg_chat": "ఛానల్ / గ్రూప్ పేరు:",
        "tg_is_channel": "పబ్లిక్ ఛానల్ బ్రాడ్‌కాస్ట్",
        "tg_body": "టెలిగ్రామ్ సందేశం:",
        "tg_btn": "✈️ టెలిగ్రామ్ సందేశాన్ని తనిఖీ చేయండి",
        "tg_auto_reply_header": "🤖 ఆటోమేటెడ్ సూపర్ గ్రూప్ హెచ్చరిక సమాధానం:",

        # Email Phishing Scanner Tab
        "em_title": "📧 ఈమెయిల్ ఫిషింగ్ & కార్పొరేట్ మోసాల స్కానర్",
        "em_desc": "నకిలీ ఇన్వాయిస్‌లు, ఎగ్జిక్యూటివ్ స్పూఫింగ్, మిస్‌మ్యాచ్ డొమైన్‌లు మరియు పాస్‌వర్డ్ దొంగతనం ఈమెయిళ్లను గుర్తిస్తుంది.",
        "em_sender": "పంపినవారి ఈమెయిల్ అడ్రస్:",
        "em_reply_to": "రిప్లై-టు (Reply-To) హెడర్:",
        "em_subject": "విషయం (Subject):",
        "em_body": "ఈమెయిల్ బాడీ కంటెంట్:",
        "em_btn": "🛡️ ఈమెయిల్ భద్రతను తనిఖీ చేయండి",
        "em_risk_score": "ఈమెయిల్ ప్రమాద స్కోరు",
        "em_domain_mismatch": "డొమైన్ అసమతుల్యత",
        "em_verdict": "ఫిషింగ్ తీర్పు",
        "em_anomalies": "🚨 గుర్తించబడిన అనుమానాస్పద అంశాలు:",
        "em_urls": "🌐 అనుమానాస్పద లింకులు:",

        # Clipboard Guard Tab
        "clip_title": "📋 రియల్-టైమ్ క్లిప్‌బోర్డ్ & బ్రౌజర్ షీల్డ్",
        "clip_desc": "బ్రౌజర్లు లేదా చాట్ నుండి కాపీ చేసిన టెక్స్ట్ మరియు లింకులను పర్యవేక్షిస్తుంది. ప్రమాదకరమైన లింకులను వెంటనే నిరోధిస్తుంది.",
        "clip_input": "క్లిప్‌బోర్డ్ టెక్స్ట్‌ను ఇక్కడ పేస్ట్ చేయండి:",
        "clip_btn": "⚡ క్లిప్‌బోర్డ్‌ను పరీక్షించండి",
        "clip_alert_header": "📋 క్లిప్‌బోర్డ్ గార్డియన్ ముప్పు హెచ్చరిక!",
        "clip_safe": "✅ క్లిప్‌బోర్డ్ కంటెంట్ విశ్లేషించబడింది: ఎటువంటి ఫిషింగ్ లేదా మోసం కనిపించలేదు.",
        "clip_recommendation": "🛑 సిఫార్సు: ఈ లింకులను మీ బ్రౌజర్‌లో తెరవవద్దు లేదా పేస్ట్ చేయవద్దు.",

        # Quishing Tab
        "qr_title": "📷 క్విషింగ్ (QR కోడ్ ఫిషింగ్) & విజువల్ ల్యూర్ స్కానర్",
        "qr_desc": "నకిలీ పేమెంట్ స్టిక్కర్లు, పార్కింగ్ ఫీజు మోసాలు మరియు అనుమానాస్పద క్యూఆర్ కోడ్ లింకులను ఆడిట్ చేస్తుంది.",
        "qr_source": "క్యూఆర్ కోడ్ మూలం:",
        "qr_loc": "సంఘటన ప్రదేశం:",
        "qr_payload": "డీకోడ్ చేసిన క్యూఆర్ కోడ్ URL లేదా టెక్స్ట్:",
        "qr_btn": "📷 క్యూఆర్ కోడ్ పేలోడ్‌ను ఆడిట్ చేయండి",
        "qr_action": "అవసరమైన చర్య",
        "qr_domain_audit": "🌐 డొమైన్ భద్రతా ఆడిట్:",
        "qr_prevention": "🛡️ క్యూఆర్ ఫిషింగ్ నివారణ మార్గదర్శకాలు:",

        # Preferences Tab
        "pref_title": "⚙️ భాష & స్థానికీకరణ ప్రాధాన్యతలు",
        "pref_desc": "సిస్టమ్ భాష, నోటిఫికేషన్ అనువాదాలు, ఆటోమేటిక్ రిప్లై విధానం మరియు ప్రాంతీయ రక్షణ ప్రాధాన్యతలను మార్చుకోండి.",
        "pref_ui_lang": "ప్రదర్శన భాష (Active Display Language):",
        "pref_auto_detect": "సందేశాల భాషను ఆటోమేటిక్‌గా గుర్తించు (AI Heuristic)",
        "pref_auto_detect_help": "ఇది ఆన్‌లో ఉంటే, వచ్చే సందేశం ఏ భాషలో ఉందో ScamShield స్వయంచాలకంగా గుర్తించి తగిన నిబంధనలను వర్తింపజేస్తుంది.",
        "pref_reply_mode": "గార్డియన్ ఆటోమేటిక్ హెచ్చరిక రిప్లై భాష:",
        "pref_reply_opt_preferred": "ప్రస్తుత ప్రదర్శన భాష ప్రకారం",
        "pref_reply_opt_en": "ఎల్లప్పుడూ ఆంగ్లం (English)",
        "pref_reply_opt_bilingual": "ద్విభాషా (ఆంగ్లం + ఎంచుకున్న భాష)",
        "pref_save_btn": "💾 భాషా ప్రాధాన్యతలను సేవ్ చేయండి",
        "pref_saved_msg": "✅ భాషా ప్రాధాన్యతలు విజయవంతంగా సేవ్ చేయబడ్డాయి!",
        "pref_preview_header": "🔍 ప్రత్యక్ష బహుళ-భాషా హెచ్చరిక ప్రివ్యూ",
        "pref_preview_text": "మద్దతు ఉన్న ప్రాంతీయ భాషలలో ScamShield హెచ్చరిక ఉదాహరణ:"
    }
}

# ==============================================================================
# LOCALIZED TYPOLOGIES & TACTICS
# ==============================================================================

CATEGORY_LABELS: Dict[str, Dict[str, str]] = {
    "bank_impersonation": {
        "en": "Bank Impersonation",
        "ms": "Penyamaran Bank",
        "ta": "வங்கி ஆள்மாறாட்டம்",
        "hi": "बैंक प्रतिरूपण धोखाधड़ी",
        "te": "బ్యాంక్ వేషధారణ / ఫిషింగ్"
    },
    "parcel_delivery": {
        "en": "Parcel Delivery Fraud",
        "ms": "Penipuan Penghantaran Bungkusan",
        "ta": "பார்சல் விநியோக மோசடி",
        "hi": "पार्सल डिलीवरी फ्रॉड",
        "te": "పార్సెల్ కొరియర్ డెలివరీ మోసం"
    },
    "delivery_fraud": {
        "en": "Parcel Delivery Fraud",
        "ms": "Penipuan Penghantaran Bungkusan",
        "ta": "பார்சல் விநியோக மோசடி",
        "hi": "पार्सल डिलीवरी फ्रॉड",
        "te": "పార్సెల్ కొరియర్ డెలివరీ మోసం"
    },
    "recruitment_job": {
        "en": "Fake Job Recruitment",
        "ms": "Penipuan Kerja Sambilan",
        "ta": "போலி வேலைவாய்ப்பு மோசடி",
        "hi": "फर्जी नौकरी घोटाला",
        "te": "నకిలీ పార్ట్ టైమ్ జాబ్ మోసం"
    },
    "job_scam": {
        "en": "Fake Job & Task Recruitment",
        "ms": "Penipuan Kerja Sambilan & Tugasan",
        "ta": "போலி வேலை & பணி மோசடி",
        "hi": "फर्जी नौकरी व कार्य घोटाला",
        "te": "నకిలీ జాబ్ & టాస్క్ మోసం"
    },
    "money_scam": {
        "en": "Money Scam / Fake Loan Fraud",
        "ms": "Penipuan Wang & Pinjaman Palsu",
        "ta": "பண மோசடி / போலி கடன் மோசடி",
        "hi": "पैसा व फर्जी लोन घोटाला",
        "te": "డబ్బు మోసం / నకిలీ లోన్ ఫ్రాడ్"
    },
    "investment_crypto": {
        "en": "Crypto / Investment Scheme",
        "ms": "Penipuan Pelaburan Kripto",
        "ta": "கிரிப்டோ முதலீட்டு மோசடி",
        "hi": "क्रिप्टो व निवेश पोंजी स्कीम",
        "te": "క్రిప్టో & పెట్టుబడి పోంజీ స్కీమ్"
    },
    "government_police": {
        "en": "Government / Police Threat",
        "ms": "Penyamaran Polis / Kerajaan",
        "ta": "அரசு / காவல்துறை மிரட்டல்",
        "hi": "पुलिस / सरकारी प्रतिरूपण",
        "te": "పోలీస్ / ప్రభుత్వ బెదిరింపు"
    },
    "tech_support": {
        "en": "Tech Support Scam",
        "ms": "Penipuan Sokongan Teknikal",
        "ta": "தொழில்நுட்ப ஆதரவு மோசடி",
        "hi": "टेक सपोर्ट फ्रॉड",
        "te": "నకిలీ టెక్ సపోర్ట్ మోసం"
    },
    "lottery_prize": {
        "en": "Lottery / Prize Scam",
        "ms": "Penipuan Hadiah Loteri",
        "ta": "லாட்டரி / பரிசு மோசடி",
        "hi": "लॉटरी / इनाम घोटाला",
        "te": "లాటరీ / బహుమతి మోసం"
    },
    "lottery_reward": {
        "en": "Lottery / Prize Reward Scam",
        "ms": "Penipuan Ganjaran & Hadiah Loteri",
        "ta": "லாட்டரி / பரிசு வெகுமதி மோசடி",
        "hi": "लॉटरी व इनाम पुरस्कार घोटाला",
        "te": "లాటరీ / బహుమతి రివార్డ్ మోసం"
    },
    "legitimate": {
        "en": "Legitimate / Ham",
        "ms": "Mesej Sah / Selamat",
        "ta": "முறையான செய்தி (பாதுகாப்பானது)",
        "hi": "वैध संदेश (सुरक्षित)",
        "te": "సురక్షితమైన సాధారణ సందేశం (Ham)"
    }
}

TACTICS_TRANSLATIONS: Dict[str, Dict[str, Dict[str, str]]] = {
    "Artificial Urgency & Coercion": {
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
        },
        "te": {
            "name": "కృత్రిమ అత్యవసరత & అరెస్ట్ బెదిరింపు",
            "desc": "ఖాతా రద్దు లేదా చట్టపరమైన అరెస్ట్ భయాన్ని సృష్టించి బాధితుడిని తొందరపాటు నిర్ణయాలు తీసుకునేలా ఒత్తిడి చేయడం."
        }
    },
    "Financial Bait / Greed Trap": {
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
        },
        "te": {
            "name": "ఆర్థిక ఎర / భారీ లాభాల వల",
            "desc": "అసాధారణమైన రోజువారీ రాబడి, గ్యారెంటీడ్ లాభాలు లేదా నకిలీ లాటరీ ద్వారా మోసగించడం."
        }
    },
    "Credential & Fee Harvesting": {
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
        },
        "te": {
            "name": "ఓటీపీ, పాస్‌వర్డ్ & ఫీజు దోపిడీ",
            "desc": "బ్యాంక్ ఓటీపీ (OTP), రహస్య పాస్‌వర్డ్ లేదా అక్రమ కస్టమ్స్ డ్యూటీ చెల్లింపులను డిమాండ్ చేయడం."
        }
    },
    "Deceptive Infrastructure": {
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
        },
        "te": {
            "name": "మోసపూరిత డొమైన్లు & నకిలీ వెబ్‌సైట్లు",
            "desc": "అధికారిక బ్యాంక్ లేదా బ్రాండ్‌లను పోలిన నకిలీ డొమైన్‌లు లేదా ప్రమాదకరమైన లింకులను ఉపయోగించడం."
        }
    },
    "Loan & Advance Fee Fraud / Money Trap": {
            "ms": {
            "name": "Penipuan Pinjaman & Yuran Pendahuluan",
            "desc": "Menuntut yuran pemprosesan pinjaman awal atau menjanjikan penggandaan wang palsu."
        },
        "ta": {
            "name": "கடன் & முன்கூட்டிய கட்டண மோசடி",
            "desc": "முன்கூட்டியே கடன் செயலாக்க கட்டணம் கோருதல் அல்லது போலி பண இரட்டிப்பு வாக்குறுதி."
        },
        "hi": {
            "name": "लोन व अग्रिम शुल्क धोखाधड़ी / मनी ट्रैप",
            "desc": "लोन प्रोसेसिंग फीस की मांग, पैसे दोगुना करने का लालच या अज्ञात खातों में पैसे ट्रांसफर करने का दबाव।"
        },
        "te": {
            "name": "నకిలీ లోన్ & అడ్వాన్స్ ఫీజు మోసం",
            "desc": "లోన్ ప్రాసెసింగ్ ఫీజు ముందుగా అడగడం లేదా డబ్బును రెట్టింపు చేస్తామని మోసగించడం."
        }
    },
    "Deceptive Job & Task Solicitation": {
            "ms": {
            "name": "Penipuan Pekerjaan & Tugasan Palsu",
            "desc": "Memikat mangsa dengan tawaran kerja sambilan palsu atau tugasan video berbayar."
        },
        "ta": {
            "name": "போலி வேலைவாய்ப்பு & பணி தூண்டில்",
            "desc": "வீடியோ லைக் அல்லது போலி ஆன்லைன் வேலைகள் மூலம் பணத்தை ஏமாற்றுதல்."
        },
        "hi": {
            "name": "फर्जी नौकरी व कार्य प्रलोभन",
            "desc": "घर बैठे वीडियो लाइक करने या टास्क पूरा करने के नाम पर पैसे की ठगी।"
        },
        "te": {
            "name": "నకిలీ ఉద్యోగ ఎర & టాస్క్ మోసం",
            "desc": "యూట్యూబ్ వీడియో లైక్స్ లేదా రివ్యూల పేరుతో బాధితులను ప్రలోభపెట్టడం."
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
        "money": [
            "💸 Licensed lenders and banks NEVER solicit loans or demand upfront processing/clearance fees via WhatsApp or SMS."
        ],
        "safe": [
            "✅ This message appears legitimate, but always exercise standard vigilance with incoming messages."
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
        "money": [
            "💸 Pemberi pinjaman wang berlesen TIDAK AKAN meminta bayaran yuran pendahuluan atau memproses pinjaman melalui SMS/WhatsApp."
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
        "money": [
            "💸 உரிமம் பெற்ற நிதி நிறுவனங்கள் ஒருபோதும் வாட்ஸ்அப் அல்லது எஸ்எம்எஸ் மூலம் முன்கூட்டியே கட்டணம் கோர மாட்டார்கள்."
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
        "money": [
            "💸 वैध वित्तीय संस्थान या बैंक कभी भी व्हाट्सएप/एसएमएस पर बिना जांच के लोन देने या एडवांस फीस की मांग नहीं करते।"
        ],
        "safe": [
            "✅ यह संदेश सुरक्षित प्रतीत होता है, फिर भी व्यक्तिगत जानकारी साझा करते समय सतर्कता बरतें।"
        ]
    },
    "te": {
        "scam_general": [
            "⚠️ ఈ సందేశంలోని ఎటువంటి లింకులను క్లిక్ చేయవద్దు లేదా ఫైల్స్‌ను డౌన్‌లోడ్ చేయవద్దు.",
            "🚫 మీ బ్యాంక్ ఓటీపీ (OTP), పాస్‌వర్డ్, యూపీఐ పిన్ లేదా ఆధార్ వివరాలను ఎవరికీ చెప్పవద్దు.",
            "📢 అధికారిక సైబర్ క్రైమ్ పోర్టల్ లేదా ScamShield యాప్ ద్వారా ఈ మోసపూరిత సందేశాన్ని నివేదించండి."
        ],
        "bank": [
            "🏦 మీ బ్యాంక్ ఖాతా వివరాలను తనిఖీ చేయడానికి నేరుగా అధికారిక బ్యాంక్ యాప్‌లో లాగిన్ అవ్వండి, సందేశంలోని లింకుల ద్వారా కాదు."
        ],
        "parcel": [
            "📦 పార్సెల్ స్థితిని అధికారిక కొరియర్ వెబ్‌సైట్ లేదా యాప్‌లో మాత్రమే ఒరిజినల్ ట్రాకింగ్ నంబర్‌తో పరిశీలించండి."
        ],
        "police": [
            "🛡️ పోలీసులు లేదా ప్రభుత్వ అధికారులు ఎప్పుడూ ఫోన్ కాల్స్ లేదా ఎస్ఎంఎస్ ద్వారా డిజిటల్ అరెస్ట్ చేయరు లేదా డబ్బు అడగరు."
        ],
        "job": [
            "💼 గుర్తింపు పొందిన సంస్థలు వాట్సాప్ లేదా టెలిగ్రామ్ ద్వారా వీడియో లైక్స్ పేరుతో ఎక్కువ జీతం ఇచ్చే పనులను ఆఫర్ చేయవు."
        ],
        "money": [
            "💸 చట్టబద్ధమైన బ్యాంకులు లేదా ఫైనాన్స్ సంస్థలు ఎప్పుడూ వాట్సాప్/ఎస్ఎంఎస్ ద్వారా లోన్ ప్రాసెసింగ్ ఫీజు ముందుగా అడగవు."
        ],
        "safe": [
            "✅ ఈ సందేశం సురక్షితమైనదిగా కనిపిస్తోంది, అయినప్పటికీ వ్యక్తిగత వివరాలను పంచుకునేటప్పుడు జాగ్రత్త వహించండి."
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
    ),
    "te": (
        "🛡️ [SCAMSHIELD సైబర్ భద్రతా హెచ్చరిక]\n"
        "హెచ్చరిక: ఈ సందేశం అనుమానాస్పద 【{category}】గా గుర్తించబడింది (ప్రమాద తీవ్రత: {risk_score}%).\n"
        "బాహ్య లింకులను క్లిక్ చేయవద్దు; మీ బ్యాంక్ ఓటీపీ (OTP) లేదా డబ్బును ఎవరికీ పంపవద్దు."
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
        elif "money" in category or "loan" in category:
            advice.extend(advice_dict.get("money", []))
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
