"""
ScamShield NLP Challenge - Official Evaluation Engine
=====================================================
Scores participant submissions against the ground truth test set.
Computes Task 1 (Binary F1), Task 2 (Multiclass F1), Calibration (Brier Score),
and the final Composite Leaderboard Score. Registers score to leaderboard.
"""

import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import argparse
import numpy as np
import pandas as pd
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
    brier_score_loss,
    classification_report
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DEFAULT_GROUND_TRUTH = os.path.join(PROJECT_ROOT, "data", "test_ground_truth.csv")
DEFAULT_SUBMISSION = os.path.join(CURRENT_DIR, "submission.csv")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from challenge.leaderboard import register_submission, get_leaderboard_dataframe

def evaluate(
    submission_file: str,
    ground_truth_file: str = DEFAULT_GROUND_TRUTH,
    team_name: str = "Anonymous Participant",
    model_name: str = "Custom NLP Model"
):
    if not os.path.exists(submission_file):
        raise FileNotFoundError(f"Submission file not found: {submission_file}")
    if not os.path.exists(ground_truth_file):
        raise FileNotFoundError(f"Ground truth file not found: {ground_truth_file}")

    sub_df = pd.read_csv(submission_file)
    gt_df = pd.read_csv(ground_truth_file)

    # 1. Validation Checks
    required_cols = ["id", "predicted_label", "predicted_category", "scam_probability"]
    for col in required_cols:
        if col not in sub_df.columns:
            raise ValueError(f"Missing required column in submission: '{col}'. Expected: {required_cols}")

    if len(sub_df) != len(gt_df):
        raise ValueError(f"Row count mismatch: Submission has {len(sub_df)} rows, ground truth has {len(gt_df)} rows.")

    merged = pd.merge(gt_df, sub_df, on="id", suffixes=("_gt", "_sub"))
    if len(merged) != len(gt_df):
        raise ValueError("ID mismatch: Some 'id' entries in submission do not match the ground truth test IDs.")

    # 2. Task 1: Binary Classification (Ham vs Scam)
    y_true_binary = (merged["label"] == "scam").astype(int).values
    y_pred_binary = (merged["predicted_label"] == "scam").astype(int).values
    y_prob_scam = merged["scam_probability"].clip(0.0, 1.0).values

    bin_f1 = f1_score(y_true_binary, y_pred_binary, average="macro")
    bin_acc = accuracy_score(y_true_binary, y_pred_binary)
    bin_prec = precision_score(y_true_binary, y_pred_binary, zero_division=0)
    bin_rec = recall_score(y_true_binary, y_pred_binary, zero_division=0)

    # 3. Task 2: Multiclass Category Classification
    y_true_cat = merged["category"].values
    y_pred_cat = merged["predicted_category"].values

    multi_f1 = f1_score(y_true_cat, y_pred_cat, average="macro")
    multi_acc = accuracy_score(y_true_cat, y_pred_cat)

    # 4. Calibration: Brier Score (lower is better, max 1.0)
    brier = brier_score_loss(y_true_binary, y_prob_scam)
    calib_score = max(0.0, 1.0 - brier)

    # 5. Composite Benchmark Score (0 - 100)
    # 40% Binary F1, 35% Multiclass F1, 15% Binary Acc, 10% Calibration
    composite = (
        0.40 * bin_f1 +
        0.35 * multi_f1 +
        0.15 * bin_acc +
        0.10 * calib_score
    ) * 100.0

    metrics = {
        "binary_macro_f1": round(float(bin_f1), 4),
        "binary_accuracy": round(float(bin_acc), 4),
        "binary_precision": round(float(bin_prec), 4),
        "binary_recall": round(float(bin_rec), 4),
        "multiclass_macro_f1": round(float(multi_f1), 4),
        "multiclass_accuracy": round(float(multi_acc), 4),
        "brier_score": round(float(brier), 4),
        "composite_score": round(float(composite), 2),
        "sample_count": len(merged)
    }

    # Register on Leaderboard
    rank = register_submission(team_name, model_name, metrics)

    print("=" * 65)
    print(" [SCAMSHIELD] NLP CHALLENGE - OFFICIAL EVALUATION REPORT")
    print("=" * 65)
    print(f"Team / Submitter             : {team_name}")
    print(f"Model Architecture           : {model_name}")
    print(f"Total Test Samples Evaluated : {len(merged)}")
    print("-" * 65)
    print("TASK 1: BINARY SCAM DETECTION (Ham vs Scam)")
    print(f"  * Macro F1-Score            : {bin_f1:.4f}  ({bin_f1*100:.2f}%)")
    print(f"  * Accuracy                  : {bin_acc:.4f}  ({bin_acc*100:.2f}%)")
    print(f"  * Precision (Scam)          : {bin_prec:.4f}")
    print(f"  * Recall (Scam)             : {bin_rec:.4f}")
    print("-" * 65)
    print("TASK 2: MULTI-CLASS TYPOLOGY DETECTION (8 Categories)")
    print(f"  * Multiclass Macro F1       : {multi_f1:.4f}  ({multi_f1*100:.2f}%)")
    print(f"  * Multiclass Accuracy       : {multi_acc:.4f}  ({multi_acc*100:.2f}%)")
    print("-" * 65)
    print("TASK 3: PROBABILITY CALIBRATION")
    print(f"  * Brier Score (lower=better): {brier:.4f}")
    print(f"  * Calibration Quality Score : {calib_score:.4f}")
    print("=" * 65)
    print(f"[FINAL] COMPOSITE SCORE     : {composite:.2f} / 100.00")
    print(f"[RANK]  LEADERBOARD POSITION : #{rank}")
    print("=" * 65)

    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate ScamShield NLP Challenge Submission")
    parser.add_argument("--submission", default=DEFAULT_SUBMISSION, help="Path to submission.csv")
    parser.add_argument("--ground-truth", default=DEFAULT_GROUND_TRUTH, help="Path to test_ground_truth.csv")
    parser.add_argument("--team", default="My Research Team", help="Your Team Name")
    parser.add_argument("--model", default="Baseline TF-IDF + LogReg", help="Your Model Description")
    args = parser.parse_args()

    evaluate(args.submission, args.ground_truth, args.team, args.model)
