# 🛡️ ScamShield AI: Multi-Channel Cyber-Fraud Defense & NLP Benchmark

[![Python](https://img.shields.io/badge/Python-3.10%2B%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**ScamShield AI** is an explainable, multi-channel natural language processing defense platform inspired by Singapore's [ScamShield](https://www.scamshield.gov.sg/) initiative. It protects users across **SMS**, **WhatsApp Notifications**, **Email Phishing**, and **Desktop Clipboard**.

---

## 🌟 Multi-Channel Applications

### 1. 📱 Application 1: WhatsApp Spam & Notification Guardian
* **Real-Time Notification Interceptor**: Parses incoming WhatsApp message payloads (sender name, phone number, direct vs group broadcast).
* **Automated Threat Assessment**: Computes a dynamic 0–100% Risk Score and identifies predatory recruitment schemes, crypto signals, or lottery baits.
* **Push Notification Toast**: Displays native alert banners (`🚨 WHATSAPP INTERCEPT ALERT`).
* **Automated Safety Reply**: Generates a pre-formatted warning reply advising users not to click links or share 2FA OTPs.
* **Webhook Support**: Compatible with Meta WhatsApp Cloud API and Twilio webhooks (`POST /whatsapp/webhook`).

### 2. 📧 Application 2: Email Phishing & Corporate Impersonation Scanner
* **Business Email Compromise (BEC)**: Detects executive impersonation originating from free webmail domains.
* **Domain Mismatch Detection**: Flags deceptive `Reply-To` vs `From` address header discrepancies.
* **Malicious URL Audit**: Evaluates embedded links for direct IP hosting and suspicious TLDs.

### 3. 📋 Application 3: Real-Time Clipboard & Browser Shield
* **Active Clipboard Watcher**: Scans text or links copied from Chrome, WhatsApp Web, or Telegram.
* **Pre-Navigation Interception**: Warns users *before* they paste or open phishing links.

### 4. 🏆 The ScamShield NLP Challenge
* A competitive benchmark evaluating models on:
  * **Task 1**: Binary Scam vs. Ham Classification (Macro F1)
  * **Task 2**: 8-Class Granular Typology Detection (Macro F1)
  * **Task 3**: Probability Calibration (Brier Score)

---

## 📁 Repository Structure

```
scamshield-nlp/
├── CHALLENGE.md                       # Official NLP Challenge guidelines & scoring specification
├── README.md                          # Comprehensive documentation
├── requirements.txt                   # Project dependencies
├── run_app.bat                        # One-click launcher for Streamlit Web App
├── run_api.bat                        # One-click launcher for FastAPI REST Service
├── run_whatsapp_guardian.bat          # One-click launcher for WhatsApp Notification Guardian
├── run_clipboard_guard.bat            # One-click launcher for Clipboard Shield
├── data/
│   ├── dataset_generator.py           # Synthetic dataset generator
│   ├── train.csv                      # Labeled train set (1,100 rows)
│   ├── val.csv                        # Validation set (350 rows)
│   ├── test_ground_truth.csv          # Hidden test set (350 rows)
│   └── test_unlabeled.csv             # Public unlabelled test set (350 rows)
├── src/
│   ├── whatsapp_guardian.py           # Application 1: WhatsApp Notification Guardian
│   ├── email_scanner.py               # Application 2: Email Phishing Scanner
│   ├── clipboard_guard.py             # Application 3: Real-Time Clipboard Shield
│   ├── preprocessor.py                # Regex extraction, homoglyph mapping, URL risk engine
│   ├── feature_extractor.py           # Word + Char TF-IDF with handcrafted dense feature union
│   ├── models.py                      # Dual-Tier ML models (Binary Scam & 8-Class Typology)
│   ├── explainability.py              # XAI engine: tactics detection, risk scores, advice
│   ├── pipeline.py                    # Master production inference pipeline
│   ├── api.py                         # Multi-channel FastAPI REST application
│   └── app.py                         # Streamlit interactive UI & challenge hub
├── challenge/
│   ├── baseline_submission.py         # Participant starter kit generating submission.csv
│   ├── evaluate_submission.py         # Automated evaluation & scoring engine
│   ├── sample_submission.csv          # Submission format template
│   └── submission.csv                 # Generated baseline submission
├── models/
│   └── scamshield_model.joblib        # Pre-trained production model artifact
└── tests/
    └── test_scamshield.py             # Unit test suite (9 tests passing)
```

---

## ⚡ Quickstart

### 1. Launch the Multi-Channel Dashboard
```bash
python -m streamlit run src/app.py
```
Open **[http://localhost:8501](http://localhost:8501)** to access all interactive tools.

### 2. Run the WhatsApp Notification Guardian
```bash
python src/whatsapp_guardian.py
```

### 3. Run the Clipboard Phishing Shield
```bash
python src/clipboard_guard.py
```

### 4. Run the Full Unit Test Suite
```bash
python tests/test_scamshield.py
```
*(All 11 unit tests passing)*

---

## 🚀 Publishing & Deployment Guide

### Option 1: Deploy Live Web App Free (Streamlit Cloud)
1. Push this repository to your GitHub account (`https://github.com/<your-username>/scamshield-ai`).
2. Visit **[share.streamlit.io](https://share.streamlit.io/)** and log in with GitHub.
3. Click **New app**, select your repository, branch `main`, and main file path `src/app.py`.
4. Click **Deploy!** — your dashboard will be live on a public URL accessible worldwide.

### Option 2: Deploy with Docker & Docker Compose
Run both the FastAPI backend and Streamlit frontend in an isolated container:
```bash
docker-compose up --build -d
```
- Dashboard: `http://localhost:8501`
- REST API: `http://localhost:8000/docs`

### Option 3: Academic Publication (IEEE Proceedings)
- Your publication-ready manuscript is compiled at:
  👉 **`ScamShield_IEEE_Research_Paper.docx`**
- Follow [`IEEE_PAPER_SUBMISSION_INSTRUCTIONS.md`](IEEE_PAPER_SUBMISSION_INSTRUCTIONS.md) to insert your author names, university affiliations, and submit to IEEE conferences or upload to arXiv as a preprint under `cs.CR` / `cs.CL`.
