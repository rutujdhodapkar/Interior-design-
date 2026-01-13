import streamlit as st
import time
from typing import Dict

# ===============================
# Streamlit Config
# ===============================
st.set_page_config(
    page_title="AI House Design Generator",
    layout="wide"
)

st.set_option("logger.level", "error")

# ===============================
# Session State Init
# ===============================
if "generated" not in st.session_state:
    st.session_state.generated = False

if "images" not in st.session_state:
    st.session_state.images = []

if "house_json" not in st.session_state:
    st.session_state.house_json = None

# ===============================
# Caesar Cipher Decryption
# ===============================
def caesar_decrypt(text: str, key: int = 3) -> str:
    result = ""
    for char in text:
        if char.isalpha():
            shift = 65 if char.isupper() else 97
            result += chr((ord(char) - shift - key) % 26 + shift)
        else:
            result += char
    return result

# ===============================
# MOCK OSS MODEL (replace later)
# provider-6/gpt-oss-120b
# ===============================
def call_oss_model(prompt: str, api_key: str) -> Dict:
    time.sleep(1)
    return {
        "house": {
            "total_area_sqft": 2200,
            "floors": [
                {
                    "floor": 1,
                    "rooms": [
                        {
                            "name": "Living Room",
                            "dimensions_ft": "18x15",
                            "design_style": "Modern Minimal",
                            "furniture": ["Sofa", "Coffee Table", "TV Unit"]
                        },
                        {
                            "name": "Kitchen",
                            "dimensions_ft": "12x10",
                            "design_style": "Contemporary",
                            "furniture": ["Modular Cabinets", "Island", "Chimney"]
                        }
                    ]
                },
                {
                    "floor": 2,
                    "rooms": [
                        {
                            "name": "Master Bedroom",
                            "dimensions_ft": "16x14",
                            "design_style": "Luxury Modern",
                            "furniture": ["King Bed", "Wardrobe", "Side Tables"]
                        }
                    ]
                }
            ]
        }
    }

# ===============================
# MOCK IMAGE MODEL
# provider-4/imagen-4
# ===============================
def call_image_model(prompt: str, api_key: str) -> str:
    time.sleep(1)
    return (
        "https://via.placeholder.com/900x600.png?text="
        + prompt.replace(" ", "+")[:100]
    )

# ===============================
# UI
# ===============================
st.title("🏠 AI House Design Generator")
st.caption("Auto pipeline · Sequential images · Stable Streamlit execution")

encrypted_api_key = st.text_input(
    "Encrypted API Key",
    value="ggf-d4i-5g489223hee84f0387e2f7h3fe01d751",
    type="password"
)

user_prompt = st.text_area(
    "Describe your house",
    placeholder="2 floor modern house with open kitchen, 3 bedrooms, balcony..."
)

# ===============================
# GENERATION PIPELINE
# ===============================
if st.button("Generate House Design 🚀") and not st.session_state.generated:

    if not user_prompt.strip():
        st.error("Prompt required.")
        st.stop()

    decrypted_key = caesar_decrypt(encrypted_api_key)

    with st.spinner("Reasoning with OSS model..."):
        house_json = call_oss_model(user_prompt, decrypted_key)

    st.session_state.house_json = house_json
    st.session_state.images = []

    total_steps = sum(
        len(floor["rooms"]) for floor in house_json["house"]["floors"]
    ) + 2  # floorplan + exterior

    progress = st.progress(0.0)
    step = 0

    # ---- ROOM IMAGES ----
    for floor in house_json["house"]["floors"]:
        for room in floor["rooms"]:
            prompt = (
                f"{room['name']} interior, {room['design_style']}, "
                f"furnished, {room['dimensions_ft']}"
            )

            img = call_image_model(prompt, decrypted_key)

            st.session_state.images.append({
                "title": f"{room['name']} (Floor {floor['floor']})",
                "url": img
            })

            step += 1
            progress.progress(step / total_steps)

    # ---- 2D FLOOR PLAN ----
    floorplan = call_image_model(
        "2D architectural floor plan, white background, dimensions, notations",
        decrypted_key
    )

    st.session_state.images.append({
        "title": "2D Floor Plan",
        "url": floorplan
    })

    step += 1
    progress.progress(step / total_steps)

    # ---- EXTERIOR ----
    exterior = call_image_model(
        "Modern house exterior realistic render",
        decrypted_key
    )

    st.session_state.images.append({
        "title": "Exterior View",
        "url": exterior
    })

    progress.progress(1.0)
    st.session_state.generated = True

# ===============================
# RENDER RESULTS
# ===============================
if st.session_state.generated:

    st.subheader("📐 Structured 2D Design (JSON)")
    st.json(st.session_state.house_json)

    st.subheader("🖼️ Auto-Generated Images")

    for img in st.session_state.images:
        st.image(
            img["url"],
            caption=img["title"],
            use_container_width=True
        )

    if st.button("Reset 🔄"):
        st.session_state.generated = False
        st.session_state.images = []
        st.session_state.house_json = None
