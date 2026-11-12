import streamlit as st
from pillow_heif import register_heif_opener
from PIL import Image
from google import genai
from pydantic import BaseModel
import time
import json
import os

register_heif_opener()

st.set_page_config(page_title="Aficionado AI Cigar Sommelier", page_icon="🍂", layout="centered")

# --- CUSTOM MAHOGANY & GOLD LOUNGE STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #1C110A; color: #F5E6CC; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: Georgia, serif; }
    .cigar-card {
        background-color: #2A1A10;
        border: 1px solid #D4AF37;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
    }
    .gold-label { color: #D4AF37; font-weight: bold; letter-spacing: 1px; font-size: 0.85em; }
    
    /* Force Primary & Standard Buttons to Gold Lounge Theme */
    div.stButton > button, button[kind="primary"] {
        background-color: #D4AF37 !important;
        color: #1C110A !important;
        border: 1px solid #F5E6CC !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    div.stButton > button:hover, button[kind="primary"]:hover {
        background-color: #E5C158 !important;
        color: #1C110A !important;
    }
    </style>
""", unsafe_allow_html=True)

class CigarProfile(BaseModel):
    cigar_name: str
    brand: str
    origin: str
    wrapper: str
    binder: str
    filler: str
    strength: int
    strength_label: str
    notes: str
    pairing: str

if "cigar_db" not in st.session_state:
    st.session_state.cigar_db = {
        "INCH Nicaragua No. 60": {"brand": "E.P. Carrillo", "origin": "Nicaragua", "wrapper": "Nicaraguan Habano", "binder": "Nicaraguan", "filler": "Nicaraguan", "strength": 85, "strength_label": "Medium-Full to Full", "notes": "Bold black pepper, dark espresso, rich leather, and toasted cedar.", "pairing": "Barrel-Proof Bourbon or Double Espresso"},
        "New World by AJ Fernandez": {"brand": "AJ Fernandez", "origin": "Nicaragua", "wrapper": "Nicaraguan Oscuro", "binder": "Nicaraguan Jalapa", "filler": "Nicaraguan", "strength": 88, "strength_label": "Full-Bodied", "notes": "Dark cocoa, roasted coffee beans, rich earth, and signature AJ pepper.", "pairing": "Single Malt Scotch or Espresso"},
        "Ashton VSG Sorcerer": {"brand": "Ashton", "origin": "Dominican Republic", "wrapper": "Ecuadorian Sumatra", "binder": "Dominican", "filler": "Dominican", "strength": 90, "strength_label": "Full-Bodied", "notes": "Rich cedar, espresso, dark chocolate, warm leather, and bold spice.", "pairing": "XO Cognac, Tawny Port, or Neat Bourbon"},
        "Drew Estate Undercrown Maduro": {"brand": "Drew Estate", "origin": "Nicaragua", "wrapper": "Mexican San Andres Maduro", "binder": "Connecticut Habano", "filler": "Brazilian & Nicaraguan", "strength": 78, "strength_label": "Medium-Full", "notes": "Velvety dark chocolate, sweet espresso, earth, cream, and black pepper.", "pairing": "Porter Beer, Bourbon, or Cappuccino"},
        "Ashton Classic Magnum": {"brand": "Ashton", "origin": "Dominican Republic", "wrapper": "Connecticut Shade", "binder": "Dominican", "filler": "Dominican", "strength": 35, "strength_label": "Mild to Medium", "notes": "Silky buttered toast, vanilla bean, light cedar, and creamy cashew.", "pairing": "Morning Latte or Chardonnay"}
    }

st.title("🍂 Aficionado AI Cigar Sommelier")
st.caption("LIVE AI BAND VISION • WRAPPER TELEMETRY • DIGITAL HUMIDOR")

api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

tab_scan, tab_humidor = st.tabs(["📸 Scan Cigar Band", "🗄️ Digital Humidor"])

with tab_scan:
    input_mode = st.radio("Choose Input Method:", ["Upload Photo", "Live Camera"], horizontal=True)
    img_file = st.camera_input("Snap Cigar Band") if input_mode == "Live Camera" else st.file_uploader("Upload Cigar Photo", type=["png", "jpg", "jpeg", "heic", "webp"])

    if img_file is not None:
        pil_img = Image.open(img_file)
        st.image(pil_img, caption="Uploaded Cigar", use_container_width=True)

        if st.button("✨ Identify Cigar with AI Vision", use_container_width=True):
            if not api_key:
                st.error("Missing GEMINI_API_KEY. Add it in Streamlit App Secrets.")
            else:
                with st.spinner("AI Sommelier examining band and wrapper..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        img_rgb = pil_img.copy().convert("RGB")
                        img_rgb.thumbnail((800, 800))

                        # Prioritize high-capacity production & lite Flash models to avoid 503 spikes
                        priority_models = [
                            "gemini-2.5-flash-lite",
                            "gemini-2.0-flash",
                            "gemini-3.8-flash-lite",
                            "gemini-3.8-flash",
                            "gemini-2.5-pro"
                        ]

                        res = None
                        last_err = ""
                        for m_name in priority_models:
                            try:
                                res = client.models.generate_content(
                                    model=m_name,
                                    contents=[img_rgb, "Identify this exact cigar from its band and wrapper. Provide accurate sommelier details."],
                                    config={"response_mime_type": "application/json", "response_schema": CigarProfile},
                                )
                                if res and res.text:
                                    break
                            except Exception as inner_e:
                                last_err = str(inner_e)
                                time.sleep(1)
                                continue

                        if not res or not res.text:
                            raise Exception(last_err or "Servers busy. Please try again in a few seconds.")

                        data = json.loads(res.text)
                        name = data["cigar_name"]
                        st.session_state.cigar_db[name] = data
                        st.session_state.selected_cigar = name
                        st.success(f"✅ Matched: {name} — Switch to the 'Digital Humidor' tab to view full tasting notes!")
                    except Exception as e:
                        st.error(f"Scan error: {e}")

with tab_humidor:
    names = list(st.session_state.cigar_db.keys())
    default_idx = names.index(st.session_state.selected_cigar) if "selected_cigar" in st.session_state and st.session_state.selected_cigar in names else 0
    selected = st.selectbox("Select or Browse Humidor:", names, index=default_idx)
    info = st.session_state.cigar_db[selected]

    st.markdown(f"""
    <div class="cigar-card">
        <h2>{selected}</h2>
        <p style="color:#B89F82;"><strong>{info['brand']}</strong> • Origin: {info['origin']}</p>
        <hr style="border-color:#3D2618;">
        <p><span class="gold-label">WRAPPER:</span> {info['wrapper']}</p>
        <p><span class="gold-label">BINDER:</span> {info['binder']}</p>
        <p><span class="gold-label">FILLER:</span> {info['filler']}</p>
        <p><span class="gold-label">STRENGTH:</span> {info['strength_label']} ({info['strength']}/100)</p>
        <p><span class="gold-label">TASTING NOTES:</span> <em>{info['notes']}</em></p>
        <p><span class="gold-label">LOUNGE PAIRING:</span> {info['pairing']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.progress(max(1, min(100, int(info["strength"]))))
