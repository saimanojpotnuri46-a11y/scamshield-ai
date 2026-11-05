# 🛡️ ScamShield NLP Challenge: Fighting Cyber-Fraud with AI

Welcome to the **ScamShield NLP Challenge**, an open competitive benchmark and machine learning challenge inspired by anti-scam defense systems (such as Singapore's ScamShield initiative). 

The goal of this challenge is to build automated natural language processing models capable of detecting smishing (SMS phishing), social engineering manipulation, and classifying deceptive messages into granular fraud typologies.

---

## 📌 Problem Statement

Every year, billions of dollars are lost globally to deceptive telecommunications fraud. Fraudsters use psychological triggers (fear, artificial urgency, greed, authority coercion), obfuscated domains (lookalike brands, IP addresses, sketchy TLDs), and leetspeak variations to bypass conventional keyword filters.

Participants in this challenge are tasked with creating robust NLP systems that can:
1. Distinguish between genuine user communications and malicious attempts (**Binary Classification**).
2. Categorize the malicious attempt into its tactical typology (**Multi-Class Classification**).
3. Provide a well-calibrated scam probability score (**Probability Calibration**).

---

## 🎯 Challenge Tasks

### Task 1: Binary Scam vs Ham Classification
- **Objective:** Predict whether an incoming message is `ham` (legitimate communication) or `scam` (fraudulent / phishing).
- **Target Column:** `predicted_label` (`"ham"` or `"scam"`).
- **Primary Metric:** Macro F1-Score.

### Task 2: Granular Scam Typology Detection
- **Objective:** Classify each message into one of 8 standardized threat typologies:
  1. `legitimate` — Genuine OTPs, medical appointments, friend SMS, standard receipts.
  2. `bank_impersonation` — Fake DBS/OCBC/Chase warnings, token expired, account locked.
  3. `delivery_fraud` — SingPost/DHL/FedEx unpaid customs fee, invalid delivery address.
  4. `job_scam` — YouTube video like tasks, easy daily cash, WhatsApp recruitment.
  5. `investment_crypto` — Guaranteed 500% ROI, AI trading bot, celebrity giveaways.
  6. `lottery_reward` — Uncollected government grant, grocery vouchers, lucky draw winner.
  7. `government_police` — Arrest warrant, tax evasion penalty (IRAS), court subpoena.
  8. `tech_support` — Windows Defender Trojan virus alert, Apple ID suspended.
- **Target Column:** `predicted_category`.
- **Primary Metric:** Macro F1-Score across all 8 classes.

### Task 3: Probability Calibration & Severity
- **Objective:** Output a continuous confidence probability $P(\text{scam}) \in [0.0, 1.0]$.
- **Target Column:** `scam_probability`.
- **Primary Metric:** Brier Score (Mean Squared Error between predicted probability and true binary label). Lower is better.

---

## 📊 Dataset Structure

All benchmark datasets are located in the [`data/`](./data/) directory:

| Split | File | Size | Description |
|---|---|---|---|
| **Train** | [`data/train.csv`](./data/train.csv) | 1,100 rows | Labeled dataset with text, labels, and metadata |
| **Validation** | [`data/val.csv`](./data/val.csv) | 350 rows | Validation split for hyperparameter tuning |
| **Test (Hidden)** | [`data/test_ground_truth.csv`](./data/test_ground_truth.csv) | 350 rows | Ground truth used by the automated evaluator |
| **Test (Public)** | [`data/test_unlabeled.csv`](./data/test_unlabeled.csv) | 350 rows | Unlabeled test set (`id`, `text`) for participants |

### Columns in `train.csv`:
- `id` — Unique message identifier (e.g. `MSG_00001`)
- `text` — Raw message text (SMS, WhatsApp, notification)
- `label` — `"ham"` or `"scam"`
- `category` — Typology name (e.g. `bank_impersonation`)
- `urgency_level` — Heuristic urgency level (`low`, `medium`, `high`, `critical`)
- `contains_url` — Binary indicator ($0$ or $1$)
- `contains_phone` — Binary indicator ($0$ or $1$)

---

## 📥 Submission Format

Submissions must be exported as a CSV file matching the format in [`challenge/sample_submission.csv`](./challenge/sample_submission.csv):

```csv
id,predicted_label,predicted_category,scam_probability
MSG_01451,scam,investment_crypto,0.9641
MSG_01452,scam,bank_impersonation,0.9766
MSG_01453,scam,lottery_reward,0.9532
MSG_01454,scam,government_police,0.9565
MSG_01455,ham,legitimate,0.0215
```

### Constraints:
- Exactly 350 rows corresponding to `test_unlabeled.csv`.
- No `NaN` or `null` values.
- `scam_probability` bounded within $[0.0, 1.0]$.

---

## 🏆 Official Scoring Formula

The final **Leaderboard Composite Score** (0 to 100) is calculated as:

$$\text{Composite Score} = \Big(0.40 \times \text{F1}_{\text{binary}} + 0.35 \times \text{F1}_{\text{multiclass}} + 0.15 \times \text{Acc}_{\text{binary}} + 0.10 \times (1 - \text{Brier Score})\Big) \times 100$$

---

## 🚀 Starter Kit & Quickstart

### 1. Run the Baseline Model
Generate your first baseline submission with one command:
```bash
python challenge/baseline_submission.py
```
This trains a baseline TF-IDF + Logistic Regression model and generates `challenge/submission.csv`.

### 2. Evaluate Your Submission
Run the official evaluation script to see your score:
```bash
python challenge/evaluate_submission.py --submission challenge/submission.csv
```

### 3. Interactive Web Leaderboard
Launch the Streamlit app and head to the **NLP Challenge** tab to upload and evaluate models interactively:
```bash
streamlit run src/app.py
```

---

## 💡 Recommended Modeling Approaches

Participants are encouraged to experiment with:
1. **Transformer Ensembles**: Fine-tuning DeBERTa-v3, RoBERTa, or ModernBERT on the training set.
2. **Hybrid Feature Fusion**: Combining dense transformer embeddings with lexical regex signals (suspicious TLDs, IP detection, urgency phrases).
3. **Few-Shot LLM Reasoning**: Leveraging Gemma 2 / Llama 3 via Chain-of-Thought prompting to classify and extract manipulative intents.
4. **Adversarial Robustness**: Testing resilience against homoglyphs (`@cc0unt`, `cl1ck`) and URL shorteners.
