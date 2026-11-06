"""
ScamShield Explainability Engine (XAI)
Provides transparent, interpretable threat assessments, identifying psychological
manipulation tactics, flagged tokens, risk scores, and actionable defense guidance.
"""

from typing import Dict, List, Any, Optional
from src.preprocessor import (
    extract_urls,
    analyze_url,
    extract_phone_numbers,
    detect_pattern_triggers,
    compute_linguistic_features
)
from src.localization import (
    get_current_language,
    get_category_label,
    get_localized_tactics,
    get_localized_safety_advice,
    detect_language,
    load_user_preferences
)

class ScamExplainer:
    def __init__(self):
        pass

    def explain(
        self,
        text: str,
        is_scam: bool,
        scam_prob: float,
        category: str,
        lang: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Builds a comprehensive explanation breakdown for an analyzed message,
        with multi-language customization support.
        """
        prefs = load_user_preferences()
        if lang:
            active_lang = lang
        elif prefs.get("auto_detect_language", True):
            active_lang = detect_language(text)
        else:
            active_lang = get_current_language()
        urls = extract_urls(text)
        phones = extract_phone_numbers(text)
        patterns = detect_pattern_triggers(text)
        ling = compute_linguistic_features(text)

        # Analyze URLs
        url_analyses = [analyze_url(u) for u in urls]
        max_url_risk = max([u["url_risk_score"] for u in url_analyses], default=0)

        # Compute dynamic risk score (0-100)
        # Combines ML probability with explicit heuristic signals
        base_score = scam_prob * 100.0
        heuristic_boost = 0.0

        if max_url_risk > 0:
            heuristic_boost += (max_url_risk * 0.3)
        if len(patterns["urgency_triggers"]) > 0:
            heuristic_boost += 15.0
        if len(patterns["credential_triggers"]) > 0:
            heuristic_boost += 15.0
        if len(patterns["bait_triggers"]) > 0:
            heuristic_boost += 10.0

        if is_scam:
            risk_score = min(100.0, max(base_score, 50.0 + heuristic_boost * 0.5))
        else:
            # If deemed legitimate by ML, but has heuristic triggers, score slightly higher than 0
            risk_score = min(base_score + (heuristic_boost * 0.2), 35.0)

        risk_score = round(risk_score, 1)

        # Categorize Risk Level
        if risk_score >= 80:
            risk_level = "CRITICAL DANGER"
            risk_badge = "🔴 Critical"
        elif risk_score >= 50:
            risk_level = "HIGH RISK"
            risk_badge = "🟠 High Risk"
        elif risk_score >= 25:
            risk_level = "SUSPICIOUS"
            risk_badge = "🟡 Suspicious"
        else:
            risk_level = "SAFE"
            risk_badge = "🟢 Safe / Ham"

        # Identify Social Engineering Tactics
        tactics = []
        if len(patterns["urgency_triggers"]) > 0:
            tactics.append({
                "tactic": "Artificial Urgency & Coercion",
                "description": "Uses time pressure or threat of loss/penalties to rush victim into action without thinking.",
                "evidence": patterns["urgency_triggers"]
            })
        if len(patterns["bait_triggers"]) > 0:
            tactics.append({
                "tactic": "Financial Bait / Greed Trap",
                "description": "Promises unrealistic financial gains, lottery prizes, or guaranteed returns.",
                "evidence": patterns["bait_triggers"]
            })
        if len(patterns["credential_triggers"]) > 0:
            tactics.append({
                "tactic": "Credential & Fee Harvesting",
                "description": "Solicits personal authentication credentials, OTPs, or upfront release fees.",
                "evidence": patterns["credential_triggers"]
            })

        for ua in url_analyses:
            if ua["reasons"]:
                tactics.append({
                    "tactic": "Deceptive Infrastructure",
                    "description": f"Domain '{ua['domain']}' exhibits deceptive indicators.",
                    "evidence": ua["reasons"]
                })

        # Flagged Token Highlighting
        flagged_tokens = set()
        for trig_list in patterns.values():
            for trig in trig_list:
                for token in trig.split():
                    if len(token) > 2:
                        flagged_tokens.add(token.lower())
        for ua in url_analyses:
            flagged_tokens.add(ua["url"])

        # Prescriptive Safety Advice (Localized)
        advice = get_localized_safety_advice(category, is_scam, risk_score, lang=active_lang)
        localized_tactics = get_localized_tactics(tactics, lang=active_lang)
        category_label = get_category_label(category, lang=active_lang)

        # Localized Summary
        if is_scam:
            summary = f"Flagged as {category_label} ({category.replace('_', ' ').title()}) with {risk_score}% risk. {len(tactics)} attack tactics identified."
        else:
            summary = "Message analyzed as safe legitimate communication." if active_lang == "en" else f"消息研判为合法安全通讯 ({category_label})。"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_badge": risk_badge,
            "category": category,
            "category_label": category_label,
            "language": active_lang,
            "scam_probability": round(scam_prob, 4),
            "tactics_detected": localized_tactics,
            "raw_tactics": tactics,
            "flagged_tokens": sorted(list(flagged_tokens)),
            "extracted_urls": url_analyses,
            "extracted_phones": phones,
            "safety_advice": advice,
            "summary": summary
        }
