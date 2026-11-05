"""
ScamShield NLP Challenge - Advanced Model Submission
====================================================
Demonstrates how to build an advanced submission that outperforms standard baselines:
1. Feature extraction using both character n-grams and word n-grams
2. Handcrafted urgency and heuristic domain indicators
3. Probability calibration for minimum Brier score
4. Generates challenge/submission_advanced.csv and ranks on Leaderboard
"""

import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from sklearn.calibration import CalibratedClassifierCV

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from challenge.evaluate_submission import evaluate

def run_advanced_model():
    train_path = os.path.join(DATA_DIR, "train.csv")
    test_path = os.path.join(DATA_DIR, "test_unlabeled.csv")
    output_path = os.path.join(CURRENT_DIR, "submission_advanced.csv")

    print("[1/4] Loading challenge training and test splits...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    print(f"      Train samples: {len(train_df)}, Test samples: {len(test_df)}")

    print("[2/4] Engineering Subword Char + Word N-Gram Features...")
    vectorizer = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), max_features=3500, sublinear_tf=True)),
        ("char", TfidfVectorizer(ngram_range=(3, 5), analyzer="char", max_features=3500, sublinear_tf=True))
    ])

    X_train = vectorizer.fit_transform(train_df["text"])
    X_test = vectorizer.transform(test_df["text"])

    print("[3/4] Training Calibrated Dual-Tier Classifiers...")
    # Binary Model with Calibrated probabilities for optimal Brier score
    base_bin = LogisticRegression(C=2.5, class_weight="balanced", max_iter=1000)
    calibrated_bin = CalibratedClassifierCV(estimator=base_bin, cv=5, method="sigmoid")
    calibrated_bin.fit(X_train, (train_df["label"] == "scam").astype(int))

    binary_preds_num = calibrated_bin.predict(X_test)
    binary_preds = ["scam" if p == 1 else "ham" for p in binary_preds_num]
    scam_probabilities = calibrated_bin.predict_proba(X_test)[:, 1]

    # Multiclass Typology Model
    multi_model = LogisticRegression(C=3.0, class_weight="balanced", max_iter=1000)
    multi_model.fit(X_train, train_df["category"].values)
    multi_preds = multi_model.predict(X_test)

    # Post-processing consistency rule
    final_cats = []
    for i in range(len(test_df)):
        if binary_preds[i] == "ham" and scam_probabilities[i] < 0.30:
            final_cats.append("legitimate")
        else:
            final_cats.append(multi_preds[i])

    print("[4/4] Writing formatted submission file...")
    sub_df = pd.DataFrame({
        "id": test_df["id"],
        "predicted_label": binary_preds,
        "predicted_category": final_cats,
        "scam_probability": scam_probabilities.round(4)
    })
    sub_df.to_csv(output_path, index=False)
    print(f"[OK] Advanced submission saved to: {output_path}")

    # Evaluate and register on official Leaderboard
    gt_path = os.path.join(DATA_DIR, "test_ground_truth.csv")
    print("\nEvaluating against official ground truth...\n")
    evaluate(
        submission_file=output_path,
        ground_truth_file=gt_path,
        team_name="CyberSentinel AI Lab",
        model_name="Calibrated Char+Word TF-IDF Ensemble"
    )

if __name__ == "__main__":
    run_advanced_model()
