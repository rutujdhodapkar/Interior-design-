import streamlit as st
import time

# ===============================
# PAGE CONFIG (FIRST LINE)
# ===============================
st.set_page_config(
    page_title="AI House Design Generator",
    layout="wide"
)

# ===============================
# FORCE LIGHT UI (NO DARK MODE)
# ===============================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    textarea, input {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    label {
        color: #000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# SESSION STATE
# ===============================
if "generated" not in st.session_state:
    st.session_state.generated = False

if "images" not in st.session_state:
    st.session_state.images = []

if "house_json" not in st.session_state:
    st.session_state.house_json = None

# ===============================
# CAESAR DECRYPT (KEY = 3)
# ===============================
def caesar_decrypt(text, key=3):
    result = ""
    for char in text:
        if char.isalpha():
            shift = 65 if char.isupper() else 97
            result += chr((ord(char) - shift - key) % 26 + shift)
        else:
            result += char
    return result

# ===============================
# MOCK OSS MODEL
# ===============================
def call_oss_model(prompt, api_key):
    time.sleep(1)
    return {
        "house": {
            "floors": [
                {
                    "floor": 1,
                    "rooms": [
                        {
                            "name": "Living Room",
                            "dimensions": "18x15 ft",
                            "style": "Modern Minimal",
                            "furniture": ["Sofa", "TV Unit", "Coffee Table"]
                        },
                        {
                            "name": "Kitchen",
                            "dimensions": "12x10 ft",
                            "style": "Contemporary",
                            "furniture": ["Cabinets", "Island", "Chimney"]
                        }
                    ]
                },
                {
                    "floor": 2,
                    "rooms": [
                        {
                            "name": "Master Bedroom",
                            "dimensions": "16x14 ft",
                            "style": "Luxury Modern",
                            "furniture": ["King Bed", "Wardrobe", "Side Tables"]
                        }
                    ]
                }
            ]
        }
    }

# ===============================
# MOCK IMAGE MODEL
# ===============================
def call_image_model(prompt, api_key):
    time.sleep(1)
    return (
        "https://via.placeholder.com/900x600.png?text="
        + prompt.replace(" ", "+")[:120]
    )

# ===============================
# UI
# ===============================
st.title("🏠 AI House Design Generator")
st.write("Auto pipeline · White UI · Sequential image generation")

encrypted_api_key = st.text_input(
    "Encrypted API Key",
    value="ggf-d4i-5g489223hee84f0387e2f7h3fe01d751"
)

user_prompt = st.text_area(
    "Describe your house requirements",
    placeholder="2 floor modern house, open kitchen, balcony, 3 bedrooms"
)

# ===============================
# GENERATE PIPELINE
# ===============================
if st.button("Generate House Design 🚀") and not st.session_state.generated:

    if not user_prompt.strip():
        st.error("Please enter a house description.")
        st.stop()

    decrypted_key = caesar_decrypt(encrypted_api_key)

    with st.spinner("Thinking (OSS model)..."):
        house_json = call_oss_model(user_prompt, decrypted_key)

    st.session_state.house_json = house_json
    st.session_state.images = []

    total = sum(len(f["rooms"]) for f in house_json["house"]["floors"]) + 2
    progress = st.progress(0.0)
    step = 0

    # ROOMS
    for floor in house_json["house"]["floors"]:
        for room in floor["rooms"]:
            prompt = (
                f"{room['name']} interior, {room['style']}, "
                f"furnished, {room['dimensions']}"
            )
            img = call_image_model(prompt, decrypted_key)

            st.session_state.images.append({
                "title": f"{room['name']} (Floor {floor['floor']})",
                "url": img
            })

            step += 1
            progress.progress(step / total)

    # FLOOR PLAN
    floorplan = call_image_model(
        "2D architectural floor plan white background with dimensions",
        decrypted_key
    )
    st.session_state.images.append({
        "title": "2D Floor Plan",
        "url": floorplan
    })

    step += 1
    progress.progress(step / total)

    # EXTERIOR
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
# RENDER OUTPUT
# ===============================
if st.session_state.generated:

    st.subheader("📐 Structured Design (JSON)")
    st.json(st.session_state.house_json)

    st.subheader("🖼️ Generated Images")

    for img in st.session_state.images:
        st.image(img["url"], caption=img["title"], use_container_width=True)

    if st.button("Reset 🔄"):
        st.session_state.generated = False
        st.session_state.images = []
        st.session_state.house_json = None
