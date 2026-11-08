"""
ScamShield AI - Streamlit Community Cloud Root Launcher & Engine Hub
====================================================================
Self-healing, auto-synchronizing production launcher that guarantees:
1. Complete removal of Chinese (zh) and prominent promotion of Telugu (te)
2. Accurate 8-class scam typology resolution (bank, delivery, police, crypto,
   tech support, lottery, job scam, and legitimate)
3. Safe cross-platform zip extraction with force-overwrite
4. Pre-registered sys.modules so 'src.localization' NEVER throws ModuleNotFoundError
5. Hot-patching of ScamShieldPipeline at runtime so even legacy repositories
   immediately classify all categories separately and accurately
"""

import os
import sys
import shutil
import zipfile
import types
import re
import json

# Setup base directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

src_dir = os.path.join(ROOT_DIR, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 1. Linux Backslash Sanitizer (fixes Windows zip paths on Linux)
try:
    for fname in os.listdir(ROOT_DIR):
        if "\\" in fname:
            bad_path = os.path.join(ROOT_DIR, fname)
            clean_subpath = fname.replace("\\", "/")
            good_path = os.path.join(ROOT_DIR, clean_subpath)
            os.makedirs(os.path.dirname(good_path), exist_ok=True)
            try:
                shutil.copy2(bad_path, good_path)
                os.remove(bad_path)
            except Exception:
                pass
except Exception:
    pass

# 2. Force-Overwrite Zip Package Extractor
for item in os.listdir(ROOT_DIR):
    if item.endswith(".zip"):
        zip_path = os.path.join(ROOT_DIR, item)
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                for member in z.infolist():
                    norm_name = member.filename.replace("\\", "/")
                    if not norm_name or norm_name.endswith("/"):
                        continue
                    target_file = os.path.join(ROOT_DIR, norm_name)
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    with z.open(member) as src_f, open(target_file, "wb") as dst_f:
                        shutil.copyfileobj(src_f, dst_f)
            print(f"[ScamShield Launcher] Auto-extracted package with overwrite: {item}")
        except Exception as e:
            print(f"[ScamShield Launcher] Zip extraction notice for {item}: {e}")

# 3. Ensure src/ directory exists & populate with __init__.py
os.makedirs(src_dir, exist_ok=True)
init_src = os.path.join(src_dir, "__init__.py")
if not os.path.exists(init_src):
    try:
        with open(init_src, "w", encoding="utf-8") as f:
            f.write("# ScamShield Package\n")
    except Exception:
        pass

# 4. Bidirectional Sync between root and src/ (Indentation-Safe Function)
def _sync_folders(s_dir, d_dir, exclude_names):
    if os.path.exists(s_dir) and os.path.exists(d_dir):
        for f in os.listdir(s_dir):
            if f.endswith(".py") and f not in exclude_names:
                sp = os.path.join(s_dir, f)
                dp = os.path.join(d_dir, f)
                if os.path.isfile(sp) and not os.path.exists(dp):
                    try:
                        shutil.copy2(sp, dp)
                    except Exception:
                        pass

_sync_folders(ROOT_DIR, src_dir, ["streamlit_app.py"])
_sync_folders(src_dir, ROOT_DIR, ["__init__.py"])

# 5. Helper to locate model & data folders
def _resolve_dir(dirname: str) -> str:
    candidates = [
        os.path.join(ROOT_DIR, dirname),
        os.path.join(src_dir, dirname),
        os.path.join(os.path.dirname(ROOT_DIR), dirname),
        os.path.join(os.getcwd(), dirname)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    fallback = os.path.join(ROOT_DIR, dirname)
    os.makedirs(fallback, exist_ok=True)
    return fallback

model_dir = _resolve_
