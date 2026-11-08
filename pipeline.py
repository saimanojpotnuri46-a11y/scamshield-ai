"""
ScamShield Master Pipeline
Integrates preprocessing, feature extraction, ML classification, and explainability
into an easy-to-use production inference pipeline.
"""

import os
import re
import pandas as pd
from typing import Dict, List, Any, Optional

try:
    from src.models import ScamShieldModel
    from src.explainability import ScamExplainer
    from src.preprocessor import detect_pattern_triggers, extract_urls, extract_phone_numbers
except ModuleNotFoundError:
    from models import ScamShieldModel
    from explainability import ScamExplainer
    from preprocessor import detect_pattern_triggers, extract_urls, extract_phone_numbers

DEFAULT_MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models"
)
DEFAULT_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)

class ScamShieldPipeline:
    def __init__(self, model_dir: str = DEFAULT_MODEL_DIR, auto_init: bool = True):
        self.model_dir = model_dir
        self.model = ScamShieldModel()
        self.explainer = ScamExplainer()
        self.is_ready = False

        if auto_init:
            self._initialize()

    def _initialize(self):
        """Loads existing model from disk, or trains on data/train.csv if not found."""
        model_file = os.path.join(self.model_dir, "scamshield_model.joblib")
        if os.path.exists(model_file):
            print(f"Loading existing ScamShield model from {model_file}...")
            self.model = ScamShieldModel.load(self.model_dir)
            self.is_ready = True
        else:
            train_file = os.path.join(DEFAULT_DATA_DIR, "train.csv")
            val_file = os.path.join(DEFAULT_DATA_DIR, "val.csv")
            if os.path.exists(train_file):
                print(f"No trained model found. Auto-training ScamShield on {train_file}...")
                train_df = pd.read_csv(train_file)
                val_df = pd.read_csv(val_file) if os.path.exists(val_file) else None
                self.train(train_df, val_df)
            else:
                print("Warning: Neither trained model nor training data found. Call train() manually.")

    def train(self, train_df: pd.DataFrame, val_df: pd.DataFrame = None) -> Dict[str, Any]:
        """Trains models and persists to disk."""
        metrics = self.model.fit(train_df, val_df)
        self.model.save(self.model_dir)
        self.is_ready = True
        return metrics

    def resolve_typology_category(self, text: str, ml_cat: str = "legitimate") -> str:
        """
        Intelligently resolves and disambiguates the scam category.
        Ensures each category (bank, delivery, police, lottery, crypto, tech support, job)
        is classified distinctly and accurately without collapsing into 'job_scam'.
        """
        text_lower = text.lower()

        # 1. Tech Support
        tech_patterns = [
            r"\b(virus|trojan|malware|spyware)\b",
            r"\b(microsoft|windows)\s*security\b",
            r"\bmcafee|norton\b",
            r"\bpc\s*(is\s*)?damaged\b",
            r"\bapple\s*id\b.*(suspended|locked|unauthorized)",
            r"వైరస్|ట్రోజన్|కంప్యూటర్|మైక్రోసాఫ్ట్|వైరస్ అలర్ట్"
        ]
        if any(re.search(p, text_lower) for p in tech_patterns):
            return "tech_support"

        # 2. Government & Police Threats
        police_patterns = [
            r"\b(police|spf|interpol|cbi|ed|cid|crime\s*branch)\b",
            r"\barrest\s*warrant\b",
            r"\b(court|subpoena|summons|fir)\b",
            r"\basset\s*seizure\b",
            r"\bmoney\s*laundering\b",
            r"\b(iras|tax)\s*(penalty|overdue|warning|clearance)\b",
            r"పోలీస్|అరెస్ట్ వారెంట్|మనీలాండరింగ్|కోర్టు|వారెంట్|సిబిఐ|క్రైమ్ బ్రాంచ్|వారెంట్ జారీ|పోలీస్ స్టేషన్|वारंट|अरेस्ट वारंट|पुलिस|मनी लॉन्ड्रिंग|கைது ஆணை|காவல்துறை"
        ]
        if any(re.search(p, text_lower) for p in police_patterns):
            return "government_police"

        # 3. Delivery / Courier Fraud
        delivery_patterns = [
            r"\b(parcel|package|shipment|courier|delivery)\b",
            r"\b(singpost|dhl|fedex|usps|ninjavan|speedpost|indiapost|india\s*post|bluedart|dtdc)\b",
            r"\b(customs|clearance)\s*(fee|duty)\b",
            r"\bfailed\s*delivery\b",
            r"\bmissing\s*(address|house\s*number)\b",
            r"\bredelivery\b",
            r"పార్సెల్|కొరియర్|డెలివరీ|షిప్‌మెంట్|పోస్టల్|కస్టమ్స్ ఫీజు|పార్సల్ డెలివరీ|డెలివరీ ఆగిపోయింది|पार्सल|कूरियर|डिलीवरी|சுங்க வரி|பார்சல்"
        ]
        if any(re.search(p, text_lower) for p in delivery_patterns):
            return "delivery_fraud"

        # 4. Bank Impersonation / Netbanking Fraud
        bank_patterns = [
            r"\b(sbi|hdfc|icici|axis|pnb|bob|kotak|canara|union\s*bank|dbs|ocbc|uob|citi|citibank|hsbc|standardchartered|chase|wellsfargo)\b",
            r"\bdigital\s*token\b",
            r"\bunauthorized\s*(login|access|transaction|withdrawal)\b",
            r"\b(card|account)\s*(locked|blocked|deactivated|suspended|frozen)\b",
            r"\b(bank|account)\s*(security|alert|notice|kyc|verification)\b",
            r"\b(pan\s*card|aadhaar)\s*(update|expired|link|verify)\b",
            r"\bnetbanking\b",
            r"బ్యాంక్|ఖాతా|కేవైసీ|పాన్ కార్డ్|డెబిట్ కార్డు|క్రెడిట్ కార్డు|లాగిన్|ఓటీపీ|ఖాతా బ్లాక్|బ్యాంక్ ఖాతా|बैंक|खाता|केवाईसी|डेबिट कार्ड|क्रेडिट कार्ड|வங்கி|டோக்கன்"
        ]
        if any(re.search(p, text_lower) for p in bank_patterns):
            return "bank_impersonation"

        # 5. Lottery & Reward Scam
        lottery_patterns = [
            r"\b(won|winner|winning)\b.*\b(draw|lottery|prize|jackpot|ticket|car|cash)\b",
            r"\blucky\s*draw\b",
            r"\bkbc\b",
            r"\b(grocery|fuel|gift|shopping)\s*voucher\b",
            r"\banniversary\s*giveaway\b",
            r"\bloyalty\s*(reward|points?)\b",
            r"\bcongratulations.*(won|prize|selected)\b",
            r"లక్కీ డ్రా|లాటరీ|బహుమతి|గెలుచుకున్నారు|విన్నర్|జాక్‌పాట్|ఇనామ్|కారు గెలుచుకున్నారు|లక్కీ విన్నర్|लॉटरी|इनाम|बंपर ड्रा|विजेता|பரிசு|லாட்டரி"
        ]
        if any(re.search(p, text_lower) for p in lottery_patterns):
            return "lottery_reward"

        # 6. Crypto & Investment Scheme
        crypto_patterns = [
            r"\b(crypto|bitcoin|btc|ethereum|eth|usdt)\b",
            r"\b(quant\s*bot|trading\s*bot|arbitrage)\b",
            r"\b(staking|apy|roi|presale\s*tokens?)\b",
            r"\bcloud\s*mining\b",
            r"\bforex\b",
            r"\bbinance\b",
            r"\b(stock\s*tips|guaranteed\s*returns?)\b",
            r"క్రిప్టో|బిట్‌కాయిన్|ట్రేడింగ్|షేర్ మార్కెట్|పెట్టుబడి|రెట్టింపు లాభం|రోజువారీ రిటర్న్స్|క్రिप्टో|बिटकॉइन|ट्रेडिंग"
        ]
        if any(re.search(p, text_lower) for p in crypto_patterns):
            return "investment_crypto"

        # 7. Job & Task Recruitment Scams
        job_patterns = [
            r"\b(part-?time|full-?time|remote)\s*(job|work|vacancy|vacancies|position|recruitment)?\b",
            r"\bwork\s*from\s*(home|phone|anywhere|mobile)\b",
            r"\bearn\s*(\$|₹|rs\.?|sgd)?\s*\d+.*(daily|per day|day|a day)\b",
            r"\b(hiring|recruitment|recruiting|recruiter)\b",
            r"\b(like|liking|watch|watching)\s*(youtube|tiktok|videos?)\b",
            r"\b(rate|rating|review|reviewing)\s*(products?|apps?|google\s*maps?)\b",
            r"\b(rating|task|order\s*processing)\s*agents?\b",
            r"\bpartner\s*program\b",
            r"\bhr\s*(department|manager|team|recruiter)?\b",
            r"\b(simple|daily)\s*tasks?\b",
            r"\b(fake\s*anukunna|try\s*cheyandi|nijamgane|vachayi)\b",
            r"ఉద్యోగం|పార్ట్ టైమ్ జాబ్|వర్క్ ఫ్రమ్ హోమ్|వీడియో లైక్స్|రోజువారీ వేతనం|టాస్క్|నకిలీ జాబ్|ట్రై చేయండి|రోజూ సంపాదించండి|नौकरी|पार्ट टाइम जॉब|घर बैठे काम|वीडियो लाइक"
        ]
        if any(re.search(p, text_lower) for p in job_patterns):
            return "job_scam"

        # 8. Respect ML Model if it predicted a specific scam category
        if ml_cat and ml_cat not in ["legitimate", "ham"]:
            return ml_cat

        return "legitimate"

    def scan_message(self, text: str, lang: Optional[str] = None) -> Dict[str, Any]:
        """Scans a single message and returns an end-to-end security verdict with language preferences."""
        if not self.is_ready:
            raise RuntimeError("ScamShield pipeline is not initialized or trained.")

        cleaned_text = text.strip() if text else ""
        if not cleaned_text:
            return {
                "text": text,
                "is_scam": False,
                "label": "ham",
                "risk_score": 0.0,
                "risk_level": "SAFE",
                "category": "legitimate",
                "category_label": "Legitimate",
                "scam_probability": 0.0,
                "summary": "Empty input provided."
            }

        # Predict with model
        binary_label = self.model.predict_binary([cleaned_text])[0]
        prob = float(self.model.predict_proba([cleaned_text])[0])
        ml_category = self.model.predict_category([cleaned_text])[0]

        # Extract structural & heuristic pattern triggers
        patterns = detect_pattern_triggers(cleaned_text)
        urls = extract_urls(cleaned_text)
        phones = extract_phone_numbers(cleaned_text)

        has_strong_scam_pattern = (
            len(patterns.get("urgency_triggers", [])) > 0 or
            len(patterns.get("bait_triggers", [])) > 0 or
            len(patterns.get("credential_triggers", [])) > 0 or
            len(patterns.get("money_triggers", [])) > 0 or
            len(patterns.get("job_triggers", [])) > 0
        )

        # Resolve true typology category
        category = self.resolve_typology_category(cleaned_text, ml_category)

        # Determine scam verdict with hybrid verification
        if category != "legitimate":
            prob = max(prob, 0.85)
            is_scam = True
        else:
            is_scam = (binary_label == "scam") or (prob >= 0.50) or has_strong_scam_pattern
            if not is_scam:
                category = "legitimate"

        # Generate Explainability & Guidance with localized preferences
        explanation = self.explainer.explain(
            text=cleaned_text,
            is_scam=is_scam,
            scam_prob=prob,
            category=category,
            lang=lang
        )

        return {
            "text": text,
            "is_scam": is_scam,
            "label": "scam" if is_scam else "ham",
            "category": category,
            "category_label": explanation.get("category_label", category.replace("_", " ").title()),
            "language": explanation.get("language", "en"),
            "scam_probability": prob,
            "risk_score": explanation["risk_score"],
            "risk_level": explanation["risk_level"],
            "risk_badge": explanation["risk_badge"],
            "tactics_detected": explanation["tactics_detected"],
            "flagged_tokens": explanation["flagged_tokens"],
            "extracted_urls": explanation["extracted_urls"],
            "extracted_phones": explanation["extracted_phones"],
            "safety_advice": explanation["safety_advice"],
            "summary": explanation["summary"]
        }

    def batch_scan(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Batch scans multiple messages efficiently."""
        return [self.scan_message(t) for t in texts]
