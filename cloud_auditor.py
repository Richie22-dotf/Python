import streamlit as st
from pillow_heif import register_heif_opener
from PIL import Image
from google import genai
from pydantic import BaseModel
from typing import List
import time, json, os

register_heif_opener()
st.set_page_config(page_title="CloudGuard AI - DevSecOps & Architecture Auditor", layout="wide")

st.markdown('''
    <style>
    .stApp { background-color: #0B0F17; color: #E6EDF3; }
    h1, h2, h3 { color: #38BDF8 !important; font-family: "Courier New", monospace; }
    .audit-card {
        background-color: #131A26;
        border: 1px solid #1E293B;
        border-left: 4px solid #38BDF8;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .finding-crit {
        background-color: #2A1215; border-left: 4px solid #F85149;
        padding: 10px 14px; border-radius: 6px; margin: 8px 0;
    }
    .finding-med {
        background-color: #271F10; border-left: 4px solid #D29922;
        padding: 10px 14px; border-radius: 6px; margin: 8px 0;
    }
    button[data-testid="stBaseButton-primary"],
    button[data-testid="stBaseButton-secondary"],
    div.stButton > button {
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
        border: 1px solid #38BDF8 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    </style>
''', unsafe_allow_html=True)

class CloudAuditReport(BaseModel):
    target_type: str
    posture_rating: str
    security_score: int
    executive_summary: str
    critical_findings: List[str]
    remediation_steps: List[str]
    hardened_code_or_blueprint: str

SAMPLE_CONFIGS = {
    "Vulnerable AWS Terraform (Public S3 + Open SSH)": '''resource "aws_s3_bucket" "customer_data" {
  bucket = "prod-customer-records-2026"
  acl    = "public-read-write"
}

resource "aws_security_group" "web_sg" {
  name = "allow_all_ssh"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}''',
    "Vulnerable Dockerfile (Root User + Hardcoded Secret)": '''FROM ubuntu:latest
ENV AWS_SECRET_ACCESS_KEY="AKIAIOSFODNN7EXAMPLEKEY"
RUN apt-get update && apt-get install -y python3 curl
COPY . /app
WORKDIR /app
EXPOSE 80 22
CMD ["python3", "app.py"]''',
    "Over-Permissive AWS IAM Policy": '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}'''
}

st.title("CloudGuard AI - DevSecOps & Architecture Auditor")
st.caption("INFRASTRUCTURE-AS-CODE SCANNER | MULTIMODAL DIAGRAM REVIEW | AUTOMATED REMEDIATION")

api_key = os.environ.get("GEMINI_API_KEY", "")
try:
    if not api_key and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    pass

def run_gemini_audit(contents_list):
    client = genai.Client(api_key=api_key)
    live_models = [
        m.name.replace("models/", "") for m in client.models.list()
        if "gemini" in m.name.lower()
        and not any(x in m.name.lower() for x in ["audio", "tts", "embedding", "vision-001", "aqa", "imagen", "veo"])
    ]
    live_models.sort(key=lambda x: (0 if "flash" in x else (1 if "lite" in x else 2), x))
    last_err = ""
    for m_name in live_models:
        for _ in range(2):
            try:
                res = client.models.generate_content(
                    model=m_name,
                    contents=contents_list,
                    config={"response_mime_type": "application/json", "response_schema": CloudAuditReport},
                )
                if res and res.text:
                    return json.loads(res.text)
            except Exception as e:
                last_err = str(e)
                if "503" in last_err:
                    time.sleep(2)
                    continue
                break
    raise Exception(last_err or "Models temporarily busy. Please try again.")

