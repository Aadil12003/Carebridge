import streamlit as st
import pytesseract
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

st.set_page_config(page_title="CareBridge PDx Tool", layout="wide", initial_sidebar_state="collapsed")

# Professional Minimal CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', -apple-system, sans-serif; }

.stApp { background: #f5f5f7; }

/* Header */
.main-header {
    background: #ffffff;
    border-bottom: 1px solid #d1d1d6;
    padding: 1rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
}

.brand {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1c1c1e;
    letter-spacing: -0.02em;
}

.brand span { color: #007aff; }

/* Layout */
.main-grid {
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}

/* Input Panel */
.input-panel {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    height: fit-content;
}

.section-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6e6e73;
    margin-bottom: 0.75rem;
}

.stTextArea textarea {
    border: 1px solid #d1d1d6 !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    background: #fafafa !important;
}

.stButton > button[kind="primary"] {
    background: #007aff !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.875rem 1.5rem !important;
    font-weight: 600 !important;
    width: 100% !important;
}

/* Results Panel */
.results-panel {
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    overflow: hidden;
}

/* PDX Header */
.pdx-header {
    background: linear-gradient(135deg, #007aff 0%, #5856d6 100%);
    color: white;
    padding: 2rem;
    position: relative;
}

.pdx-code {
    font-family: 'SF Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    margin-bottom: 0.5rem;
}

.pdx-desc {
    font-size: 1.25rem;
    opacity: 0.9;
    font-weight: 500;
}

.confidence-badge {
    position: absolute;
    top: 1.5rem;
    right: 1.5rem;
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
}

/* Content Sections */
.content-section {
    padding: 1.5rem 2rem;
    border-bottom: 1px solid #f0f0f0;
}

.content-section:last-child { border-bottom: none; }

.section-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1c1c1e;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Data Grid */
.data-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}

.data-item {
    background: #f5f5f7;
    padding: 1rem;
    border-radius: 8px;
}

.data-label {
    font-size: 0.75rem;
    color: #6e6e73;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.data-value {
    font-size: 0.9375rem;
    color: #1c1c1e;
    font-weight: 600;
}

/* Code List */
.code-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.code-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #f5f5f7;
    border-radius: 8px;
    border-left: 4px solid #007aff;
}

.code-number {
    font-family: 'SF Mono', monospace;
    font-size: 1rem;
    font-weight: 700;
    color: #007aff;
    min-width: 100px;
}

.code-text {
    flex: 1;
    font-size: 0.9375rem;
    color: #1c1c1e;
}

.code-rationale {
    font-size: 0.875rem;
    color: #6e6e73;
    margin-top: 0.25rem;
}

/* Wound Care Card */
.wound-card {
    background: #fff5f5;
    border: 1px solid #ffcccc;
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}

.wound-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #d32f2f;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.wound-detail {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid #ffcccc;
    font-size: 0.875rem;
}

.wound-detail:last-child { border-bottom: none; }

/* Alerts */
.alert-box {
    background: #fff3e0;
    border-left: 4px solid #ff9800;
    padding: 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.75rem;
    font-size: 0.9375rem;
    color: #e65100;
}

.error-box {
    background: #ffebee;
    border-left: 4px solid #f44336;
    padding: 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.75rem;
    font-size: 0.9375rem;
    color: #c62828;
}

.info-box {
    background: #e3f2fd;
    border-left: 4px solid #2196f3;
    padding: 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.75rem;
    font-size: 0.9375rem;
    color: #1565c0;
}

/* Correction Panel */
.correction-panel {
    background: #f5f5f7;
    border: 2px solid #007aff;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1.5rem;
}

.correction-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1c1c1e;
    margin-bottom: 1rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 0 !important;
    border-bottom: 1px solid #d1d1d6;
}

.stTabs [data-baseweb="tab"] {
    color: #6e6e73 !important;
    font-weight: 500 !important;
    padding: 1rem 1.5rem !important;
    border-bottom: 2px solid transparent !important;
}

.stTabs [aria-selected="true"] {
    color: #007aff !important;
    border-bottom-color: #007aff !important;
}

