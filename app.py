"""
ScamShield NLP Multi-Channel Defense Dashboard
Interactive Operations Center for SMS, WhatsApp Notification Guardian,
Telegram Guardian, Email Phishing Scanner, Clipboard Shield, QR Quishing Audit,
Language Preferences, and NLP Challenge Evaluation.
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
from src.localization import (
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
    t,
    get_current_language,
    set_current_language,
    load_user_preferences,
    save_user_preferences,
    get_localized_presets,
    get_category_label,
    generate_auto_reply_warning,
    detect_language
)
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

# Load User Preferences
user_prefs = load_user_preferences()

if "preferred_lang" not in st.session_state:
    st.session_state["preferred_lang"] = user_prefs.get("preferred_language", DEFAULT_LANGUAGE)

curr_lang = st.session_state["preferred_lang"]
if curr_lang not in SUPPORTED_LANGUAGES:
    curr_lang = DEFAULT_LANGUAGE

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/shield.png", width=70)
st.sidebar.title(t("sidebar_title", curr_lang))
st.sidebar.markdown(t("sidebar_desc", curr_lang))

st.sidebar.markdown("---")
st.sidebar.subheader(t("lang_selector", curr_lang))

# Language selection dropdown in sidebar
lang_codes = list(SUPPORTED_LANGUAGES.keys())
lang_labels = [
    f"{SUPPORTED_LANGUAGES[code]['flag']} {SUPPORTED_LANGUAGES[code]['native_name']} ({SUPPORTED_LANGUAGES[code]['name']})"
    for code in lang_codes
]
current_lang_idx = lang_codes.index(curr_lang) if curr_lang in lang_codes else 0

selected_lang_label = st.sidebar.selectbox(
    "Select Language / 选择语言:",
    options=lang_labels,
    index=current_lang_idx,
    key="sb_language_selector"
)
selected_lang_code = lang_codes[lang_labels.index(selected_lang_label)]

if selected_lang_code != curr_lang:
    st.session_state["preferred_lang"] = selected_lang_code
    set_current_language(selected_lang_code)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(f"**{t('core_engine', curr_lang)}**: {'🟢 Ready' if pipeline.is_ready else '🔴 Off'}")
st.sidebar.markdown(f"**{t('channels_protected', curr_lang)}**")
st.sidebar.markdown(f"- {t('channel_sms', curr_lang)}")
st.sidebar.markdown(f"- {t('channel_wa', curr_lang)}")
st.sidebar.markdown(f"- {t('channel_tg', curr_lang)}")
st.sidebar.markdown(f"- {t('channel_email', curr_lang)}")
st.sidebar.markdown(f"- {t('channel_clip', curr_lang)}")
st.sidebar.markdown(f"- {t('channel_qr', curr_lang)}")
st.sidebar.markdown("---")
st.sidebar.caption(t("sidebar_caption", curr_lang))

# ==========================================
# MAIN HEADER & NAVIGATION TABS
# ==========================================
st.title(t("app_title", curr_lang))
st.markdown(t("app_subtitle", curr_lang))

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    t("tab_sms", curr_lang),
    t("tab_wa", curr_lang),
    t("tab_tg", curr_lang),
    t("tab_email", curr_lang),
    t("tab_clip", curr_lang),
    t("tab_qr", curr_lang),
    t("tab_prefs", curr_lang),
    t("tab_challenge", curr_lang),
    t("tab_api", curr_lang)
])

# ==========================================
# TAB 1: SMS MESSAGE SCANNER
# ==========================================
with tab1:
    st.subheader(t("tab_sms", curr_lang))
    st.markdown("Select a preset scenario or type any incoming suspicious message:")

    # Load localized presets for the active language
    localized_presets = get_localized_presets(curr_lang)
    preset_keys = [t("custom_input", curr_lang)] + list(localized_presets.keys())
    
    preset_choice = st.selectbox(
        t("load_scenario", curr_lang),
        options=preset_keys,
        key="sms_preset_selector"
    )
    
    default_text = ""
    if preset_choice != t("custom_input", curr_lang) and preset_choice in localized_presets:
        default_text = localized_presets[preset_choice]

    user_input = st.text_area(
        t("message_to_inspect", curr_lang),
        value=default_text,
        height=110,
        placeholder="e.g. URGENT: Your bank account will be frozen. Click link to verify...",
        key="sms_input_area"
    )

    if st.button(t("run_deep_scan", curr_lang), type="primary", key="btn_scan_sms"):
        if not user_input.strip():
            st.warning("Please enter a message to scan.")
        else:
            with st.spinner(t("analyzing", curr_lang)):
                res = pipeline.scan_message(user_input, lang=curr_lang)

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric(
                t("risk_score", curr_lang),
                f"{res['risk_score']}%",
                res["risk_level"],
                delta_color="inverse" if res["is_scam"] else "normal"
            )
            c2.metric(
                t("classification", curr_lang),
                res["label"].upper(),
                res.get("category_label", res["category"].replace("_", " ").title())
            )
            c3.metric(
                t("scam_probability", curr_lang),
                f"{res['scam_probability'] * 100:.1f}%"
            )

            st.progress(min(1.0, res["risk_score"] / 100.0))

            cd1, cd2 = st.columns(2)
            with cd1:
                st.markdown(f"#### {t('tactics_detected_header', curr_lang)}")
                if res["tactics_detected"]:
                    for tac in res["tactics_detected"]:
                        st.warning(f"**{tac['tactic']}**\n\n{tac['description']}")
                else:
                    st.success(t("no_tactics", curr_lang))

            with cd2:
                st.markdown(f"#### {t('extracted_urls_header', curr_lang)}")
                if res["extracted_urls"]:
                    for u in res["extracted_urls"]:
                        st.info(f"**URL:** `{u['url']}`\n- Risk Score: **{u['url_risk_score']}/100**")
                else:
                    st.write(t("no_urls", curr_lang))

            st.subheader(t("safety_checklist_header", curr_lang))
            for item in res["safety_advice"]:
                st.markdown(f"- {item}")

# ==========================================
# TAB 2: WHATSAPP NOTIFICATION GUARDIAN
# ==========================================
with tab2:
    st.subheader(t("wa_title", curr_lang))
    st.markdown(t("wa_desc", curr_lang))

    col_wa_in, col_wa_phone = st.columns([3, 2])

    with col_wa_in:
        wa_sender_name = st.text_input(t("wa_sender_name", curr_lang), value="Dave (Recruitment HR)")
        wa_sender_num = st.text_input(t("wa_sender_num", curr_lang), value="+65 8921 4452")
        wa_is_group = st.checkbox(t("wa_is_group", curr_lang), value=True)
        wa_group_name = st.text_input(t("wa_group_name", curr_lang), value="Singapore Part-Time Job Seekers") if wa_is_group else None
        
        wa_default_msg = (
            "Hi all! Earn $300-$800 daily working from home! Simple task: like YouTube videos and review products. Daily payout via PayNow. Register: http://job-daily-income.xyz"
            if curr_lang == "en" else
            "居家兼职诚招人员！每天轻松点赞YouTube视频和评测商品，日赚$200-$600新币，当日PayNow结算。立即添加WhatsApp: +65 8921 4452"
            if curr_lang == "zh" else
            "Jana $200-$600 sehari bekerja dari rumah! Tugas mudah: tonton dan like video YouTube. Bayaran harian via PayNow: http://job-daily-income.xyz"
        )
        wa_body = st.text_area(t("wa_body", curr_lang), value=wa_default_msg, height=110)

    with col_wa_phone:
        st.markdown(f"#### {t('wa_sim_header', curr_lang)}")
        if st.button(t("wa_sim_btn", curr_lang), type="primary", key="btn_sim_wa"):
            msg_obj = WhatsAppMessage(
                sender_name=wa_sender_name,
                sender_number=wa_sender_num,
                message_text=wa_body,
                is_group=wa_is_group,
                group_name=wa_group_name
            )
            alert = whatsapp_guardian.inspect_message(msg_obj, lang=curr_lang)

            if alert["risk_score"] >= 50:
                st.error(
                    f"""
                    **{alert['notification_icon']} {t('wa_intercept_alert', curr_lang)}**  
                    **From:** {alert['sender']}  
                    **Group:** {alert.get('group_name') or 'Direct Message'}  
                    **{t('risk_score', curr_lang)}:** {alert['risk_score']}% ({alert['risk_level']})  
                    **{t('typology', curr_lang)}:** {get_category_label(alert['category'], curr_lang)}  
                    **{t('action_taken', curr_lang)}:** `{alert['action_taken']}`
                    """
                )
            else:
                st.success(
                    f"""
                    **{alert['notification_icon']} {t('wa_safe_notice', curr_lang)}**  
                    **From:** {alert['sender']}  
                    **Status:** Delivered normally.
                    """
                )

            if alert["auto_reply_warning"]:
                st.markdown(f"#### {t('wa_auto_reply_header', curr_lang)}")
                st.code(alert["auto_reply_warning"], language="text")

# ==========================================
# TAB 3: TELEGRAM GUARDIAN
# ==========================================
with tab3:
    st.subheader(t("tg_title", curr_lang))
    st.markdown(t("tg_desc", curr_lang))

    tg_col1, tg_col2 = st.columns(2)
    with tg_col1:
        tg_user = st.text_input(t("tg_user", curr_lang), value="@Binance_VIP_QuantBot")
        tg_is_bot = st.checkbox(t("tg_is_bot", curr_lang), value=True)
    with tg_col2:
        tg_chat = st.text_input(t("tg_chat", curr_lang), value="SG VIP Crypto Signals & Arbitrage")
        tg_is_channel = st.checkbox(t("tg_is_channel", curr_lang), value=False)

    tg_default_body = (
        "Exclusive VIP Crypto Signals! Guaranteed 300% to 500% returns in 7 days using automated AI quant bot. Join Telegram bot @binance_yield_bot or http://binance-vault-promo.live"
        if curr_lang != "zh" else
        "内部VIP加密货币投资！AI量化机器人交易，7天保证300%-500%无风险超高回报。立即加入Telegram机器人 @binance_yield_bot 或访问 http://binance-vault-promo.live"
    )
    tg_text = st.text_area(t("tg_body", curr_lang), value=tg_default_body, height=100)

    if st.button(t("tg_btn", curr_lang), type="primary", key="btn_tg"):
        msg = TelegramMessage(
            sender_username=tg_user,
            message_text=tg_text,
            chat_title=tg_chat,
            is_bot=tg_is_bot,
            is_channel=tg_is_channel
        )
        tg_alert = telegram_guardian.inspect_message(msg, lang=curr_lang)

        tc1, tc2, tc3 = st.columns(3)
        tc1.metric(t("risk_score", curr_lang), f"{tg_alert['risk_score']}%", tg_alert["risk_level"], delta_color="inverse" if tg_alert["risk_score"] >= 50 else "normal")
        tc2.metric(t("typology", curr_lang), get_category_label(tg_alert["category"], curr_lang))
        tc3.metric(t("action_taken", curr_lang), tg_alert["action_taken"])

        st.progress(min(1.0, tg_alert["risk_score"] / 100.0))

        if tg_alert["auto_reply_warning"]:
            st.markdown(f"#### {t('tg_auto_reply_header', curr_lang)}")
            st.code(tg_alert["auto_reply_warning"], language="text")

# ==========================================
# TAB 4: EMAIL PHISHING SCANNER
# ==========================================
with tab4:
    st.subheader(t("em_title", curr_lang))
    st.markdown(t("em_desc", curr_lang))

    em_sender = st.text_input(t("em_sender", curr_lang), value="hr-payroll@dbs-corp-service.xyz")
    em_reply_to = st.text_input(t("em_reply_to", curr_lang), value="shadow-account@gmail.com")
    em_subject = st.text_input(t("em_subject", curr_lang), value="URGENT: Payroll Verification & IRAS Tax Settlement")
    em_body = st.text_area(
        t("em_body", curr_lang),
        value="Dear Employee,\n\nOur annual IRAS audit detected an outstanding tax penalty of $1,420 under your account. Failure to verify and settle within 24 hours will result in salary freeze and court subpoena.\n\nSettle invoice immediately at: http://iras-tax-clearance.vip\n\nFinance Department",
        height=140
    )

    if st.button(t("em_btn", curr_lang), type="primary", key="btn_em"):
        em_res = email_scanner.scan_email(
            sender_email=em_sender,
            subject=em_subject,
            body=em_body,
            reply_to=em_reply_to,
            lang=curr_lang
        )

        st.markdown("---")
        em_c1, em_c2, em_c3 = st.columns(3)
        em_c1.metric(t("em_risk_score", curr_lang), f"{em_res['email_risk_score']}%", em_res["threat_tier"])
        em_c2.metric(t("em_domain_mismatch", curr_lang), "YES (Spoofed)" if em_res["domain_mismatch"] else "NO")
        em_c3.metric(t("em_verdict", curr_lang), "BLOCKED" if em_res["is_phishing"] else "CLEAN")

        if em_res["flags"]:
            st.error(t("em_anomalies", curr_lang))
            for flag in em_res["flags"]:
                st.markdown(f"- ⚠️ {flag}")

        if em_res["urls"]:
            st.warning(t("em_urls", curr_lang))
            for u in em_res["urls"]:
                st.markdown(f"- Link: `{u['url']}` (Risk: **{u['url_risk_score']}/100**)")

# ==========================================
# TAB 5: CLIPBOARD & BROWSER SHIELD
# ==========================================
with tab5:
    st.subheader(t("clip_title", curr_lang))
    st.markdown(t("clip_desc", curr_lang))

    clip_input = st.text_area(
        t("clip_input", curr_lang),
        value="SingPost: Your package is held at terminal hub due to unpaid customs fee of $2.50. Pay fee: http://singpost-tracking-fees.top",
        height=90
    )

    if st.button(t("clip_btn", curr_lang), type="primary", key="btn_clip"):
        clip_alert = clipboard_guard.inspect_clipboard_text(clip_input, lang=curr_lang)
        if clip_alert:
            st.error(
                f"""
                ### {t('clip_alert_header', curr_lang)}
                **Warning:** {clip_alert['warning']}  
                **{t('risk_score', curr_lang)}:** {clip_alert['risk_score']}% ({clip_alert['risk_level']})  
                **{t('typology', curr_lang)}:** {get_category_label(clip_alert['category'], curr_lang)}  
                
                {t('clip_recommendation', curr_lang)}
                """
            )
        else:
            st.success(t("clip_safe", curr_lang))

# ==========================================
# TAB 6: QUISHING (QR PHISHING) AUDIT
# ==========================================
with tab6:
    st.subheader(t("qr_title", curr_lang))
    st.markdown(t("qr_desc", curr_lang))

    qr_col1, qr_col2 = st.columns(2)
    with qr_col1:
        qr_context = st.selectbox(
            t("qr_source", curr_lang),
            [
                "Tampered sticker over public parking ticket machine",
                "Physical mailer / Fake official utility bill",
                "Retail storefront PayNow / SGQR overlay sticker",
                "WhatsApp / Telegram image attachment",
                "Unsolicited parcel delivery note sticker"
            ]
        )
    with qr_col2:
        qr_loc = st.text_input(t("qr_loc", curr_lang), value="Tampines St 21 Public Carpark")

    qr_payload = st.text_area(
        t("qr_payload", curr_lang),
        value="Scan to settle unpaid HDB parking fine of $12.00 immediately: http://hdb-parking-notice.top/paynow",
        height=90
    )

    if st.button(t("qr_btn", curr_lang), type="primary", key="btn_qr"):
        qr_report = quishing_scanner.scan_qr_payload(
            payload_text=qr_payload,
            source_context=qr_context,
            location_tag=qr_loc,
            lang=curr_lang
        )

        qc1, qc2, qc3 = st.columns(3)
        qc1.metric(t("risk_score", curr_lang), f"{qr_report['risk_score']}%", qr_report["threat_level"], delta_color="inverse" if qr_report["risk_score"] >= 50 else "normal")
        qc2.metric(t("typology", curr_lang), get_category_label(qr_report["category"], curr_lang))
        qc3.metric(t("qr_action", curr_lang), qr_report["action_recommendation"])

        st.progress(min(1.0, qr_report["risk_score"] / 100.0))

        if qr_report["url_security_audit"]:
            st.markdown(f"#### {t('qr_domain_audit', curr_lang)}")
            for audit in qr_report["url_security_audit"]:
                st.error(f"**Domain:** `{audit['domain']}` | Risk Score: **{audit['url_risk_score']}/100**")
                for r in audit["reasons"]:
                    st.write(f"- ⚠️ {r}")

        st.subheader(t("qr_prevention", curr_lang))
        for advice in qr_report["safety_checklist"]:
            st.info(f"• {advice}")

# ==========================================
# TAB 7: LANGUAGE PREFERENCES & LOCALIZATION
# ==========================================
with tab7:
    st.subheader(t("pref_title", curr_lang))
    st.markdown(t("pref_desc", curr_lang))

    st.markdown("---")
    col_p1, col_p2 = st.columns([3, 2])

    with col_p1:
        st.markdown("#### ⚙️ Regional & Language Preferences")
        
        pref_lang_selection = st.selectbox(
            t("pref_ui_lang", curr_lang),
            options=lang_codes,
            format_func=lambda c: f"{SUPPORTED_LANGUAGES[c]['flag']} {SUPPORTED_LANGUAGES[c]['native_name']} ({SUPPORTED_LANGUAGES[c]['name']}) - {SUPPORTED_LANGUAGES[c]['region']}",
            index=lang_codes.index(curr_lang) if curr_lang in lang_codes else 0,
            key="pref_main_lang_selector"
        )

        pref_auto_detect = st.checkbox(
            t("pref_auto_detect", curr_lang),
            value=user_prefs.get("auto_detect_language", True),
            help=t("pref_auto_detect_help", curr_lang)
        )

        reply_mode_opts = {
            "preferred": t("pref_reply_opt_preferred", curr_lang),
            "en": t("pref_reply_opt_en", curr_lang),
            "bilingual": t("pref_reply_opt_bilingual", curr_lang)
        }
        current_reply_mode = user_prefs.get("auto_reply_mode", "preferred")
        reply_mode_keys = list(reply_mode_opts.keys())
        reply_mode_idx = reply_mode_keys.index(current_reply_mode) if current_reply_mode in reply_mode_keys else 0

        pref_reply_mode = st.radio(
            t("pref_reply_mode", curr_lang),
            options=reply_mode_keys,
            format_func=lambda k: reply_mode_opts[k],
            index=reply_mode_idx
        )

        if st.button(t("pref_save_btn", curr_lang), type="primary", key="btn_save_prefs"):
            new_prefs = {
                "preferred_language": pref_lang_selection,
                "auto_detect_language": pref_auto_detect,
                "auto_reply_mode": pref_reply_mode
            }
            save_user_preferences(new_prefs)
            st.session_state["preferred_lang"] = pref_lang_selection
            st.success(t("pref_saved_msg", curr_lang))
            st.rerun()

    with col_p2:
        st.markdown("#### 🌐 Supported Official Languages")
        for code, meta in SUPPORTED_LANGUAGES.items():
            is_active = (code == curr_lang)
            with st.container():
                st.markdown(
                    f"""
                    **{meta['flag']} {meta['native_name']} ({meta['name']})** {' *(Active)*' if is_active else ''}  
                    - **Region:** {meta['region']}  
                    - **Description:** {meta['description']}
                    """
                )
                st.markdown("---")

    st.markdown("---")
    st.subheader(t("pref_preview_header", curr_lang))
    st.markdown(t("pref_preview_text", curr_lang))

    preview_cols = st.columns(len(SUPPORTED_LANGUAGES))
    for idx, (p_code, p_meta) in enumerate(SUPPORTED_LANGUAGES.items()):
        with preview_cols[idx]:
            st.markdown(f"**{p_meta['flag']} {p_meta['name']}**")
            sample_warning = generate_auto_reply_warning("bank_impersonation", 85.0, lang=p_code, mode="preferred")
            st.code(sample_warning, language="text")

# ==========================================
# TAB 8: NLP CHALLENGE & LEADERBOARD
# ==========================================
with tab8:
    st.subheader(t("tab_challenge", curr_lang))
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
# TAB 9: MULTI-CHANNEL API DOCS
# ==========================================
with tab9:
    st.subheader(t("tab_api", curr_lang))
    st.markdown("Easily integrate ScamShield into WhatsApp Business, Telegram Bots, Email Gateways, or Quishing Scanners:")

    st.markdown("#### 1. Language Preferences API")
    st.code(
        """import requests

