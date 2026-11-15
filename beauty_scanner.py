import streamlit as st
from pillow_heif import register_heif_opener
from PIL import Image
from google import genai
from pydantic import BaseModel
from typing import List
import time, json, os

register_heif_opener()
st.set_page_config(page_title="12 Esthetics AI • Beauty & Ethics Scanner", page_icon="🌿", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #111614; color: #F2EFE9; }
    h1, h2, h3 { color: #D8B878 !important; font-family: Georgia, serif; }
    .product-card { background-color: #1A221F; border: 1px solid #4E7A65; border-radius: 14px; padding: 22px; margin-top: 15px; }
    .gold-label { color: #D8B878; font-weight: bold; letter-spacing: 0.8px; font-size: 0.85em; }
    .badge-ethical { background-color: #1E4632; color: #7EE787; border: 1px solid #3FB950; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 0.85em; display: inline-block; }
    .badge-mixed { background-color: #423315; color: #F2CC60; border: 1px solid #D29922; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 0.85em; display: inline-block; }
    .badge-unethical { background-color: #491B1D; color: #FF7B72; border: 1px solid #F85149; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 0.85em; display: inline-block; }
    button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-secondary"], div.stButton > button {
        background-color: #4E7A65 !important; color: #FFFFFF !important; border: 1px solid #D8B878 !important; font-weight: bold !important; border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

class BeautyAudit(BaseModel):
    product_name: str
    brand: str
    category: str
    main_components: List[str]
    ingredient_benefits_and_flags: str
    clean_score: int
    sourcing_verdict: str
    cruelty_free_status: str
    high_risk_ingredients_audit: str
    ethics_summary: str

if "beauty_shelf" not in st.session_state:
    st.session_state.beauty_shelf = {
        "The Ordinary Niacinamide 10% + Zinc 1%": {
            "brand": "The Ordinary (DECIEM)", "category": "Facial Serum",
            "main_components": ["Niacinamide (Vitamin B3) — 10%", "Zinc PCA — 1%", "Tamarindus Indica Seed Gum", "Pentylene Glycol"],
            "ingredient_benefits_and_flags": "Fragrance-free, silicone-free, oil-free formula that regulates sebum and minimizes pores.",
            "clean_score": 88, "sourcing_verdict": "Ethical / Certified",
            "cruelty_free_status": "Cruelty-Free & 100% Vegan.",
            "high_risk_ingredients_audit": "Free of mica, palm-derived high-risk esters, and animal byproducts.",
            "ethics_summary": "Transparent clinical formulation with vegan, cruelty-free standards."
        }
    }

st.title("🌿 12 Esthetics AI • Beauty & Ethics Scanner")
st.caption("INGREDIENT TELEMETRY • SUPPLY-CHAIN ETHICS AUDIT • DIGITAL VANITY SHELF")

api_key = os.environ.get("GEMINI_API_KEY", "")
try:
    if not api_key and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    pass

tab_scan, tab_shelf = st.tabs(["📸 Scan Product / Label", "🪞 Digital Vanity Shelf"])

with tab_scan:
    st.info("💡 Tip: Snap either the front bottle/compact OR the back ingredient list for the deepest analysis.")
    input_mode = st.radio("Choose Input Method:", ["Upload Photo", "Live Camera"], horizontal=True)
    img_file = st.camera_input("Snap Beauty Product") if input_mode == "Live Camera" else st.file_uploader("Upload Product Photo", type=["png", "jpg", "jpeg", "heic", "webp"])

    if img_file is not None:
        pil_img = Image.open(img_file)
        st.image(pil_img, caption="Product to Analyze", use_container_width=True)

        if st.button("🔬 Analyze Ingredients & Ethical Sourcing", use_container_width=True):
            if not api_key:
                st.error("Missing GEMINI_API_KEY. Set it in ~/.zshrc (local) or Streamlit App Secrets (cloud).")
            else:
                with st.spinner("Auditing active ingredients, formulation safety, and ethical supply chain..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        img_rgb = pil_img.copy().convert("RGB")
                        img_rgb.thumbnail((900, 900))
                        prompt = (
                            "Analyze this beauty, skincare, haircare, or cosmetic product from its packaging or ingredient list. "
                            "1) Identify product_name, brand, and category. "
                            "2) List main_components and explain ingredient_benefits_and_flags (parabens, sulfates, synthetic fragrance). "
                            "3) Rate clean_score from 0 to 100. "
                            "4) Classify sourcing_verdict strictly as Ethical / Certified, Mixed / Needs Verification, or Unethical / High Risk, "
                            "detailing cruelty_free_status, high_risk_ingredients_audit (mica child labor, palm oil deforestation), and ethics_summary."
                        )
                        live_models = [
                            m.name.replace("models/", "") for m in client.models.list()
                            if "gemini" in m.name.lower() and not any(x in m.name.lower() for x in ["audio", "tts", "embedding", "vision-001", "aqa", "imagen", "veo"])
                        ]
                        live_models.sort(key=lambda x: (0 if "lite" in x else (1 if "flash" in x else 2), x))
                        res = None
                        last_err = ""
                        for m_name in live_models:
                            for attempt in range(2):
                                try:
                                    res = client.models.generate_content(
                                        model=m_name, contents=[img_rgb, prompt],
                                        config={"response_mime_type": "application/json", "response_schema": BeautyAudit},
                                    )
                                    if res and res.text: break
                                except Exception as inner_e:
                                    last_err = str(inner_e)
                                    if "503" in last_err:
                                        time.sleep(2)
                                        continue
                                    break
                            if res and res.text: break
                        if not res or not res.text:
                            raise Exception(last_err or "Models temporarily busy. Please try again.")
                        data = json.loads(res.text)
                        name = data.get("product_name", "Scanned Product")
                        st.session_state.beauty_shelf.update({name: data})
                        st.session_state.selected_beauty = name
                        st.success(f"✅ Audit Complete: {name} — Switch to Digital Vanity Shelf to view the full report!")
                    except Exception as e:
                        st.error(f"Audit error: {e}")

with tab_shelf:
    names = list(st.session_state.beauty_shelf.keys())
    default_idx = names.index(st.session_state.selected_beauty) if "selected_beauty" in st.session_state and st.session_state.selected_beauty in names else 0
    selected = st.selectbox("Select Audited Product:", names, index=default_idx)
    info = st.session_state.beauty_shelf.get(selected, {})
    verdict = info.get("sourcing_verdict", "Mixed / Needs Verification")
    badge_cls = "badge-ethical" if ("Ethical" in verdict and "Unethical" not in verdict) else ("badge-unethical" if "Unethical" in verdict else "badge-mixed")
    badge_icon = "✅" if badge_cls == "badge-ethical" else ("🚨" if badge_cls == "badge-unethical" else "⚠️")
    comp_html = "".join([f"<li>{item}</li>" for item in info.get("main_components", [])])
    score = int(info.get("clean_score", 80))

    st.markdown(f"""
    <div class="product-card">
        <h2>{selected}</h2>
        <p style="color:#A3B8AE;"><strong>{info.get("brand", "")}</strong> • {info.get("category", "")}</p>
        <div class="{badge_cls}">{badge_icon} SOURCING VERDICT: {verdict.upper()}</div>
        <hr style="border-color:#2C3A34; margin:15px 0;">
        <p><span class="gold-label">MAIN COMPONENTS:</span></p>
        <ul style="margin-top:4px; color:#E6EDF3;">{comp_html}</ul>
        <p><span class="gold-label">FORMULA SAFETY & BENEFITS:</span> {info.get("ingredient_benefits_and_flags", "")}</p>
        <p><span class="gold-label">CRUELTY-FREE & ANIMAL TESTING:</span> {info.get("cruelty_free_status", "")}</p>
        <p><span class="gold-label">HIGH-RISK INGREDIENT AUDIT (MICA / PALM OIL / ETC.):</span> {info.get("high_risk_ingredients_audit", "")}</p>
        <p><span class="gold-label">ETHICS SUMMARY:</span> <em>{info.get("ethics_summary", "")}</em></p>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"Clean Formulation Score: {score}/100")
    st.progress(max(1, min(100, score)))
