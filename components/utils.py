import json
from pathlib import Path
from datetime import datetime
import streamlit as st

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def _path(name: str) -> Path:
    return DATA_DIR / name

def load_json(name: str, default):
    p = _path(name)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(name: str, data):
    _path(name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def text_badge(label: str, value: str):
    st.markdown(f"<span style='font-size:0.9rem;opacity:.7'>{label}</span><br><b>{value}</b>", unsafe_allow_html=True)

def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def try_gemini():
    # 任意：GEMINI_API_KEY があるときだけ読み込む
    if "GEMINI_API_KEY" in st.secrets:
        try:
            import google.generativeai as genai
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
        except Exception:
            return None
    return None