# 1. Fetch supported regional and international languages
langs = requests.get("http://localhost:8000/languages").json()
print("Supported Languages:", list(langs["supported_languages"].keys()))

# 2. Update user preferred defense language to Chinese ("zh"), Malay ("ms"), Tamil ("ta"), or Hindi ("hi")
requests.post("http://localhost:8000/preferences", json={
    "preferred_language": "zh",
    "auto_detect_language": True,
    "auto_reply_mode": "bilingual"
})
""",
        language="python"
    )

    st.markdown("#### 2. WhatsApp Intercept API with Language Parameter")
    st.code(
        """import requests

payload = {
    "sender_name": "Dave (Recruiter)",
    "sender_number": "+65 8921 4452",
    "message_text": "Earn $500 daily liking YouTube videos! Message HR now.",
    "lang": "zh"  # Response & Auto-Reply generated in preferred language
}

res = requests.post("http://localhost:8000/whatsapp/scan", json=payload)
data = res.json()
print("Action Taken:", data["action_taken"])
print("Auto-Reply:", data["auto_reply_warning"])
""",
        language="python"
    )

    st.markdown("#### 3. Telegram Bot Webhook Call (Python)")
    st.code(
        """import requests

payload = {
    "sender_username": "crypto_quant_bot",
    "message_text": "Exclusive VIP Crypto Signals! Guaranteed 500% ROI in 7 days: http://crypto-vault.xyz",
    "is_bot": True,
    "chat_title": "VIP Trading Group",
    "lang": "en"
}

res = requests.post("http://localhost:8000/telegram/scan", json=payload)
data = res.json()
print("Risk Score:", data["risk_score"])
print("Action Taken:", data["action_taken"])
""",
        language="python"
    )

    st.markdown("#### 4. Quishing (QR Phishing) Audit Call (cURL)")
    st.code(
        """curl -X POST "http://localhost:8000/quishing/scan" \\
     -H "Content-Type: application/json" \\
     -d '{"payload_text": "Scan QR to pay parking fine: http://hdb-parking-notice.top/paynow", "source_context": "Physical parking meter sticker", "lang": "zh"}'
""",
        language="bash"
    )

    st.markdown("#### 5. Email Phishing Inspection Call (cURL)")
    st.code(
        """curl -X POST "http://localhost:8000/email/scan" \\
     -H "Content-Type: application/json" \\
     -d '{"sender_email": "hr@dbs-corp.xyz", "subject": "Urgent Tax Hold", "body": "Verify account: http://iras-tax.vip", "lang": "en"}'
""",
        language="bash"
    )
