"""
ScamShield AI - Streamlit Community Cloud Root Launcher
======================================================
Entry point configured for automatic discovery on Streamlit Community Cloud.
"""

import os
import sys

# Ensure project root is in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Execute main application script
APP_PATH = os.path.join(ROOT_DIR, "src", "app.py")
with open(APP_PATH, "r", encoding="utf-8") as f:
    code = f.read()

exec(compile(code, APP_PATH, "exec"), globals())
