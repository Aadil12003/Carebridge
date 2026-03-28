import streamlit as st
import pytesseract
import base64
import json
import requests
from PIL import Image
import re
from datetime import datetime
import fitz
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO
import pandas as pd

# Professional Minimal Theme
st.set_page_config(
    page_title="CareBridge | Clinical Coding",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS - Clean, Minimal, No Rainbow Colors
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: #fafafa;
    color: #1a1a1a;
}

/* Clean Header */
.main-header {
    background: #ffffff;
    border-bottom: 1px solid #e5e5e5;
    padding: 1.5rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
}

.logo-text {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a1a1a;
    letter-spacing: -0.02em;
}

.logo-accent {
    color: #0066cc;
    font-weight: 700;
}

/* Cards - Clean White */
.card {
    background: #ffffff;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.card:hover {
    border-color: #d0d0d0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* Section Headers - Clean */
.section-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #666;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #0066cc;
    display: inline-block;
}

/* PDx Display - Professional */
.pdx-box {
    background: #ffffff;
    border: 2px solid #0066cc;
    border-radius: 8px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
}

.pdx-code {
    font-family: 'SF Mono', Monaco, monospace;
    font-size: 2.5rem;
    font-weight: 700;
    color: #0066cc;
    letter-spacing: -0.02em;
}

.pdx-desc {
    font-size: 1.125rem;
    color: #333;
    margin-top: 0.5rem;
    font-weight: 500;
}

/* Confidence - Subtle */
.confidence-tag {
    display: inline-block;
    padding: 0.375rem 1rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.conf-high {
    background: #dcfce7;
    color: #166534;
    border: 1px solid #bbf7d0;
}

.conf-med {
    background: #fef3c7;
    color: #92400e;
    border: 1px solid #fde68a;
}

.conf-low {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

/* Data Grid */
.data-row {
    display: flex;
    padding: 0.875rem 0;
    border-bottom: 1px solid #f0f0f0;
}

.data-row:last-child {
    border-bottom: none;
}

.data-label {
    width: 140px;
    color: #666;
    font-size: 0.875rem;
    font-weight: 500;
}

.data-value {
    flex: 1;
    color: #1a1a1a;
    font-size: 0.875rem;
    font-weight: 600;
}

/* Code List */
.code-row {
    background: #f8f9fa;
    border-left: 3px solid #0066cc;
    padding: 1rem;
    margin-bottom: 0.75rem;
    border-radius: 0 4px 4px 0;
}

.code-num {
    font-family: monospace;
    font-size: 1rem;
    font-weight: 700;
    color: #0066cc;
    margin-bottom: 0.25rem;
}

.code-text {
    color: #333;
    font-size: 0.875rem;
    font-weight: 500;
}

.code-rationale {
    color: #666;
    font-size: 0.8rem;
    margin-top: 0.25rem;
}

/* Interactive Correction Panel - Clean */
.correct-panel {
    background: #ffffff;
    border: 2px solid #1a1a1a;
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 2rem;
}

.correct-header {
    font-size: 0.875rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Form Elements */
.stTextInput input, .stTextArea textarea {
    border: 1px solid #d0d0d0 !important;
    border-radius: 6px !important;
    background: #ffffff !important;
    color: #1a1a1a !important;
    font-size: 0.875rem !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #0066cc !important;
    box-shadow: 0 0 0 3px rgba(0,102,204,0.1) !important;
}

/* Buttons - Clean */
.stButton > button {
    background: #1a1a1a !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: #333 !important;
    transform: translateY(-1px);
}

.stButton > button[type="primary"] {
    background: #0066cc !important;
}

.stButton > button[type="primary"]:hover {
    background: #0052a3 !important;
}

/* Alerts - Clean */
.alert-box {
    background: #fef3c7;
    border-left: 4px solid #f59e0b;
    padding: 1rem;
    margin: 0.75rem 0;
    color: #92400e;
    font-size: 0.875rem;
}

.error-box {
    background: #fee2e2;
    border-left: 4px solid #ef4444;
    padding: 1rem;
    margin: 0.75rem 0;
    color: #991b1b;
    font-size: 0.875rem;
}

.success-box {
    background: #dcfce7;
    border-left: 4px solid #22c55e;
    padding: 1rem;
    margin: 0.75rem 0;
    color: #166534;
    font-size: 0.875rem;
}

/* Info Box */
.info-box {
    background: #f0f9ff;
    border-left: 4px solid #0066cc;
    padding: 1rem;
    margin: 0.75rem 0;
    color: #1a1a1a;
    font-size: 0.875rem;
}

/* Tabs - Clean */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #e5e5e5 !important;
    gap: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    color: #666 !important;
    font-weight: 500 !important;
    padding: 1rem 1.5rem !important;
    border-bottom: 2px solid transparent !important;
}

.stTabs [aria-selected="true"] {
    color: #0066cc !important;
    border-bottom-color: #0066cc !important;
    background: transparent !important;
}

/* Expander - Clean */
.streamlit-expanderHeader {
    background: #f8f9fa !important;
    border: 1px solid #e5e5e5 !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    color: #1a1a1a !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {
    visibility: hidden;
}

/* Metric - Clean */
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #1a1a1a !important;
}

[data-testid="stMetricLabel"] {
    color: #666 !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
}

/* File Uploader - Clean */
.stFileUploader {
    border: 2px dashed #d0d0d0 !important;
    border-radius: 8px !important;
    padding: 2rem !important;
}

.stFileUploader:hover {
    border-color: #0066cc !important;
    background: #f0f9ff !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f0f0f0;
}

::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #999;
}
</style>
""", unsafe_allow_html=True)

# API Configuration
NVIDIA_API_KEY = "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"
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-3.1-70b-instruct"

# Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "corrections" not in st.session_state:
    st.session_state.corrections = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "edited_result" not in st.session_state:
    st.session_state.edited_result = None

def call_api(prompt):
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3000,
        "temperature": 0.1,
        "stream": False
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    data = response.json()
    if "choices" not in data:
        raise Exception(f"API error")
    return data["choices"][0]["message"]["content"]

def extract_text_from_pdf(pdf_file):
    try:
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        return "".join([page.get_text() for page in doc])
    except Exception as e:
        return f"Error: {str(e)}"

def extract_text_from_image(image_file):
    try:
        image = Image.open(image_file)
        return pytesseract.image_to_string(image)
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_clinical_notes(clinical_text):
    prompt = f"""You are an expert Home Health ICD-10-CM Coding Specialist.

