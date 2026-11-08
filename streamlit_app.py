"""
ScamShield AI - Streamlit Community Cloud Root Launcher
======================================================
Production self-healing launcher that automatically handles:
- Linux & Windows path normalizations (backslashes in zip files)
- Auto-extracting uploaded .zip packages safely
- Bidirectional syncing between root and src/
- Ensuring challenge/, models/, and data/ paths are always populated
- sys.modules registration so 'src.localization' and 'localization' never throw ModuleNotFoundError
"""

import os
import sys
import shutil
import zipfile
import types

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

src_dir = os.path.join(ROOT_DIR, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 1. Linux Backslash Sanitizer:
# When Windows zips are extracted on Linux, files like "src\\localization.py"
# become literal filenames in ROOT_DIR instead of creating proper directories.
try:
    for fname in os.listdir(ROOT_DIR):
        if "\\" in fname:
            bad_path = os.path.join(ROOT_DIR, fname)
            clean_subpath = fname.replace("\\", "/")
            good_path = os.path.join(ROOT_DIR, clean_subpath)
            os.makedirs(os.path.dirname(good_path), exist_ok=True)
            if not os.path.exists(good_path):
                shutil.copy2(bad_path, good_path)
            try:
                os.remove(bad_path)
            except Exception:
                pass
except Exception:
    pass

# 2. Self-healing Zip Package Extractor with Cross-Platform Path Normalization:
for item in os.listdir(ROOT_DIR):
    if item.endswith(".zip"):
        zip_path = os.path.join(ROOT_DIR, item)
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                for member in z.infolist():
                    norm_name = member.filename.replace("\\", "/")
                    if not norm_name or norm_name.endswith("/"):
                        continue
                    target_file = os.path.join(ROOT_DIR, norm_name)
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    if not os.path.exists(target_file):
                        with z.open(member) as src_f, open(target_file, "wb") as dst_f:
                            shutil.copyfileobj(src_f, dst_f)
            print(f"[ScamShield Launcher] Auto-extracted package: {item}")
        except Exception as e:
            print(f"[ScamShield Launcher] Zip extraction notice for {item}: {e}")

# 3. Ensure src/ directory exists & populated with all python modules
os.makedirs(src_dir, exist_ok=True)
init_src = os.path.join(src_dir, "__init__.py")
if not os.path.exists(init_src):
    with open(init_src, "w", encoding="utf-8") as f:
        f.write("# ScamShield Package\n")

# Bidirectional sync: copy all python files between root and src/
# so both 'from src.module import ...' and 'from module import ...' work consistently
for item in os.listdir(ROOT_DIR):
    item_path = os.path.join(ROOT_DIR, item)
    if os.path.isfile(item_path) and item.endswith(".py") and item != "streamlit_app.py":
        dst_path = os.path.join(src_dir, item)
        if not os.path.exists(dst_path):
            try:
                shutil.copy2(item_path, dst_path)
            except Exception:
                pass

if os.path.exists(src_dir):
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        if os.path.isfile(src_path) and item.endswith(".py") and item != "__init__.py":
            dst_path = os.path.join(ROOT_DIR, item)
            if not os.path.exists(dst_path):
                try:
                    shutil.copy2(src_path, dst_path)
                except Exception:
                    pass

# 4. Synthesize localization.py on disk if completely absent
loc_src = os.path.join(src_dir, "localization.py")
loc_root = os.path.join(ROOT_DIR, "localization.py")
if not os.path.exists(loc_src) and not os.path.exists(loc_root):
    fallback_loc_code = '''"""ScamShield Fallback Localization Module"""
from typing import Dict, List, Any, Optional

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {
    "en": {"code": "en", "name": "English", "native_name": "English", "flag": "🇬🇧", "region": "India / Global"},
    "te": {"code": "te", "name": "Telugu", "native_name": "తెలుగు", "flag": "🇮🇳", "region": "Andhra Pradesh / Telangana"},
    "hi": {"code": "hi", "name": "Hindi", "native_name": "हिन्दी", "flag": "🇮🇳", "region": "India"},
    "ta": {"code": "ta", "name": "Tamil", "native_name": "தமிழ்", "flag": "🇮🇳", "region": "Tamil Nadu"},
    "ms": {"code": "ms", "name": "Malay", "native_name": "Bahasa Melayu", "flag": "🇲🇾", "region": "Malaysia"}
}
_STRINGS = {
    "app_title": "🛡️ ScamShield Multi-Channel Fraud Defense System",
    "app_subtitle": "Detect, analyze, and intercept deceptive cyber-fraud in real time.",
    "sidebar_title": "🛡️ ScamShield AI",
    "sidebar_desc": "Autonomous Multi-Channel Defense",
    "core_engine": "Core Engine",
    "channels_protected": "Channels Protected:",
    "channel_sms": "💬 SMS / Smishing",
    "channel_wa": "📱 WhatsApp Notifications",
    "channel_tg": "✈️ Telegram Channel & Bot Guard",
    "channel_email": "📧 Email Phishing & BEC",
    "channel_clip": "📋 Clipboard / Link Guard",
    "channel_qr": "📷 Quishing (QR Code Phishing)",
    "sidebar_caption": "Inspired by Singapore ScamShield initiative.",
    "lang_selector": "🌐 Language Preferences",
    "tab_sms": "🔍 SMS Message Scanner",
    "tab_wa": "📱 WhatsApp Guardian",
    "tab_tg": "✈️ Telegram Guardian",
    "tab_email": "📧 Email Phishing Scanner",
    "tab_clip": "📋 Clipboard & Browser Shield",
    "tab_qr": "📷 Quishing (QR Phishing) Audit",
    "tab_prefs": "⚙️ Language & Localization Preferences",
    "tab_challenge": "🏆 NLP Challenge & Leaderboard",
    "tab_api": "🔌 Multi-Channel REST API",
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
    "action_taken": "Action Taken"
}
def t(k, lang=None, **kwargs):
    s = _STRINGS.get(k, k)
    if kwargs:
        try: s = s.format(**kwargs)
        except Exception: pass
    return s
def get_current_language(): return "en"
def set_current_language(code): return "en"
def load_user_preferences(): return {"language": "en", "auto_detect_language": True}
def save_user_preferences(prefs): return prefs
def get_localized_presets(lang=None): return []
def get_category_label(cat, lang=None): return cat.replace("_", " ").title()
def generate_auto_reply_warning(sender, text, is_scam, prob, cat, lang=None):
    return f"⚠️ [SCAMSHIELD ADVISORY]: Suspected {cat.replace('_', ' ').title()} threat detected ({prob*100:.1f}% risk)."
def detect_language(text): return "en"
def get_localized_tactics(tactics, lang=None): return tactics
def get_localized_safety_advice(category, is_scam, risk_score, lang=None):
    if not is_scam: return ["Message appears safe. Exercise standard caution with unknown links."]
    return [
        "Do NOT click on any embedded URLs or verify credentials via phone numbers provided.",
        "Verify independently by contacting the official institution directly using a known trusted number.",
        "Never share One-Time Passwords (OTPs), PINs, or banking login credentials.",
        "Report this fraudulent message immediately to your telecommunications carrier."
    ]
'''
    try:
        with open(loc_src, "w", encoding="utf-8") as f:
            f.write(fallback_loc_code)
        with open(loc_root, "w", encoding="utf-8") as f:
            f.write(fallback_loc_code)
    except Exception:
        pass

# 5. Pre-register sys.modules packages so 'from src.localization' NEVER fails
if "src" not in sys.modules:
    src_mod = types.ModuleType("src")
    src_mod.__path__ = [src_dir]
    sys.modules["src"] = src_mod

try:
    if "localization" not in sys.modules:
        import localization
        sys.modules["src.localization"] = localization
        sys.modules["localization"] = localization
except Exception:
    pass

# 6. Ensure challenge/ directory exists & populated
challenge_dir = os.path.join(ROOT_DIR, "challenge")
os.makedirs(challenge_dir, exist_ok=True)
if challenge_dir not in sys.path:
    sys.path.insert(0, challenge_dir)

init_challenge = os.path.join(challenge_dir, "__init__.py")
if not os.path.exists(init_challenge):
    with open(init_challenge, "w", encoding="utf-8") as f:
        f.write("")

challenge_files = [
    "evaluate_submission.py", "leaderboard.py", "leaderboard.json",
    "sample_submission.csv", "submission.csv", "submission_advanced.csv",
    "baseline_submission.py", "advanced_submission.py",
    "benchmark_analysis.py", "benchmark_metrics.json"
]
for f in challenge_files:
    r_path = os.path.join(ROOT_DIR, f)
    c_path = os.path.join(challenge_dir, f)
    if os.path.exists(r_path) and not os.path.exists(c_path):
        try: shutil.copy2(r_path, c_path)
        except Exception: pass
    elif os.path.exists(c_path) and not os.path.exists(r_path):
        try: shutil.copy2(c_path, r_path)
        except Exception: pass

# 7. Ensure models/ directory exists & populated
model_dir = os.path.join(ROOT_DIR, "models")
os.makedirs(model_dir, exist_ok=True)
model_files = ["scamshield_model.joblib"]
for f in model_files:
    r_path = os.path.join(ROOT_DIR, f)
    m_path = os.path.join(model_dir, f)
    if os.path.exists(r_path) and not os.path.exists(m_path):
        try: shutil.copy2(r_path, m_path)
        except Exception: pass
    elif os.path.exists(m_path) and not os.path.exists(r_path):
        try: shutil.copy2(m_path, r_path)
        except Exception: pass

# 8. Ensure data/ directory exists & populated
data_dir = os.path.join(ROOT_DIR, "data")
os.makedirs(data_dir, exist_ok=True)
data_files = [
    "train.csv", "val.csv", "test_ground_truth.csv", "test_unlabeled.csv",
    "dataset_generator.py", "preferences.json"
]
for f in data_files:
    r_path = os.path.join(ROOT_DIR, f)
    d_path = os.path.join(data_dir, f)
    if os.path.exists(r_path) and not os.path.exists(d_path):
        try: shutil.copy2(r_path, d_path)
        except Exception: pass
    elif os.path.exists(d_path) and not os.path.exists(r_path):
        try: shutil.copy2(d_path, r_path)
        except Exception: pass

# 9. Locate master app script
if os.path.exists(os.path.join(src_dir, "app.py")):
    APP_PATH = os.path.join(src_dir, "app.py")
elif os.path.exists(os.path.join(ROOT_DIR, "app.py")):
    APP_PATH = os.path.join(ROOT_DIR, "app.py")
else:
    found = None
    for root_folder, dirs, files in os.walk(ROOT_DIR):
        if "app.py" in files:
            found = os.path.join(root_folder, "app.py")
            break
    if found:
        APP_PATH = found
    else:
        raise FileNotFoundError(f"Could not locate app.py in {ROOT_DIR} or any subfolder.")

app_dir = os.path.dirname(APP_PATH)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# 10. Execute main dashboard app
with open(APP_PATH, "r", encoding="utf-8") as f:
    code = f.read()

exec(compile(code, APP_PATH, "exec"), globals())
