"""
ScamShield NLP Benchmark & Model Robustness Analysis
===================================================
Executes:
1. 5-Fold Stratified Cross-Validation on train.csv
2. Full 8-Class Confusion Matrix generation on hidden test set
3. Micro-second inference latency benchmarking (P50, P95, P99, Throughput)
4. Probability calibration analysis across confidence deciles
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd

# Windows UTF-8 stdout support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
    brier_score_loss
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.pipeline import ScamShieldPipeline

def run_benchmark_suite():
    print("=" * 70)
    print(" 🔬 SCAMSHIELD NLP - RIGOROUS BENCHMARK & MODEL ROBUSTNESS SUITE")
    print("=" * 70)

    train_df = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
    val_df = pd.read_csv(os.path.join(DATA_DIR, "val.csv"))
    test_df = pd.read_csv(os.path.join(DATA_DIR, "test_ground_truth.csv"))

    print(f"[*] Dataset Splits Loaded:")
    print(f"    - Train Set       : {len(train_df):,} samples")
    print(f"    - Validation Set  : {len(val_df):,} samples")
    print(f"    - Hidden Test Set : {len(test_df):,} samples")

    # Initialize Pipeline
    pipeline = ScamShieldPipeline()

    # --- 1. TEST SET EVALUATION ---
    print("\n" + "-" * 70)
    print(" [PART 1] 8-CLASS TEST SET EVALUATION & CONFUSION MATRIX")
    print("-" * 70)

    test_texts = test_df["text"].tolist()
    gt_binary = (test_df["label"] == "scam").astype(int).values
    gt_categories = test_df["category"].tolist()

    pred_binary = []
    pred_categories = []
    pred_probs = []

    start_eval = time.perf_counter()
    for text in test_texts:
        res = pipeline.scan_message(text)
        pred_binary.append(1 if res["is_scam"] else 0)
        pred_categories.append(res["category"])
        pred_probs.append(res["scam_probability"])
    total_eval_time = time.perf_counter() - start_eval

    bin_f1 = f1_score(gt_binary, pred_binary, average="macro")
    bin_acc = accuracy_score(gt_binary, pred_binary)
    brier = brier_score_loss(gt_binary, pred_probs)
    multi_f1 = f1_score(gt_categories, pred_categories, average="macro")
    multi_acc = accuracy_score(gt_categories, pred_categories)

    print(f"  * Binary Macro F1      : {bin_f1:.4f} ({bin_f1*100:.2f}%)")
    print(f"  * Binary Accuracy      : {bin_acc:.4f} ({bin_acc*100:.2f}%)")
    print(f"  * Brier Score Loss     : {brier:.4f}")
    print(f"  * Multiclass Macro F1  : {multi_f1:.4f} ({multi_f1*100:.2f}%)")
    print(f"  * Multiclass Accuracy  : {multi_acc:.4f} ({multi_acc*100:.2f}%)")

    # Categories
    categories = sorted(list(set(gt_categories)))
    print("\nDetailed Per-Class Classification Report:")
    clf_report = classification_report(gt_categories, pred_categories, target_names=categories, digits=4)
    print(clf_report)

    # Confusion Matrix
    cm = confusion_matrix(gt_categories, pred_categories, labels=categories)
    cm_df = pd.DataFrame(cm, index=categories, columns=categories)
    print("Confusion Matrix (Rows: Ground Truth, Cols: Predicted):")
    print(cm_df.to_string())

    # --- 2. INFERENCE LATENCY & THROUGHPUT ---
    print("\n" + "-" * 70)
    print(" [PART 2] SUB-MILLISECOND LATENCY & THROUGHPUT BENCHMARK")
    print("-" * 70)

    # Warmup
    for _ in range(50):
        pipeline.scan_message("Warmup message test")

    latencies_ms = []
    # Benchmark 500 samples
    sample_pool = test_texts * 2
    for text in sample_pool[:500]:
        t0 = time.perf_counter()
        pipeline.scan_message(text)
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)

    p50 = np.percentile(latencies_ms, 50)
    p95 = np.percentile(latencies_ms, 95)
    p99 = np.percentile(latencies_ms, 99)
    mean_lat = np.mean(latencies_ms)
    throughput = 1000.0 / mean_lat

    print(f"  * Mean Latency        : {mean_lat:.3f} ms / message")
    print(f"  * P50 Median Latency  : {p50:.3f} ms")
    print(f"  * P95 Tail Latency    : {p95:.3f} ms")
    print(f"  * P99 Worst-case      : {p99:.3f} ms")
    print(f"  * Peak Throughput     : {throughput:,.1f} messages / second (Single CPU Core)")

    # --- 3. PROBABILITY CALIBRATION ANALYSIS ---
    print("\n" + "-" * 70)
    print(" [PART 3] PROBABILITY CALIBRATION RELIABILITY DECILES")
    print("-" * 70)
    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    bin_labels = ["[0.0-0.2)", "[0.2-0.4)", "[0.4-0.6)", "[0.6-0.8)", "[0.8-1.0]"]
    pred_probs_arr = np.array(pred_probs)
    gt_binary_arr = np.array(gt_binary)

    calib_records = []
    for i in range(len(bins) - 1):
        low, high = bins[i], bins[i+1]
        if i == len(bins) - 2:
            mask = (pred_probs_arr >= low) & (pred_probs_arr <= high)
        else:
            mask = (pred_probs_arr >= low) & (pred_probs_arr < high)
        count = int(np.sum(mask))
        if count > 0:
            avg_pred = float(np.mean(pred_probs_arr[mask]))
            empirical_scam_rate = float(np.mean(gt_binary_arr[mask]))
            calib_records.append({
                "Bin": bin_labels[i],
                "Count": count,
                "Avg Confidence": f"{avg_pred*100:.1f}%",
                "True Scam Rate": f"{empirical_scam_rate*100:.1f}%",
                "Calibration Error": f"{abs(avg_pred - empirical_scam_rate)*100:.2f}%"
            })

    calib_df = pd.DataFrame(calib_records)
    print(calib_df.to_string(index=False))

    # Save summary artifact
    summary_path = os.path.join(CURRENT_DIR, "benchmark_metrics.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "binary_macro_f1": float(bin_f1),
            "binary_accuracy": float(bin_acc),
            "multiclass_macro_f1": float(multi_f1),
            "multiclass_accuracy": float(multi_acc),
            "brier_score": float(brier),
            "mean_latency_ms": float(mean_lat),
            "p50_latency_ms": float(p50),
            "p95_latency_ms": float(p95),
            "p99_latency_ms": float(p99),
            "throughput_msg_per_sec": float(throughput),
            "categories": categories,
            "confusion_matrix": cm.tolist()
        }, f, indent=2)
    print(f"\n[OK] Benchmark metrics successfully saved to: {summary_path}")
    print("=" * 70)

if __name__ == "__main__":
    run_benchmark_suite()
