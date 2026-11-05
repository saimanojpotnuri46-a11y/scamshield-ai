"""
ScamShield NLP Challenge - Baseline Starter Kit
===============================================
This script provides an end-to-end baseline for participants:
1. Loads train.csv and test_unlabeled.csv
2. Trains a TF-IDF + Logistic Regression model
3. Generates the official format submission.csv
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

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

def run_baseline():
    train_path = os.path.join(DATA_DIR, "train.csv")
    test_path = os.path.join(DATA_DIR, "test_unlabeled.csv")
    output_path = os.path.join(CURRENT_DIR, "submission.csv")

    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print("Error: Train or test dataset not found in data/ directory.")
        return

    print("1. Loading datasets...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    print(f"   Train samples: {len(train_df)}, Test samples: {len(test_df)}")

    # 2. Build NLP vectorizer
    print("2. Building NLP TF-IDF Pipeline...")
    vectorizer = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=3000, sublinear_tf=True)),
        ("char_tfidf", TfidfVectorizer(ngram_range=(3, 5), analyzer="char", max_features=3000, sublinear_tf=True))
    ])

    X_train = vectorizer.fit_transform(train_df["text"])
    X_test = vectorizer.transform(test_df["text"])

    # 3. Train Task 1: Binary Scam Classifier (Ham vs Scam)
    print("3. Training Binary Classifier (Ham vs Scam)...")
    y_train_binary = train_df["label"].values
    binary_model = LogisticRegression(C=1.5, class_weight="balanced", max_iter=1000)
    binary_model.fit(X_train, y_train_binary)

    binary_preds = binary_model.predict(X_test)
    binary_probs = binary_model.predict_proba(X_test)
    scam_prob_idx = list(binary_model.classes_).index("scam")
    scam_probs = binary_probs[:, scam_prob_idx]

    # 4. Train Task 2: Multiclass Typology Classifier
    print("4. Training Multiclass Classifier (Scam Typologies)...")
    y_train_cat = train_df["category"].values
    cat_model = LogisticRegression(C=2.0, class_weight="balanced", max_iter=1000)
    cat_model.fit(X_train, y_train_cat)

    cat_preds = cat_model.predict(X_test)

    # 5. Build official submission DataFrame
    submission_df = pd.DataFrame({
        "id": test_df["id"],
        "predicted_label": binary_preds,
        "predicted_category": cat_preds,
        "scam_probability": scam_probs.round(4)
    })

    # Rule refinement: If binary model says ham and scam_probability < 0.35, category should be legitimate
    for idx in range(len(submission_df)):
        if submission_df.at[idx, "predicted_label"] == "ham" and submission_df.at[idx, "scam_probability"] < 0.35:
            submission_df.at[idx, "predicted_category"] = "legitimate"

    submission_df.to_csv(output_path, index=False)
    print(f"\n[OK] Baseline submission generated successfully at: {output_path}")
    print(f"   Rows: {len(submission_df)}")
    print(submission_df.head())

if __name__ == "__main__":
    run_baseline()
