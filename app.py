import streamlit as st
import requests
import json
import base64
import socket

# ================= CONFIG =================

API_KEY = st.secrets.get("API_KEY", "ddc-a4f-5d489223ebb84c0387b2c7e3cb01a751")
BASE_URL = st.secrets.get("BASE_URL", "https://api.a4f.ai/v1/chat/completions")

REASONING_MODEL = "provider-3/gpt-5.1-chat"
IMAGE_MODEL = "provider-3/gemini-2.5-flash-image-preview-edit"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ================= UI =================

st.set_page_config(page_title="Interior AI", layout="wide")
st.title("🏠 Interior Design AI")

# ================= NETWORK CHECK =================

def check_dns(host):
    try:
        socket.gethostbyname(host)
        return True
    except:
        return False

host = BASE_URL.replace("https://", "").split("/")[0]

if not check_dns(host):
    st.error(f"""
❌ **Endpoint not reachable**

Host: `{host}`

This is NOT a Streamlit issue  
This is NOT a Python issue  

👉 The API endpoint is not publicly resolvable.
""")
    st.stop()

# ================= APP =================

prompt = st.text_area("Interior design prompt")
run = st.button("Run")

if run:
    payload = {
        "model": REASONING_MODEL,
        "messages": [
            {"role": "system", "content": "Interior design only. JSON only."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        res = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=30)
        st.write(res.json())
    except Exception as e:
        st.error(f"Request failed: {e}")

