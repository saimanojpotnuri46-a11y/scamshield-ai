"""
ScamShield Machine Learning Models
Contains binary scam detection (Ham vs Scam) and multi-class typology classification.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, accuracy_score

from src.feature_extractor import ScamShieldFeatureExtractor

class ScamShieldModel:
    def __init__(self):
        self.feature_extractor = ScamShieldFeatureExtractor()
        # Binary Classifier: Logistic Regression with balanced class weighting
        self.binary_clf = LogisticRegression(
            C=1.5,
            class_weight="balanced",
            max_iter=1000,
            solver="lbfgs",
            random_state=42
        )
        # Multiclass Classifier for Scam Typologies
        self.multiclass_clf = LogisticRegression(
            C=2.0,
            class_weight="balanced",
            max_iter=1000,
            solver="lbfgs",
            random_state=42
        )
        self.is_trained = False
        self.classes_binary = None
        self.classes_multiclass = None

    def fit(self, train_df: pd.DataFrame, val_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Trains both binary and multi-class models on training DataFrame.
        Expected columns: 'text', 'label' ('ham'/'scam'), 'category'.
        """
        texts = train_df["text"].tolist()
        y_binary = (train_df["label"] == "scam").astype(int).values
        y_multi = train_df["category"].values

        print(f"Extracting features from {len(texts)} samples...")
        X = self.feature_extractor.fit_transform(texts)

        print("Fitting Binary Scam Classifier...")
        self.binary_clf.fit(X, y_binary)
        self.classes_binary = np.array(["ham", "scam"])

        print("Fitting Multiclass Typology Classifier...")
        self.multiclass_clf.fit(X, y_multi)
        self.classes_multiclass = self.multiclass_clf.classes_

        self.is_trained = True

        metrics = {}
        if val_df is not None:
            metrics = self.evaluate(val_df)
        return metrics

    def predict_binary(self, texts: List[str]) -> List[str]:
        """Returns 'ham' or 'scam' for each text."""
        if not self.is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        X = self.feature_extractor.transform(texts)
        preds = self.binary_clf.predict(X)
        return ["scam" if p == 1 else "ham" for p in preds]

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Returns scam probability (float between 0.0 and 1.0) for each text."""
        if not self.is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        X = self.feature_extractor.transform(texts)
        # binary_clf predict_proba returns [P(ham), P(scam)]
        probas = self.binary_clf.predict_proba(X)
        return probas[:, 1]

    def predict_category(self, texts: List[str]) -> List[str]:
        """Predicts specific typology category for each text."""
        if not self.is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        X = self.feature_extractor.transform(texts)
        return self.multiclass_clf.predict(X).tolist()

    def predict_category_proba(self, texts: List[str]) -> List[Dict[str, float]]:
        """Returns category probabilities dictionary for each text."""
        if not self.is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        X = self.feature_extractor.transform(texts)
        probs = self.multiclass_clf.predict_proba(X)
        results = []
        for row in probs:
            cat_prob_map = {cls: float(row[i]) for i, cls in enumerate(self.classes_multiclass)}
            results.append(cat_prob_map)
        return results

    def evaluate(self, val_df: pd.DataFrame) -> Dict[str, Any]:
        """Evaluates model performance against validation/test dataset."""
        texts = val_df["text"].tolist()
        y_true_binary = (val_df["label"] == "scam").astype(int).values
        y_true_multi = val_df["category"].values

        binary_preds = [1 if p == "scam" else 0 for p in self.predict_binary(texts)]
        multi_preds = self.predict_category(texts)
        scam_probs = self.predict_proba(texts)

        bin_f1 = f1_score(y_true_binary, binary_preds, average="macro")
        bin_prec = precision_score(y_true_binary, binary_preds, zero_division=0)
        bin_rec = recall_score(y_true_binary, binary_preds, zero_division=0)
        bin_acc = accuracy_score(y_true_binary, binary_preds)

        multi_f1 = f1_score(y_true_multi, multi_preds, average="macro")
        multi_acc = accuracy_score(y_true_multi, multi_preds)

        return {
            "binary_macro_f1": float(bin_f1),
            "binary_precision": float(bin_prec),
            "binary_recall": float(bin_rec),
            "binary_accuracy": float(bin_acc),
            "multiclass_macro_f1": float(multi_f1),
            "multiclass_accuracy": float(multi_acc),
            "sample_count": len(val_df)
        }

    def save(self, model_dir: str):
        """Saves feature extractor and trained models to directory."""
        os.makedirs(model_dir, exist_ok=True)
        dump_data = {
            "feature_extractor": self.feature_extractor,
            "binary_clf": self.binary_clf,
            "multiclass_clf": self.multiclass_clf,
            "classes_binary": self.classes_binary,
            "classes_multiclass": self.classes_multiclass,
            "is_trained": self.is_trained
        }
        path = os.path.join(model_dir, "scamshield_model.joblib")
        joblib.dump(dump_data, path)
        print(f"Model saved successfully to {path}")

    @classmethod
    def load(cls, model_dir: str) -> "ScamShieldModel":
        """Loads model from directory."""
        path = os.path.join(model_dir, "scamshield_model.joblib")
        if not os.path.exists(path):
            raise FileNotFoundError(f"No saved model found at {path}")
        data = joblib.load(path)
        instance = cls()
        instance.feature_extractor = data["feature_extractor"]
        instance.binary_clf = data["binary_clf"]
        instance.multiclass_clf = data["multiclass_clf"]
        instance.classes_binary = data["classes_binary"]
        instance.classes_multiclass = data["classes_multiclass"]
        instance.is_trained = data["is_trained"]
        return instance