/* Hide defaults */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Configuration
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
        "max_tokens": 4000,
        "temperature": 0.05,  # Very low for consistency
        "stream": False
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        data = response.json()
        if "choices" not in data:
            return None
        content = data["choices"][0]["message"]["content"]
        return content if content else None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def extract_text_from_pdf(pdf_file):
    try:
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_image(image_file):
    try:
        image = Image.open(image_file)
        return pytesseract.image_to_string(image)
    except Exception as e:
        return f"Error extracting image: {str(e)}"

def build_corrections_context():
    if not st.session_state.corrections:
        return ""
    context = "\n\nLEARNED CORRECTIONS FROM PREVIOUS CASES:\n"
    for c in st.session_state.corrections[-5:]:
        context += f"- When documentation shows: {c['context']}, use {c['correct_code']} not {c['wrong_code']}. Reason: {c['reason']}\n"
    return context

def validate_pdx_result(result, clinical_text):
    """Hardcoded validation rules for accuracy"""
    pdx = result.get('pdx_code', '')
    text_lower = clinical_text.lower()
    corrections_made = []
    
    # Rule 1: Aortoiliac/Aortobifemoral bypass cases
    if any(x in text_lower for x in ['aortoiliac', 'aortobifemoral', 'aorto-bifemoral']):
        if pdx in ['I70.201', 'I70.202', 'I70.203', 'I70.208', 'I70.209', 'I70.211', 'I70.212', 'I70.213', 'I70.218', 'I70.219', 'I70.2']:
            old_pdx = pdx
            result['pdx_code'] = 'I74.5'
            result['pdx_description'] = 'Embolism and thrombosis of iliac artery'
            result['pdx_rationale'] = f'CORRECTED from {old_pdx}: Aortoiliac occlusion requiring bypass indicates acute thrombosis/embolism at the iliac level (I74.5), not chronic native artery disease of extremities (I70.2x). I70.2x codes are for femoral/popliteal/tibial disease below the inguinal ligament.'
            result['confidence_score'] = 'High'
            result['validation_override'] = True
            corrections_made.append(f'Auto-corrected: {old_pdx} → I74.5')
    
    # Rule 2: Z-codes cannot be PDx
    if pdx.startswith('Z'):
        corrections_made.append(f'CRITICAL: Z-code {pdx} cannot be primary diagnosis in home health')
        result['confidence_score'] = 'Low'
    
    # Rule 3: R-codes (symptoms) cannot be PDx
    if pdx.startswith('R'):
        corrections_made.append(f'CRITICAL: Symptom code {pdx} cannot be primary without definitive diagnosis')
        result['confidence_score'] = 'Low'
    
    # Rule 4: History codes cannot be PDx
    if pdx.startswith('Z86') or pdx.startswith('Z87'):
        corrections_made.append(f'CRITICAL: History code {pdx} cannot be primary')
        result['confidence_score'] = 'Low'
    
    # Rule 5: Bilateral vs unilateral
    if 'bilateral' in text_lower and (pdx.endswith('1') or pdx.endswith('2')):
        corrections_made.append(f'WARNING: Unilateral code {pdx} used but documentation suggests bilateral disease')
    
    # Add corrections to warnings
    if corrections_made:
        result['coding_warnings'] = result.get('coding_warnings', []) + corrections_made
    
    return result

