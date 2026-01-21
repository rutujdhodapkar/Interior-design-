import streamlit as st
import requests
import json
import base64
import os

# ================= CONFIG =================

API_KEY = "ddc-a4f-5d489223ebb84c0387b2c7e3cb01a751"
BASE_URL = "https://api.a4f.ai/v1/chat/completions"

REASONING_MODEL = "provider-3/gpt-5.1-chat"
IMAGE_MODEL = "provider-3/gemini-2.5-flash-image-preview-edit"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ================= UI =================

st.set_page_config(page_title="Interior AI", layout="wide")
st.title("🏠 Interior Design AI System")

st.caption("Reasoning → JSON → Interior Images (Strict Interior Tasks Only)")

user_prompt = st.text_area("Enter your interior design prompt")

uploaded_image = st.file_uploader(
    "Optional: Upload room/house image",
    type=["png", "jpg", "jpeg"]
)

generate_btn = st.button("Generate")

# ================= HELPERS =================

def safe_post(payload):
    try:
        return requests.post(
            BASE_URL,
            headers=HEADERS,
            json=payload,
            timeout=40
        )
    except requests.exceptions.RequestException as e:
        st.error("❌ Network / DNS error. Deployment environment required.")
        st.stop()

# ================= REASONING =================

SYSTEM_PROMPT = """
You are an interior-design reasoning engine.

RULES:
- ONLY handle interior design tasks.
- If task is NOT interior related, respond EXACTLY:
  {"error":"INVALID_TASK"}

- Output ONLY valid JSON.
- Include:
  house -> floors -> rooms
  room dimensions
  room type
  furniture placement

- If user asks for a specific room, generate ONLY that room.
"""

def run_reasoning(prompt):
    payload = {
        "model": REASONING_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    res = safe_post(payload)

    if res.status_code != 200:
        st.error(res.text)
        st.stop()

    content = res.json()["choices"][0]["message"]["content"]

    if "INVALID_TASK" in content:
        return None

    return json.loads(content)

# ================= IMAGE GEN =================

def generate_image(prompt, image_bytes=None):
    messages = []

    if image_bytes:
        img_b64 = base64.b64encode(image_bytes).decode()
        messages.append({
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_base64": img_b64}
            ]
        })
    else:
        messages.append({"role": "user", "content": prompt})

    payload = {
        "model": IMAGE_MODEL,
        "messages": messages
    }

    res = safe_post(payload)

    if res.status_code != 200:
        st.error(res.text)
        st.stop()

    return base64.b64decode(
        res.json()["choices"][0]["message"]["content"][0]["image_base64"]
    )

# ================= MAIN FLOW =================

if generate_btn:
    if not user_prompt.strip():
        st.warning("Enter a prompt")
        st.stop()

    # CASE 1: IMAGE UPLOADED → DIRECT IMAGE MODEL
    if uploaded_image:
        st.info("Image detected → skipping reasoning model")
        image_bytes = uploaded_image.read()

        img = generate_image(user_prompt, image_bytes)
        st.image(img, caption="Generated Interior")

    # CASE 2: TEXT → REASONING → IMAGES
    else:
        layout = run_reasoning(user_prompt)

        if layout is None:
            st.error("❌ Not an interior design task")
            st.stop()

        st.subheader("📄 Generated Layout JSON")
        st.json(layout)

        for floor in layout["house"]["floors"]:
            for room in floor["rooms"]:
                prompt = f"""
                Ultra-realistic interior design of a {room['room_type']}
                Room name: {room['room_name']}
                Dimensions: {room['dimensions']}
                Furniture layout: {room['furniture']}
                Modern lighting, realistic materials, 4K render
                """
                img = generate_image(prompt)
                st.image(img, caption=room["room_name"])
