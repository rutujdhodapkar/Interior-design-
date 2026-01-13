import streamlit as st
import time
import json
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

# ===============================
# Streamlit Config
# ===============================
st.set_page_config(
    page_title="AI House Design Generator",
    layout="wide"
)

# ===============================
# Load Stable Diffusion (ONCE)
# ===============================
@st.cache_resource
def load_sd():
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    return pipe

pipe = load_sd()

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
    return {
        "house": {
            "floors": [
                {
                    "floor": 1,
                    "rooms": [
                        {
                            "name": "Living Room",
                            "dimensions": "18x15 ft",
                            "style": "modern minimal",
                            "furniture": ["sofa", "coffee table", "tv unit"]
                        },
                        {
                            "name": "Kitchen",
                            "dimensions": "12x10 ft",
                            "style": "contemporary",
                            "furniture": ["modular cabinets", "kitchen island"]
                        }
                    ]
                }
            ]
        }
    }

# ===============================
# JSON → IMAGE PROMPT
# ===============================
def generate_room_image(room_json):
    prompt = (
        f"photorealistic {room_json['style']} {room_json['name']} interior, "
        f"fully furnished with {', '.join(room_json['furniture'])}, "
        f"luxury lighting, ultra realistic, interior design, high quality"
    )

    image = pipe(
        prompt,
        num_inference_steps=30,
        guidance_scale=7.5
    ).images[0]

    return image

# ===============================
# UI
# ===============================
st.title("🏠 AI Furnished Room Generator (REAL IMAGES)")
st.caption("Stable Diffusion powered · JSON → Interior Images")

encrypted_key = st.text_input(
    "Encrypted API Key",
    type="password"
)

user_prompt = st.text_area(
    "Describe your house",
    placeholder="Modern 2 floor house with open kitchen"
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
# RENDER + IMAGE GEN
# ===============================
if st.session_state.generated:

    st.subheader("📐 Design JSON")
    st.json(st.session_state.house_json)

    st.subheader("🖼️ Furnished Room Images")

    progress = st.progress(0.0)
    rooms = st.session_state.house_json["house"]["floors"][0]["rooms"]

    for i, room in enumerate(rooms):
        with st.spinner(f"Generating {room['name']}..."):
            img = generate_room_image(room)

        st.image(
            img,
            caption=f"{room['name']} ({room['style']})",
            use_container_width=True
        )

        st.code(json.dumps(room, indent=2), language="json")
        progress.progress((i + 1) / len(rooms))

    st.success("✅ Real furnished images generated")

    if st.button("Reset 🔄"):
        st.session_state.generated = False
        st.session_state.house_json = None