def analyze_clinical_notes(clinical_text):
    corrections_context = build_corrections_context()
    
    # Escape for JSON
    safe_text = clinical_text.replace("\\", "\\\\").replace('"', '\\"')
    
    prompt = f"""You are an expert Home Health ICD-10-CM Coding Specialist for OASIS and 485 coding with deep knowledge of PDGM payment model and CMS guidelines.

Analyze this clinical documentation and return ONLY valid JSON with no markdown.

{corrections_context}

REQUIRED JSON STRUCTURE:
{{
  "patient_name": "full name or Not found",
  "patient_dob": "DOB or Not found",
  "patient_age": "age or Not found",
  "patient_gender": "gender or Not found",
  "admission_date": "date or Not found",
  "discharge_date": "date or Not found",
  "face_to_face_date": "date or Not found",
  "attending_physician": "name or Not found",
  "referring_physician": "name or Not found",
  "qualifying_event": "event with date",
  "homebound_status": "evidence of homebound status",
  "change_in_condition": "specific symptoms/signs representing change",
  "pdx_code": "primary ICD-10-CM code - MUST be definitive diagnosis",
  "pdx_description": "official description",
  "pdx_rationale": "detailed explanation",
  "pdx_alternative": "alternative code or None",
  "confidence_score": "High/Medium/Low",
  "confidence_reason": "explanation",
  "secondary_codes": [
    {{"code": "ICD-10", "description": "desc", "rationale": "why included"}}
  ],
  "queries_needed": ["query topics"],
  "physician_query_letters": [
    {{"query_topic": "topic", "query_letter": "full letter text"}}
  ],
  "wound_care": {{
    "present": "Yes/No",
    "wound_type": "type",
    "location": "anatomical location",
    "stage": "stage",
    "size": "dimensions",
    "details": "description",
    "skilled_need": "interventions needed",
    "oasis_item": "M1300/M1302/M1306/M1307/M1308"
  }},
  "lab_draw": {{
    "present": "Yes/No",
    "details": "labs ordered",
    "high_risk_monitoring": "monitoring needed"
  }},
  "skilled_need": {{
    "service": "SN/PT/OT/ST/combination",
    "rationale": "justification",
    "frequency_suggestion": "visit frequency"
  }},
  "medications": {{
    "high_risk": "list",
    "medication_teaching_needed": "Yes/No",
    "reconciliation_needed": "Yes/No"
  }},
  "oasis_alerts": {{
    "m1033_hospitalization_risk": "High/Medium/Low",
    "m1240_pain_assessment": "details",
    "m1800_grooming": "level",
    "m1910_fall_risk": "Yes/No",
    "mental_health_flags": "flags",
    "face_to_face_missing": "Yes/No",
    "homebound_documentation_sufficient": "Yes/No"
  }},
  "therapy_needs": {{
    "pt_indicated": "Yes/No with deficits",
    "ot_indicated": "Yes/No with deficits",
    "st_indicated": "Yes/No with deficits"
  }},
  "coding_warnings": ["warnings"],
  "pdgm_considerations": {{
    "clinical_group": "PDGM group",
    "comorbidity_adjustment": "adjustment",
    "functional_impairment": "level"
  }},
  "documentation_gaps": ["gaps"]
}}

CRITICAL RULES:
1. PDx must be definitive - NO Z-codes, NO R-codes, NO history codes as primary
2. Aortoiliac/aortobifemoral bypass = I74.5 (NOT I70.2x)
3. Code condition requiring surgery, NOT post-op status
4. Use highest specificity
5. Wound care must include OASIS item (M1300, M1302, M1306, M1307, M1308)
6. Include all 12 PDGM clinical group considerations

Clinical documentation:
{safe_text[:10000]}

Return ONLY valid JSON:"""

    raw = call_api(prompt)
    if not raw:
        return fallback_result(clinical_text)
    
    try:
        cleaned = re.sub(r'```json|```', '', raw).strip()
        start = cleaned.find('{')
        end = cleaned.rfind('}') + 1
        
        if start == -1 or end <= start:
            return fallback_result(clinical_text, raw)
        
        cleaned = cleaned[start:end]
        result = json.loads(cleaned)
        
        # Ensure all required fields exist
        required_fields = ['patient_name', 'pdx_code', 'pdx_description', 'secondary_codes', 
                          'wound_care', 'lab_draw', 'skilled_need', 'medications', 
                          'oasis_alerts', 'therapy_needs', 'coding_warnings', 'change_in_condition']
        for field in required_fields:
            if field not in result:
                result[field] = {} if field in ['wound_care', 'lab_draw', 'skilled_need', 'medications', 'oasis_alerts', 'therapy_needs', 'pdgm_considerations'] else []
        
        # Apply hardcoded validation
        result = validate_pdx_result(result, clinical_text)
        
        result['raw_api_response'] = raw[:500]
        return result
        
    except Exception as e:
        return fallback_result(clinical_text, raw)

def fallback_result(text, raw=None):
    """When API fails"""
    return {
        "patient_name": "Parse Error",
        "pdx_code": "ERROR",
        "pdx_description": "API parsing failed - manual review required",
        "confidence_score": "Low",
        "confidence_reason": "System error",
        "pdx_rationale": "The AI failed to return valid JSON. Please check the raw response.",
        "secondary_codes": [],
        "wound_care": {"present": "No"},
        "lab_draw": {"present": "No"},
        "skilled_need": {"service": "Unknown"},
        "medications": {},
        "oasis_alerts": {},
        "therapy_needs": {},
        "coding_warnings": ["SYSTEM ERROR: Manual coding required"],
        "change_in_condition": "Not parsed",
        "raw_api_response": raw[:500] if raw else "No response"
    }