def render_report(report):
    score = max(1, min(100, int(report.get("security_score", 50))))
    rating = report.get("posture_rating", "NEEDS HARDENING")
    st.markdown(f'''
    <div class="audit-card">
        <h3>[AUDIT VERDICT] {rating.upper()} ({score}/100)</h3>
        <p><strong>Target Analyzed:</strong> {report.get("target_type", "Cloud Infrastructure")}</p>
        <p>{report.get("executive_summary", "")}</p>
    </div>
    ''', unsafe_allow_html=True)
    st.progress(score)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Vulnerability Findings")
        for f in report.get("critical_findings", []):
            st.markdown(f"<div class='finding-crit'>{f}</div>", unsafe_allow_html=True)
    with col2:
        st.subheader("Actionable Remediation")
        for step in report.get("remediation_steps", []):
            st.markdown(f"<div class='finding-med'>{step}</div>", unsafe_allow_html=True)

    st.subheader("Hardened Configuration / Reference Architecture")
    st.code(report.get("hardened_code_or_blueprint", ""), language="hcl")

tab_iac, tab_diagram = st.tabs(["Audit IaC / Config Code", "Audit Architecture Diagram"])

with tab_iac:
    sample_choice = st.selectbox("Load Sample Template (or paste your own below):", ["Custom Input"] + list(SAMPLE_CONFIGS.keys()))
    default_code = SAMPLE_CONFIGS.get(sample_choice, "")
    code_input = st.text_area("Paste Terraform, Dockerfile, Kubernetes YAML, or IAM JSON:", value=default_code, height=220)

    if st.button("Run DevSecOps Config Audit", use_container_width=True):
        if not code_input.strip():
            st.warning("Paste a configuration snippet or choose a sample template first.")
        elif not api_key:
            st.error("Missing GEMINI_API_KEY in ~/.zshrc or Streamlit Secrets.")
        else:
            with st.spinner("Scanning IaC for CIS benchmark violations, IAM wildcards, and exposed ports..."):
                try:
                    prompt = (
                        "You are a Principal Cloud Security Architect & DevSecOps Engineer. "
                        "Audit this Infrastructure-as-Code or cloud configuration for security misconfigurations, "
                        "least-privilege IAM violations, unencrypted storage, exposed ingress ports, and hardcoded secrets. "
                        "Provide critical_findings, step-by-step remediation_steps, a security_score (0-100), posture_rating, "
                        "and the complete, production-hardened replacement code in hardened_code_or_blueprint:\n\n"
                        f"{code_input}"
                    )
                    rep = run_gemini_audit([prompt])
                    render_report(rep)
                except Exception as e:
                    st.error(f"Audit error: {e}")

with tab_diagram:
    st.info("Upload a screenshot or photo of an AWS/Azure/GCP architecture diagram, network topology, or whiteboard sketch.")
    diag_file = st.file_uploader("Upload Architecture Diagram", type=["png", "jpg", "jpeg", "webp", "heic"])
    if diag_file is not None:
        pil_img = Image.open(diag_file)
        st.image(pil_img, caption="Architecture Diagram Under Review", use_container_width=True)
        if st.button("Audit Cloud Architecture Diagram", use_container_width=True):
            if not api_key:
                st.error("Missing GEMINI_API_KEY in ~/.zshrc or Streamlit Secrets.")
            else:
                with st.spinner("Analyzing network trust boundaries, VPC segmentation, and attack surfaces..."):
                    try:
                        img_rgb = pil_img.copy().convert("RGB")
                        img_rgb.thumbnail((1100, 1100))
                        prompt = (
                            "You are a Principal Cloud Security Architect reviewing this network or cloud architecture diagram. "
                            "Identify missing security controls (WAF, private subnets, bastion/SSM, encryption in transit/at rest, "
                            "overly broad ingress routes, single points of failure). Provide critical_findings, remediation_steps, "
                            "security_score (0-100), posture_rating, and a hardened Terraform or architectural blueprint outline in hardened_code_or_blueprint."
                        )
                        rep = run_gemini_audit([img_rgb, prompt])
                        render_report(rep)
                    except Exception as e:
                        st.error(f"Diagram audit error: {e}")
