import streamlit as st
import time
import json

# ===============================
# Streamlit Config
# ===============================
st.set_page_config(
    page_title="AI House Design Generator",
    layout="wide"
)

# ===============================
# Session State
# ===============================
if "generated" not in st.session_state:
    st.session_state.generated = False

if "house_json" not in st.session_state:
    st.session_state.house_json = None

# ===============================
# Caesar Decrypt
# ===============================
def caesar_decrypt(text, key=3):
    result = ""
    for c in text:
        if c.isalpha():
            base = 65 if c.isupper() else 97
            result += chr((ord(c) - base - key) % 26 + base)
        else:
            result += c
    return result

# ===============================
# MOCK OSS MODEL (JSON OUTPUT)
# ===============================
def call_oss_model(prompt, api_key):
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
                            "style": "Modern Minimal",
                            "furniture": ["Sofa", "Coffee Table", "TV Unit"]
                        },
                        {
                            "name": "Kitchen",
                            "dimensions_ft": "12x10",
                            "style": "Contemporary",
                            "furniture": ["Modular Cabinets", "Island", "Chimney"]
                        }
                    ]
                }
            ]
        }
    }

# ===============================
# IMAGE MODEL (JSON → IMAGE)
# ===============================
def call_image_model(json_payload, api_key):
    """
    Image model receives FULL JSON description.
    """
    time.sleep(1)

    # simulate image generation
    prompt = json.dumps(json_payload)
    return (
        "https://via.placeholder.com/900x600.png?text="
        + prompt[:120].replace(" ", "+")
    )

# ===============================
# UI
# ===============================
st.title("🏠 AI Interior + House Generator")

encrypted_key = st.text_input(
    "Encrypted API Key",
    value="ggf-d4i-5g489223hee84f0387e2f7h3fe01d751",
    type="password"
)

user_prompt = st.text_area(
    "Describe your house",
    placeholder="Modern 2-floor house with open kitchen and balcony"
)

# ===============================
# PIPELINE
# ===============================
if st.button("Generate 🚀") and not st.session_state.generated:

    api_key = caesar_decrypt(encrypted_key)

    with st.spinner("Reasoning (OSS model)..."):
        house_json = call_oss_model(user_prompt, api_key)

    st.session_state.house_json = house_json
    st.session_state.generated = True

# ===============================
# RENDER + AUTO IMAGE GENERATION
# ===============================
if st.session_state.generated:

    st.subheader("📐 House JSON Structure")
    st.json(st.session_state.house_json)

    st.subheader("🖼️ Auto-Generated Images")

    progress = st.progress(0.0)
    image_container = st.empty()

    floors = st.session_state.house_json["house"]["floors"]
    total = sum(len(f["rooms"]) for f in floors) + 2
    step = 0

    # ---- ROOM IMAGES ----
    for floor in floors:
        for room in floor["rooms"]:

            room_payload = {
                "type": "room_interior",
                "floor": floor["floor"],
                "room": room,
                "render": "photorealistic, furnished"
            }

            img = call_image_model(room_payload, encrypted_key)

            image_container.image(
                img,
                caption=f"{room['name']} – Floor {floor['floor']}",
                use_container_width=True
            )

            step += 1
            progress.progress(step / total)

    # ---- FLOOR PLAN ----
    floorplan_payload = {
        "type": "2d_floor_plan",
        "style": "white paper",
        "notations": True,
        "house": st.session_state.house_json
    }

    image_container.image(
        call_image_model(floorplan_payload, encrypted_key),
        caption="2D Floor Plan",
        use_container_width=True
    )

    step += 1
    progress.progress(step / total)

    # ---- EXTERIOR ----
    exterior_payload = {
        "type": "house_exterior",
        "style": "modern realistic",
        "house": st.session_state.house_json
    }

    image_container.image(
        call_image_model(exterior_payload, encrypted_key),
        caption="Exterior View",
        use_container_width=True
    )

    progress.progress(1.0)

    st.success("Images generated from JSON successfully ✅")