def generate_pdf_report(result):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('title', parent=styles['Title'], fontSize=18, textColor=colors.HexColor('#007aff'))
    header_style = ParagraphStyle('header', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#1c1c1e'))
    body_style = ParagraphStyle('body', parent=styles['Normal'], fontSize=10, spaceAfter=6)
    
    story.append(Paragraph("CareBridge Home Health PDx Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Patient Info
    story.append(Paragraph("Patient Information", header_style))
    patient_data = [
        ["Name", result.get('patient_name', 'Not found')],
        ["DOB", result.get('patient_dob', 'Not found')],
        ["Admission", result.get('admission_date', 'Not found')],
        ["Discharge", result.get('discharge_date', 'Not found')],
        ["F2F Date", result.get('face_to_face_date', 'Not found')]
    ]
    t = Table(patient_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f7')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))
    
    # PDx
    story.append(Paragraph("Primary Diagnosis", header_style))
    story.append(Paragraph(f"<b>{result.get('pdx_code', '')}</b> - {result.get('pdx_description', '')}", body_style))
    story.append(Paragraph(f"Rationale: {result.get('pdx_rationale', '')}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Secondary
    secondary = result.get('secondary_codes', [])
    if secondary:
        story.append(Paragraph("Secondary Diagnoses", header_style))
        for code in secondary:
            story.append(Paragraph(f"• {code.get('code', '')} - {code.get('description', '')}", body_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def render_results(result):
    # Validation override notice
    if result.get('validation_override'):
        st.markdown(f'''
            <div class="alert-box">
                <strong>⚠️ Auto-Corrected:</strong> {result.get('pdx_rationale', '')[:200]}...
            </div>
        ''', unsafe_allow_html=True)
    
    # PDX Header
    conf_color = {'High': '#34c759', 'Medium': '#ff9500', 'Low': '#ff3b30'}.get(result.get('confidence_score', 'Medium'), '#ff9500')
    st.markdown(f'''
        <div class="pdx-header">
            <div class="pdx-code">{result.get("pdx_code", "---")}</div>
            <div class="pdx-desc">{result.get("pdx_description", "")}</div>
            <div class="confidence-badge" style="color: {conf_color};">
                ● {result.get("confidence_score", "Medium")} Confidence
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Patient Info
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 Patient Information</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="data-grid">
            <div class="data-item">
                <div class="data-label">Patient</div>
                <div class="data-value">{result.get("patient_name", "Not found")}</div>
            </div>
            <div class="data-item">
                <div class="data-label">DOB / Age</div>
                <div class="data-value">{result.get("patient_dob", "---")} ({result.get("patient_age", "---")})</div>
            </div>
            <div class="data-item">
                <div class="data-label">Admission</div>
                <div class="data-value">{result.get("admission_date", "---")}</div>
            </div>
            <div class="data-item">
                <div class="data-label">Discharge</div>
                <div class="data-value">{result.get("discharge_date", "---")}</div>
            </div>
            <div class="data-item">
                <div class="data-label">F2F Date</div>
                <div class="data-value" style="color: {"#ff3b30" if result.get("face_to_face_date") == "Not found" else "#1c1c1e"};">
                    {result.get("face_to_face_date", "Not found")}
                </div>
            </div>
            <div class="data-item">
                <div class="data-label">Attending</div>
                <div class="data-value">{result.get("attending_physician", "---")}</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Change in Condition
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Change in Condition</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-box">{result.get("change_in_condition", "Not documented")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Rationale
    with st.expander("📖 View Full Rationale"):
        st.markdown(f'<div style="font-size: 0.9375rem; line-height: 1.6;">{result.get("pdx_rationale", "No rationale")}</div>', unsafe_allow_html=True)
        if result.get('pdx_alternative') and result.get('pdx_alternative') != "None":
            st.markdown(f'<div style="margin-top: 1rem; padding: 1rem; background: #f5f5f7; border-radius: 8px;"><strong>Alternative:</strong> {result.get("pdx_alternative")}</div>', unsafe_allow_html=True)
    
    # Secondary Codes
    secondary = result.get("secondary_codes", [])
    if secondary:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Secondary Diagnoses</div>', unsafe_allow_html=True)
        for code in secondary:
            st.markdown(f'''
                <div class="code-item">
                    <span class="code-number">{code.get("code", "")}</span>
                    <div>
                        <div class="code-text">{code.get("description", "")}</div>
                        <div class="code-rationale">{code.get("rationale", "")}</div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # PDGM
    pdgm = result.get("pdgm_considerations", {})
    if pdgm:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💰 PDGM Considerations</div>', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">Clinical Group</div>
                    <div class="data-value">{pdgm.get("clinical_group", "---")}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Comorbidity Adjustment</div>
                    <div class="data-value">{pdgm.get("comorbidity_adjustment", "---")}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Functional Impairment</div>
                    <div class="data-value">{pdgm.get("functional_impairment", "---")}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Wound Care
    wound = result.get("wound_care", {})
    if wound.get("present") == "Yes":
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🩹 Wound Care</div>', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="wound-card">
                <div class="wound-title">⚠️ Active Wound Management Required</div>
                <div class="wound-detail"><span>Type</span><span>{wound.get("wound_type", "---")}</span></div>
                <div class="wound-detail"><span>Location</span><span>{wound.get("location", "---")}</span></div>
                <div class="wound-detail"><span>Stage</span><span>{wound.get("stage", "---")}</span></div>
                <div class="wound-detail"><span>Size</span><span>{wound.get("size", "---")}</span></div>
                <div class="wound-detail"><span>OASIS Item</span><span style="color: #007aff; font-weight: 600;">{wound.get("oasis_item", "---")}</span></div>
                <div class="wound-detail"><span>Skilled Need</span><span>{wound.get("skilled_need", "---")}</span></div>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Lab Draw
    lab = result.get("lab_draw", {})
    if lab.get("present") == "Yes":
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🧪 Lab Monitoring</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">{lab.get("details", "Labs ordered")}<br><strong>High Risk Monitoring:</strong> {lab.get("high_risk_monitoring", "")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Medications
    meds = result.get("medications", {})
    if meds:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💊 Medications</div>', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">High Risk Medications</div>
                    <div class="data-value">{meds.get("high_risk", "None")}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Teaching Needed</div>
                    <div class="data-value">{meds.get("medication_teaching_needed", "---")}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Skilled Need
    skilled = result.get("skilled_need", {})
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏥 Skilled Need</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="data-grid">
            <div class="data-item">
                <div class="data-label">Service</div>
                <div class="data-value">{skilled.get("service", "---")}</div>
            </div>
            <div class="data-item">
                <div class="data-label">Frequency</div>
                <div class="data-value">{skilled.get("frequency_suggestion", "---")}</div>
            </div>
        </div>
        <div style="margin-top: 1rem; padding: 1rem; background: #f5f5f7; border-radius: 8px; font-size: 0.9375rem;">
            <strong>Rationale:</strong> {skilled.get("rationale", "No rationale")}
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Therapy
    therapy = result.get("therapy_needs", {})
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏃 Therapy Assessment</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    with cols[0]:
        st.metric("PT", therapy.get("pt_indicated", "No")[:3])
    with cols[1]:
        st.metric("OT", therapy.get("ot_indicated", "No")[:3])
    with cols[2]:
        st.metric("ST", therapy.get("st_indicated", "No")[:3])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # OASIS Alerts
    oasis = result.get("oasis_alerts", {})
    alerts = []
    if oasis.get("face_to_face_missing") == "Yes":
        alerts.append("⚠️ Face-to-face encounter date missing")
    if oasis.get("homebound_documentation_sufficient") == "No":
        alerts.append("⚠️ Homebound status insufficiently documented")
    
    if alerts:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🚨 OASIS Compliance Alerts</div>', unsafe_allow_html=True)
        for alert in alerts:
            st.markdown(f'<div class="error-box">{alert}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # OASIS Summary
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 OASIS Assessment</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="data-grid">
            <div class="data-item">
                <div class="data-label">M1033 Hospitalization Risk</div>
                <div class="data-value">{oasis.get("m1033_hospitalization_risk", "---")}</div>
            </div>
            <div class="data-item">
                <div class="data-label">M1240 Pain</div>
                <div class="data-value">{oasis.get("m1240_pain_assessment", "---")}</div>
            </div>
            <div class="data-item">
                <div class="data-label">M1910 Fall Risk</div>
                <div class="data-value">{oasis.get("m1910_fall_risk", "---")}</div>
            </div>
            <div class="data-item">
                <div class="data-label">Mental Health</div>
                <div class="data-value">{oasis.get("mental_health_flags", "---")}</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Warnings
    warnings = [w for w in result.get("coding_warnings", []) if not w.startswith("Auto-corrected")]
    if warnings:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚠️ Coding Warnings</div>', unsafe_allow_html=True)
        for w in warnings:
            st.markdown(f'<div class="alert-box">{w}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Queries
    queries = result.get("queries_needed", [])
    if queries:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">❓ Physician Queries Needed</div>', unsafe_allow_html=True)
        for q in queries:
            st.markdown(f'<div class="alert-box">🔍 {q}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # REAL-TIME INTERACTIVE CORRECTION
    st.markdown('<div class="content-section" style="background: #f5f5f7;">', unsafe_allow_html=True)
    st.markdown('<div class="correction-panel">', unsafe_allow_html=True)
    st.markdown('<div class="correction-title">✏️ Interactive Correction & Learning</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fix_code = st.text_input("Correct PDx Code", value=result.get("pdx_code", ""), key="fix_code")
    with col2:
        fix_desc = st.text_input("Correct Description", value=result.get("pdx_description", ""), key="fix_desc")
    
    fix_reason = st.text_area("Clinical Reasoning for Change", placeholder="Explain why this is the correct code based on documentation...", key="fix_reason")
    
    col_apply, col_save = st.columns([1, 1])
    
    with col_apply:
        if st.button("✓ Apply Instantly", use_container_width=True, type="primary"):
            # INSTANT UPDATE - Modify result directly, no API
            result["pdx_code"] = fix_code
            result["pdx_description"] = fix_desc
            result["pdx_rationale"] = f"[USER CORRECTED] {fix_reason}\n\nOriginal: {result.get('pdx_code')}"
            result["confidence_score"] = "High"
            result["user_corrected"] = True
            st.session_state.edited_result = result
            st.session_state.current_result = result
            st.success("✓ Updated instantly!")
            st.rerun()
    
    with col_save:
        if st.button("💾 Save & Teach AI", use_container_width=True):
            if fix_code and fix_reason:
                # Save to learning database
                correction = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "wrong_code": result.get("pdx_code"),
                    "correct_code": fix_code,
                    "wrong_desc": result.get("pdx_description"),
                    "correct_desc": fix_desc,
                    "reason": fix_reason,
                    "context": result.get("change_in_condition", "")[:200],
                    "clinical_group": result.get("pdgm_considerations", {}).get("clinical_group", "")
                }
                st.session_state.corrections.append(correction)
                
                # Apply correction
                result["pdx_code"] = fix_code
                result["pdx_description"] = fix_desc
                result["pdx_rationale"] = f"[LEARNED CORRECTION] {fix_reason}"
                result["confidence_score"] = "High"
                result["ai_learning_note"] = "This correction will be applied to similar future cases"
                st.session_state.current_result = result
                st.success("✓ Saved! AI will learn this pattern.")
                st.balloons()
                st.rerun()
    
    # Show learning history
    if st.session_state.corrections:
        with st.expander(f"🧠 AI Learning History ({len(st.session_state.corrections)} corrections)"):
            for corr in reversed(st.session_state.corrections[-5:]):
                st.caption(f"{corr['timestamp']}: {corr['wrong_code']} → {corr['correct_code']}")
                st.text(f"Reason: {corr['reason'][:100]}...")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export
    st.markdown('<div class="content-section" style="background: #f5f5f7;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📥 Export</div>', unsafe_allow_html=True)
    col_json, col_pdf = st.columns(2)
    with col_json:
        st.download_button("Download JSON", json.dumps(result, indent=2, default=str), 
                          f"pdx_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 
                          "application/json", use_container_width=True)
    with col_pdf:
        try:
            pdf_buf = generate_pdf_report(result)
            st.download_button("Download PDF", pdf_buf, 
                              f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", 
                              "application/pdf", use_container_width=True)
        except:
            st.button("PDF Error", disabled=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Header
st.markdown('''
    <div class="main-header">
        <div class="brand">Care<span>Bridge</span> Clinical Intelligence</div>
    </div>
''', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🔄 New Analysis", "📚 History", "❓ Help"])

with tab1:
    col_input, col_output = st.columns([1, 2])
    
    with col_input:
        st.markdown('<div class="input-panel">', unsafe_allow_html=True)
        
        st.markdown('<div class="section-label">Upload Documents</div>', unsafe_allow_html=True)
        pdfs = st.file_uploader("PDF files", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
        imgs = st.file_uploader("Image files", type=["png", "jpg", "jpeg"], accept_multiple_files=True, label_visibility="collapsed")
        
        st.markdown('<div class="section-label" style="margin-top: 1rem;">Clinical Notes</div>', unsafe_allow_html=True)
        text = st.text_area("", height=150, placeholder="Paste discharge summary, progress notes, or clinical documentation here...", label_visibility="collapsed")
        
        # Compile
        full_text = text or ""
        for p in (pdfs or []):
            full_text += f"\n\n[PDF: {p.name}]\n{extract_text_from_pdf(p)}"
        for i in (imgs or []):
            i.seek(0)
            full_text += f"\n\n[IMG: {i.name}]\n{extract_text_from_image(i)}"
        
        if st.button("Analyze with AI", type="primary", disabled=not full_text.strip()):
            with st.spinner("Analyzing clinical documentation..."):
                result = analyze_clinical_notes(full_text)
                result["analyzed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                result["source_text"] = full_text[:500]
                st.session_state.current_result = result
                st.session_state.edited_result = None
                st.session_state.history.append(result)
                st.rerun()
        
        if st.session_state.corrections:
            st.markdown(f'<div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #d1d1d6; font-size: 0.875rem; color: #6e6e73;"><strong>{len(st.session_state.corrections)}</strong> corrections in AI learning database</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_output:
        result = st.session_state.edited_result or st.session_state.current_result
        
        if result:
            st.markdown('<div class="results-panel">', unsafe_allow_html=True)
            render_results(result)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div class="results-panel" style="display: flex; align-items: center; justify-content: center; height: 600px; color: #6e6e73;">
                    <div style="text-align: center;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
                        <div style="font-size: 1.125rem; font-weight: 500; color: #1c1c1e; margin-bottom: 0.5rem;">Ready to Analyze</div>
                        <div style="font-size: 0.9375rem;">Upload documents or paste clinical notes to begin</div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

with tab2:
    st.markdown('<div style="max-width: 900px;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Case History</div>', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("No cases analyzed yet.")
    else:
        for i, case in enumerate(reversed(st.session_state.history[-10:])):
            with st.expander(f"{case.get('patient_name', 'Unknown')} | {case.get('pdx_code', '---')} | {case.get('analyzed_at', '')} {'✓' if case.get('user_corrected') else ''}"):
                st.json(case)
                if st.button("Load This Case", key=f"load_{i}"):
                    st.session_state.current_result = case
                    st.session_state.edited_result = None
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div style="max-width: 800px;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">How to Use CareBridge</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 1. Upload Clinical Documents
    - PDF discharge summaries
    - Photos of documents (OCR enabled)
    - Direct text paste from EHR
    
    ### 2. AI Analysis
    - Automatic PDx suggestion with confidence score
    - Secondary diagnoses with PDGM value
    - Wound care assessment with OASIS items
    - Lab draw identification
    - Therapy needs assessment
    - OASIS compliance alerts
    
    ### 3. Interactive Correction
    If the AI suggests wrong code:
    1. Enter correct ICD-10 code
    2. Explain clinical reasoning
    3. **Apply Instantly** - Updates result immediately
    4. **Save & Teach AI** - AI learns for future cases
    
    ### 4. Export
    - JSON for EHR integration
    - PDF report for physicians
    
    ### Color Guide
    - **Green dot** = High confidence
    - **Orange dot** = Medium confidence (review suggested)
    - **Red dot** = Low confidence (manual review required)
    
    ### Critical Coding Rules (Auto-Applied)
    - **Aortoiliac bypass** → I74.5 (not I70.2x)
    - **Z-codes** cannot be primary
    - **Symptom codes (R)** cannot be primary
    - **History codes** cannot be primary
    """)
    st.markdown('</div>', unsafe_allow_html=True)