Analyze and return ONLY valid JSON:

{{
  "patient_name": "name or Not found",
  "patient_dob": "DOB or Not found", 
  "patient_age": "age or Not found",
  "patient_gender": "gender or Not found",
  "admission_date": "date or Not found",
  "discharge_date": "date or Not found",
  "face_to_face_date": "date or Not found",
  "attending_physician": "name or Not found",
  "pdx_code": "ICD-10 code",
  "pdx_description": "description",
  "pdx_rationale": "explanation",
  "confidence_score": "High/Medium/Low",
  "confidence_reason": "why",
  "secondary_codes": [{{"code": "", "description": "", "rationale": ""}}],
  "oasis_alerts": {{"face_to_face_missing": "Yes/No", "homebound_documentation_sufficient": "Yes/No"}},
  "coding_warnings": ["warning"],
  "change_in_condition": "description"
}}

Rules:
- PDx must be definitive (no Z, R, or history codes as primary)
- Aortoiliac bypass = I74.5 (not I70.2x)
- Code condition requiring surgery, not post-op status

Text: {clinical_text[:8000]}

Return JSON only:"""

    try:
        raw = call_api(prompt)
        cleaned = re.sub(r'```json|```', '', raw).strip()
        start, end = cleaned.find('{'), cleaned.rfind('}') + 1
        result = json.loads(cleaned[start:end])
        
        # Basic validation
        if result.get('pdx_code', '').startswith(('Z', 'R')):
            result['coding_warnings'] = result.get('coding_warnings', []) + ['Invalid: Symptom or status code as PDx']
            result['confidence_score'] = 'Low'
        
        return result
    except:
        return {
            "pdx_code": "ERROR",
            "pdx_description": "Failed to parse",
            "confidence_score": "Low",
            "coding_warnings": ["Analysis failed - please retry"]
        }

def generate_pdf(result):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("CareBridge Report", styles['Title'])]
    
    data = [
        ["Patient", result.get('patient_name', '')],
        ["PDx", f"{result.get('pdx_code', '')} - {result.get('pdx_description', '')}"],
        ["Confidence", result.get('confidence_score', '')]
    ]
    story.append(Table(data))
    doc.build(story)
    buffer.seek(0)
    return buffer

# Header
st.markdown('''
    <div class="main-header">
        <span class="logo-text">Care<span class="logo-accent">Bridge</span></span>
    </div>
''', unsafe_allow_html=True)

# Main Interface
tab1, tab2, tab3 = st.tabs(["Analyze", "History", "Help"])

with tab1:
    col_input, col_output = st.columns([1, 1.2])
    
    with col_input:
        st.markdown('<div class="section-title">Input</div>', unsafe_allow_html=True)
        
        with st.container():
            uploaded_pdfs = st.file_uploader("PDF", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
            uploaded_images = st.file_uploader("Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, label_visibility="collapsed")
            pasted_text = st.text_area("Clinical Notes", height=200, placeholder="Paste discharge summary here...", label_visibility="collapsed")
            
            all_text = ""
            if uploaded_pdfs:
                for pdf in uploaded_pdfs:
                    all_text += f"\n\n--- {pdf.name} ---\n{extract_text_from_pdf(pdf)}"
            if uploaded_images:
                for img in uploaded_images:
                    img.seek(0)
                    all_text += f"\n\n--- {img.name} ---\n{extract_text_from_image(img)}"
            if pasted_text:
                all_text += pasted_text
            
            if st.button("Analyze", type="primary", use_container_width=True, disabled=not all_text):
                with st.spinner("Analyzing..."):
                    result = analyze_clinical_notes(all_text)
                    result["analyzed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    result["source_text"] = all_text[:1000]
                    st.session_state.current_result = result
                    st.session_state.edited_result = None  # Reset any edits
                    st.session_state.history.append(result)
    
    with col_output:
        st.markdown('<div class="section-title">Results</div>', unsafe_allow_html=True)
        
        result = st.session_state.edited_result or st.session_state.current_result
        
        if result:
            # Confidence
            conf = result.get('confidence_score', 'Medium')
            conf_class = 'conf-high' if conf == 'High' else 'conf-low' if conf == 'Low' else 'conf-med'
            st.markdown(f'<div style="text-align: right; margin-bottom: 1rem;"><span class="confidence-tag {conf_class}">{conf} Confidence</span></div>', unsafe_allow_html=True)
            
            # PDx Display
            st.markdown(f'''
                <div class="pdx-box">
                    <div class="pdx-code">{result.get("pdx_code", "---")}</div>
                    <div class="pdx-desc">{result.get("pdx_description", "")}</div>
                </div>
            ''', unsafe_allow_html=True)
            
            # Patient Info
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                cols = st.columns(2)
                fields = [
                    ("Patient", result.get('patient_name')),
                    ("DOB", result.get('patient_dob')),
                    ("Admission", result.get('admission_date')),
                    ("Discharge", result.get('discharge_date')),
                    ("F2F Date", result.get('face_to_face_date')),
                    ("Attending", result.get('attending_physician'))
                ]
                for i, (label, value) in enumerate(fields):
                    with cols[i % 2]:
                        st.markdown(f'<div class="data-row"><span class="data-label">{label}</span><span class="data-value">{value or "---"}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Rationale
            with st.expander("Rationale"):
                st.markdown(f'<div class="info-box">{result.get("pdx_rationale", "No rationale")}</div>', unsafe_allow_html=True)
            
            # Secondary Codes
            secondary = result.get('secondary_codes', [])
            if secondary:
                st.markdown('<div class="section-title">Secondary Diagnoses</div>', unsafe_allow_html=True)
                for code in secondary:
                    st.markdown(f'''
                        <div class="code-row">
                            <div class="code-num">{code.get("code", "")}</div>
                            <div class="code-text">{code.get("description", "")}</div>
                            <div class="code-rationale">{code.get("rationale", "")}</div>
                        </div>
                    ''', unsafe_allow_html=True)
            
            # Warnings
            warnings = result.get('coding_warnings', [])
            if warnings:
                for w in warnings:
                    st.markdown(f'<div class="alert-box">⚠️ {w}</div>', unsafe_allow_html=True)
            
            # REAL-TIME INTERACTIVE CORRECTION - No API, Instant Update
            st.markdown('<div class="correct-panel">', unsafe_allow_html=True)
            st.markdown('<div class="correct-header">✏️ Correct This PDx</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                new_code = st.text_input("Correct ICD-10 Code", value=result.get('pdx_code', ''), key="edit_code")
            with col2:
                new_desc = st.text_input("Description", value=result.get('pdx_description', ''), key="edit_desc")
            
            new_rationale = st.text_area("Clinical Reasoning", value=result.get('pdx_rationale', ''), key="edit_rationale")
            
            col_apply, col_save = st.columns(2)
            
            with col_apply:
                if st.button("✓ Apply Correction (Instant)", use_container_width=True, type="primary"):
                    # INSTANT UPDATE - No API call, modifies result directly
                    edited = dict(result)
                    edited['pdx_code'] = new_code
                    edited['pdx_description'] = new_desc
                    edited['pdx_rationale'] = new_rationale + " [CORRECTED]"
                    edited['confidence_score'] = 'High'
                    edited['coding_warnings'] = edited.get('coding_warnings', []) + ['Manually corrected by user']
                    st.session_state.edited_result = edited
                    st.session_state.current_result = edited  # Update main result too
                    st.success("✓ Updated instantly!")
                    st.rerun()  # Refresh to show changes
            
            with col_save:
                if st.button("💾 Save for Future Learning", use_container_width=True):
                    correction = {
                        "wrong_code": result.get('pdx_code'),
                        "correct_code": new_code,
                        "context": result.get('source_text', '')[:200],
                        "reason": new_rationale,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.corrections.append(correction)
                    st.success("✓ Saved to learning database")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Export
            col_json, col_pdf = st.columns(2)
            with col_json:
                st.download_button("Download JSON", json.dumps(result, indent=2), "result.json", "application/json", use_container_width=True)
            with col_pdf:
                try:
                    st.download_button("Download PDF", generate_pdf(result), "result.pdf", "application/pdf", use_container_width=True)
                except:
                    st.button("PDF Error", disabled=True, use_container_width=True)
        
        else:
            st.markdown('<div style="text-align: center; padding: 4rem; color: #999;">Upload documents to begin analysis</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-title">Case History</div>', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("No cases yet")
    else:
        for i, case in enumerate(reversed(st.session_state.history[-10:])):
            with st.expander(f"{case.get('patient_name', 'Unknown')} | {case.get('pdx_code', '')} | {case.get('analyzed_at', '')}"):
                st.json(case)
                if st.button("Load This Case", key=f"load_{i}"):
                    st.session_state.current_result = case
                    st.session_state.edited_result = None
                    st.rerun()

with tab3:
    st.markdown('<div class="section-title">How to Use</div>', unsafe_allow_html=True)
    st.markdown("""
    **1. Upload** - PDF or images of clinical documents
    **2. Analyze** - AI extracts data and suggests PDx
    **3. Correct** - If wrong, edit code instantly (no re-analysis needed)
    **4. Save** - Store corrections to improve future results
    
    **Color Guide:**
    - Blue accent = Primary actions
    - Green = High confidence / Success
    - Yellow = Medium confidence / Warning
    - Red = Low confidence / Error
    """)

# Sidebar - Minimal
with st.sidebar:
    st.markdown('<div style="font-size: 0.875rem; font-weight: 600; color: #666; margin-bottom: 1rem;">STATISTICS</div>', unsafe_allow_html=True)
    st.metric("Total Cases", len(st.session_state.history))
    st.metric("Corrections", len(st.session_state.corrections))
    
    if st.session_state.corrections:
        st.markdown("---")
        st.markdown('<div style="font-size: 0.875rem; font-weight: 600; color: #666; margin-bottom: 1rem;">RECENT CORRECTIONS</div>', unsafe_allow_html=True)
        for c in list(st.session_state.corrections)[-3:]:
            st.markdown(f"`{c['wrong_code']}` → `{c['correct_code']}`")
