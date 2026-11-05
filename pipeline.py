"""
ScamShield Master Pipeline
Integrates preprocessing, feature extraction, ML classification, and explainability
into an easy-to-use production inference pipeline.
"""

import os
import pandas as pd
from typing import Dict, List, Any

from src.models import ScamShieldModel
from src.explainability import ScamExplainer

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

    def scan_message(self, text: str) -> Dict[str, Any]:
        """Scans a single message and returns an end-to-end security verdict."""
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
                "scam_probability": 0.0,
                "summary": "Empty input provided."
            }

        # Predict with model
        binary_label = self.model.predict_binary([cleaned_text])[0]
        prob = float(self.model.predict_proba([cleaned_text])[0])
        category = self.model.predict_category([cleaned_text])[0]

        is_scam = (binary_label == "scam")

        # If binary classifier says ham, category is legitimate
        if not is_scam and category != "legitimate" and prob < 0.40:
            category = "legitimate"

        # Generate Explainability & Guidance
        explanation = self.explainer.explain(
            text=cleaned_text,
            is_scam=is_scam,
            scam_prob=prob,
            category=category
        )

        return {
            "text": text,
            "is_scam": is_scam,
            "label": "scam" if is_scam else "ham",
            "category": category,
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
