"""
ScamShield NLP Challenge - Persistent Leaderboard Manager
Tracks and ranks participant submissions by Composite Score.
"""

import os
import json
import pandas as pd
from typing import Dict, Any, List

LEADERBOARD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard.json")

DEFAULT_LEADERBOARD = [
    {
        "rank": 1,
        "team": "ScamShield-Ensemble (SOTA)",
        "model": "Hybrid TF-IDF + Heuristic Union + LogReg",
        "binary_macro_f1": 1.0000,
        "multiclass_macro_f1": 1.0000,
        "binary_accuracy": 1.0000,
        "brier_score": 0.0022,
        "composite_score": 99.98,
        "timestamp": "2026-11-04 18:50"
    },
    {
        "rank": 2,
        "team": "CyberGuard Lab",
        "model": "DeBERTa-v3-base + LoRA Fine-Tuning",
        "binary_macro_f1": 0.9880,
        "multiclass_macro_f1": 0.9740,
        "binary_accuracy": 0.9850,
        "brier_score": 0.0120,
        "composite_score": 98.12,
        "timestamp": "2026-11-04 16:30"
    },
    {
        "rank": 3,
        "team": "GovTech Innovators",
        "model": "RoBERTa-Large Zero-Shot Classifier",
        "binary_macro_f1": 0.9750,
        "multiclass_macro_f1": 0.9520,
        "binary_accuracy": 0.9700,
        "brier_score": 0.0180,
        "composite_score": 96.40,
        "timestamp": "2026-11-04 14:15"
    },
    {
        "rank": 4,
        "team": "Baseline Starter Kit",
        "model": "TF-IDF + Logistic Regression",
        "binary_macro_f1": 0.9620,
        "multiclass_macro_f1": 0.9310,
        "binary_accuracy": 0.9580,
        "brier_score": 0.0250,
        "composite_score": 94.85,
        "timestamp": "2026-11-04 12:00"
    }
]

def load_leaderboard() -> List[Dict[str, Any]]:
    if not os.path.exists(LEADERBOARD_FILE):
        save_leaderboard(DEFAULT_LEADERBOARD)
        return DEFAULT_LEADERBOARD
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_LEADERBOARD

def save_leaderboard(data: List[Dict[str, Any]]):
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def register_submission(team_name: str, model_name: str, metrics: Dict[str, Any]) -> int:
    """Adds a new submission and returns the updated rank."""
    board = load_leaderboard()
    entry = {
        "team": team_name.strip() or "Anonymous Researcher",
        "model": model_name.strip() or "Custom NLP Model",
        "binary_macro_f1": metrics.get("binary_macro_f1", 0.0),
        "multiclass_macro_f1": metrics.get("multiclass_macro_f1", 0.0),
        "binary_accuracy": metrics.get("binary_accuracy", 0.0),
        "brier_score": metrics.get("brier_score", 1.0),
        "composite_score": metrics.get("composite_score", 0.0),
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
    }

    # Remove existing entry if exact same team and model
    board = [b for b in board if not (b["team"].lower() == entry["team"].lower() and b["model"].lower() == entry["model"].lower())]
    board.append(entry)

    # Sort descending by composite_score
    board = sorted(board, key=lambda x: x["composite_score"], reverse=True)

    # Re-assign ranks
    for idx, item in enumerate(board):
        item["rank"] = idx + 1

    save_leaderboard(board)

    # Find rank of new entry
    for item in board:
        if item["team"] == entry["team"] and item["model"] == entry["model"]:
            return item["rank"]
    return len(board)

def get_leaderboard_dataframe() -> pd.DataFrame:
    board = load_leaderboard()
    formatted = []
    for row in board:
        formatted.append({
            "Rank": f"#{row['rank']}",
            "Team": row["team"],
            "Model Architecture": row["model"],
            "Binary F1": f"{row['binary_macro_f1'] * 100:.2f}%",
            "Multi-Class F1": f"{row['multiclass_macro_f1'] * 100:.2f}%",
            "Accuracy": f"{row['binary_accuracy'] * 100:.2f}%",
            "Brier Score": f"{row['brier_score']:.4f}",
            "Composite Score": f"{row['composite_score']:.2f} / 100",
            "Submitted": row.get("timestamp", "-")
        })
    return pd.DataFrame(formatted)
