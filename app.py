import streamlit as st
import json
import time
from typing import Dict, List

# -------------------------------
# Caesar Cipher Decryption (key=3)
# -------------------------------
def caesar_decrypt(text: str, key: int = 3) -> str:
    result = ""
    for char in text:
        if char.isalpha():
            shift = 65 if char.isupper() else 97
            result += chr((ord(char) - shift - key) % 26 + shift)
        else:
            result += char
    return result


# -------------------------------
# Mock OSS LLM Call (replace later)
# -------------------------------
def call_oss_model(prompt: str, api_key: str) -> Dict:
    """
    Model: provider-6/gpt-oss-120b
    This is a mocked response. Replace with real API call later.
    """

    # Simulated structured output
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
                            "furniture": ["Sofa", "Coffee Table", "TV Unit"],
                            "design_style": "Modern minimal"
                        },
                        {
                            "name": "Kitchen",
                            "dimensions_ft": "12x10",
                            "furniture": ["Modular Cabinets", "Island", "Chimney"],
                            "design_style": "Contemporary"
                        }
                    ]
                },
                {
                    "floor": 2,
                    "rooms": [
                        {
                            "name": "Master Bedroom",
                            "dimensions_ft": "16x14",
                            "furniture": ["King Bed", "Wardrobe", "Side Tables"],
                            "design_style": "Luxury modern"
                        }
                    ]
                }
            ]
        }
    }


# -------------------------------
# Mock Image Generation Call
# -------------------------------
def call_image_model(description: str, api_key: str) -> str:
    """
    Model: provider-4/imagen-4
    Returns a placeholder image URL.
    Replace with real image generation API.
    """
    time.sleep(1)  # simulate latency
    return "https://via.placeholder.com/800x600.png?text=" + description.replace(" ", "+")


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="AI House Design Pipeline", layout="wide")

st.title("🏠 AI House Design Generator")
st.caption("OSS reasoning → structured design → sequential image generation")

encrypted_api_key = st.text_input(
    "Encrypted API Key",
    value="ggf-d4i-5g489223hee84f0387e2f7h3fe01d751",
    type="password"
)

user_prompt = st.text_area(
    "Describe your house requirements",
    placeholder="e.g. 2 floor modern house with 3 bedrooms, open kitchen, balcony..."
)

if st.button("Generate House Design 🚀"):

    if not user_prompt.strip():
        st.error("Prompt required. Don’t be lazy.")
        st.stop()

    # Decrypt API key
    decrypted_key = caesar_decrypt(encrypted_api_key)

    st.success("API key decrypted successfully.")

    # Call OSS model
    with st.spinner("Reasoning with OSS model..."):
        house_json = call_oss_model(user_prompt, decrypted_key)

    st.subheader("📐 Structured 2D Design (JSON)")
    st.json(house_json)

    # Image generation pipeline
    st.subheader("🖼️ Generated Visuals")

    for floor in house_json["house"]["floors"]:
        st.markdown(f"## Floor {floor['floor']}")

        for room in floor["rooms"]:
            desc = (
                f"{room['name']} | {room['design_style']} | "
                f"Dimensions {room['dimensions_ft']} | "
                f"Furniture: {', '.join(room['furniture'])}"
            )

            with st.spinner(f"Generating image for {room['name']}..."):
                img_url = call_image_model(desc, decrypted_key)

            st.image(img_url, caption=desc, use_container_width=True)

    # Floor plan + exterior
    st.markdown("## 🧾 2D Floor Plan (White Paper)")
    floorplan_img = call_image_model(
        "2D architectural floor plan white background with dimensions and notations",
        decrypted_key
    )
    st.image(floorplan_img, use_container_width=True)

    st.markdown("## 🏡 Exterior View")
    exterior_img = call_image_model(
        "Modern house exterior realistic render",
        decrypted_key
    )
    st.image(exterior_img, use_container_width=True)

    st.success("Pipeline complete. Clean. Sequential. Controlled. 😎")
