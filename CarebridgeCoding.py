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

# Premium Dark Theme Configuration
st.set_page_config(
    page_title="CareBridge AI | Clinical Intelligence Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS with Fixed Contrast and Visibility
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --secondary: #ec4899;
    --accent: #06b6d4;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --bg-dark: #0f172a;
    --bg-card: rgba(30, 41, 59, 0.85);
    --bg-glass: rgba(15, 23, 42, 0.6);
    --text-primary: #f1f5f9;
    --text-secondary: #cbd5e1;
    --text-muted: #94a3b8;
    --border: rgba(148, 163, 184, 0.2);
    --shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    --glow: 0 0 40px rgba(99, 102, 241, 0.3);
}

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    background-attachment: fixed;
}

/* Animated Background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(236, 72, 153, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(6, 182, 212, 0.1) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

/* Glassmorphism Header */
.main-header {
    background: rgba(30, 41, 59, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}

.logo-text {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}

.tagline {
    color: var(--text-secondary);
    font-size: 1.1rem;
    font-weight: 400;
    margin-top: 0.5rem;
}

/* Glass Cards - FIXED VISIBILITY */
.glass-card {
    background: rgba(30, 41, 59, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--glow), var(--shadow);
    border-color: rgba(99, 102, 241, 0.4);
}

/* Section Headers - FIXED */
.section-header {
    font-size: 0.875rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-primary);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.section-header::before {
    content: '';
    width: 4px;
    height: 16px;
    background: linear-gradient(180deg, var(--primary), var(--secondary));
    border-radius: 2px;
}

/* PDx Display - ENHANCED VISIBILITY */
.pdx-display {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(236, 72, 153, 0.3) 100%);
    border: 2px solid rgba(99, 102, 241, 0.5);
    border-radius: 20px;
    padding: 2.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.5rem;
}

.pdx-display::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.2) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 0.8; }
}

.pdx-code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3.5rem;
    font-weight: 800;
    color: #ffffff;
    text-shadow: 0 0 30px rgba(99, 102, 241, 0.8), 0 0 60px rgba(99, 102, 241, 0.4);
    position: relative;
    z-index: 1;
    letter-spacing: -0.02em;
}

.pdx-description {
    font-size: 1.25rem;
    color: var(--text-primary);
    margin-top: 0.75rem;
    font-weight: 500;
    position: relative;
    z-index: 1;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

/* Confidence Badges - FIXED */
.confidence-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #ffffff !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.confidence-high {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    border: 2px solid #34d399;
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.4), inset 0 1px 0 rgba(255,255,255,0.2);
}

.confidence-medium {
    background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
    border: 2px solid #fbbf24;
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.4), inset 0 1px 0 rgba(255,255,255,0.2);
}

.confidence-low {
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    border: 2px solid #f87171;
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.4), inset 0 1px 0 rgba(255,255,255,0.2);
}

/* Status Items - FIXED VISIBILITY */
.status-item {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: all 0.2s;
    margin-bottom: 0.75rem;
}

.status-item:hover {
    background: rgba(99, 102, 241, 0.15);
    border-color: rgba(99, 102, 241, 0.4);
}

.status-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    background: rgba(99, 102, 241, 0.2);
    border: 1px solid rgba(99, 102, 241, 0.3);
}

.status-content {
    flex: 1;
}

.status-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}

.status-value {
    font-size: 1rem;
    color: var(--text-primary);
    font-weight: 600;
    margin-top: 0.25rem;
}

/* Alert Cards - FIXED */
.alert-card {
    background: rgba(239, 68, 68, 0.15);
    border: 2px solid rgba(239, 68, 68, 0.4);
    border-radius: 12px;
    padding: 1.25rem;
    margin: 0.75rem 0;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    color: var(--text-primary);
    font-weight: 500;
}

.alert-card::before {
    content: '⚠️';
    font-size: 1.5rem;
    flex-shrink: 0;
}

.warning-card {
    background: rgba(245, 158, 11, 0.15);
    border: 2px solid rgba(245, 158, 11, 0.4);
    border-radius: 12px;
    padding: 1.25rem;
    margin: 0.75rem 0;
    color: var(--text-primary);
    font-weight: 500;
}

.info-card {
    background: rgba(6, 182, 212, 0.15);
    border: 2px solid rgba(6, 182, 212, 0.4);
    border-radius: 12px;
    padding: 1.25rem;
    margin: 0.75rem 0;
    color: var(--text-primary);
    font-weight: 500;
}

.success-card {
    background: rgba(16, 185, 129, 0.15);
    border: 2px solid rgba(16, 185, 129, 0.4);
    border-radius: 12px;
    padding: 1.25rem;
    margin: 0.75rem 0;
    color: var(--text-primary);
    font-weight: 500;
}

/* Code Items - FIXED */
.code-item {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    transition: all 0.2s;
    margin-bottom: 0.75rem;
}

.code-item:hover {
    border-color: rgba(99, 102, 241, 0.5);
    transform: translateX(4px);
    background: rgba(99, 102, 241, 0.1);
}

.code-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.25rem;
    font-weight: 700;
    color: #ffffff;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    padding: 0.5rem 1rem;
    border-radius: 8px;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    flex-shrink: 0;
}

.code-details {
    flex: 1;
    margin-left: 1rem;
}

.code-title {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 0.25rem;
}

.code-rationale {
    color: var(--text-secondary);
    font-size: 0.875rem;
    line-height: 1.5;
}

/* Auto-correction Notice - FIXED */
.auto-correct {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(239, 68, 68, 0.25) 100%);
    border: 2px solid rgba(245, 158, 11, 0.5);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    animation: slideIn 0.5s ease-out;
    color: var(--text-primary);
    font-weight: 600;
    font-size: 1rem;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Interactive Correction Panel - NEW */
.correction-panel {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%);
    border: 2px solid rgba(99, 102, 241, 0.4);
    border-radius: 20px;
    padding: 2rem;
    margin-top: 2rem;
    position: relative;
}

.correction-panel::before {
    content: '✏️ LIVE CORRECTION';
    position: absolute;
    top: -12px;
    left: 2rem;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
}

.correction-history {
    background: rgba(15, 23, 42, 0.6);
    border-radius: 12px;
    padding: 1rem;
    margin-top: 1rem;
    max-height: 300px;
    overflow-y: auto;
}

.correction-item {
    background: rgba(99, 102, 241, 0.1);
    border-left: 4px solid var(--primary);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    transition: all 0.2s;
}

.correction-item:hover {
    background: rgba(99, 102, 241, 0.2);
    transform: translateX(4px);
}

.correction-item .code-change {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
}

.correction-item .code-change .arrow {
    color: var(--secondary);
    margin: 0 0.5rem;
}

.correction-item .meta {
    color: var(--text-muted);
    font-size: 0.875rem;
    margin-top: 0.5rem;
}

/* Query Cards - FIXED */
.query-card {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(245, 158, 11, 0.15) 100%);
    border: 2px solid rgba(239, 68, 68, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 0.75rem 0;
    position: relative;
    overflow: hidden;
    color: var(--text-primary);
    font-weight: 500;
}

.query-card::before {
    content: '🔍';
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 2rem;
    opacity: 0.2;
}

/* Sidebar - NEW INTERACTIVE SPACE */
.css-1d391kg, .css-163ttbj, [data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border-right: 1px solid var(--border);
}

.sidebar-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Buttons - ENHANCED */
.stButton > button {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.875rem 1.5rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.025em !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    transition: all 0.3s !important;
    position: relative !important;
    overflow: hidden !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6), inset 0 1px 0 rgba(255,255,255,0.2) !important;
}

/* Form Elements - FIXED */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 2px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
}

/* Expander - FIXED */
.streamlit-expanderHeader {
    background: rgba(15, 23, 42, 0.8) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

/* Tabs - FIXED */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15, 23, 42, 0.6) !important;
    border-radius: 12px !important;
    padding: 0.5rem !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
    color: white !important;
    border-radius: 8px !important;
}

/* Metrics - FIXED */
[data-testid="stMetricValue"] {
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: var(--bg-dark);
}

::-webkit-scrollbar-thumb {
    background: var(--primary);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--secondary);
}

/* Hide Streamlit Elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Animation */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-in {
    animation: fadeInUp 0.6s ease-out;
}

/* Comparison Cards */
.comparison-card {
    background: rgba(15, 23, 42, 0.8);
    border-radius: 16px;
    padding: 1.5rem;
    border: 2px solid var(--border);
    color: var(--text-primary);
}

.comparison-card.highlight {
    border-color: var(--primary);
    box-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
}

/* History Items */
.history-item {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin: 0.5rem 0;
    transition: all 0.2s;
    cursor: pointer;
    color: var(--text-primary);
}

.history-item:hover {
    border-color: var(--primary);
    transform: translateX(4px);
    background: rgba(99, 102, 241, 0.1);
}

/* Responsive */
@media (max-width: 768px) {
    .logo-text { font-size: 1.75rem; }
    .pdx-code { font-size: 2.5rem; }
}
</style>
""", unsafe_allow_html=True)

NVIDIA_API_KEY = "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"
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-3.1-70b-instruct"

if "history" not in st.session_state:
    st.session_state.history = []
if "corrections" not in st.session_state:
    st.session_state.corrections = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "comparison_cases" not in st.session_state:
    st.session_state.comparison_cases = []
if "show_correction_panel" not in st.session_state:
    st.session_state.show_correction_panel = False

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
        raise Exception(f"API error: {json.dumps(data)}")
    content = data["choices"][0]["message"]["content"]
    if not content:
        raise Exception("API returned empty response")
    return content

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
    context = "\n\nLEARNED CORRECTIONS FROM PREVIOUS CASES - APPLY THESE:\n"
    for c in st.session_state.corrections[-10:]:  # Last 10 corrections
        context += f"- When documentation shows: {c['context']}, the correct PDx is {c['correct_code']} not {c['wrong_code']}. Reason: {c['reason']}\n"
    return context

def validate_pdx_result(result, clinical_text):
    """Validate and correct common PDx errors with clinical logic"""
    
    pdx = result.get('pdx_code', '')
    pdx_desc = result.get('pdx_description', '')
    text_lower = clinical_text.lower()
    corrections_made = []
    
    # Rule 1: Aortoiliac/Aortobifemoral bypass cases
    if 'aortoiliac' in text_lower or 'aortobifemoral' in text_lower or ('bypass' in text_lower and 'aorto' in text_lower):
        if pdx in ['I70.201', 'I70.202', 'I70.203', 'I70.208', 'I70.209', 'I70.211', 'I70.212', 'I70.213', 'I70.218', 'I70.219']:
            old_pdx = pdx
            result['pdx_code'] = 'I74.5'
            result['pdx_description'] = 'Embolism and thrombosis of iliac artery'
            result['pdx_rationale'] = f'CORRECTED from {old_pdx}: Aortoiliac occlusion requiring bypass indicates acute thrombosis/embolism at the iliac level (I74.5), not chronic native artery disease of extremities (I70.2x). I70.2x codes are for femoral/popliteal/tibial disease below the inguinal ligament. The aortoiliac segment is coded with I74.x.'
            result['confidence_score'] = 'High'
            corrections_made.append(f'Auto-corrected: {old_pdx} → I74.5 (aortoiliac level disease requires I74.x, not I70.2x)')
            
            if result.get('pdx_alternative') in [None, 'None', '']:
                result['pdx_alternative'] = old_pdx
    
    # Rule 2: Z-codes cannot be PDx in home health
    if pdx.startswith('Z'):
        corrections_made.append(f'CRITICAL: Z-code {pdx} suggested as PDx - Z-codes cannot be primary in home health per CMS guidelines')
        result['confidence_score'] = 'Low'
    
    # Rule 3: Symptom codes (R-codes) cannot be PDx
    if pdx.startswith('R'):
        corrections_made.append(f'CRITICAL: R-code {pdx} (symptom) suggested as PDx - symptoms cannot be primary unless no definitive diagnosis exists')
        result['confidence_score'] = 'Low'
    
    # Rule 4: History codes cannot be PDx
    if pdx.startswith('Z86') or pdx.startswith('Z87') or 'history' in pdx_desc.lower():
        corrections_made.append(f'CRITICAL: History code {pdx} suggested as PDx - history codes cannot be primary')
        result['confidence_score'] = 'Low'
    
    # Rule 5: Bilateral vs unilateral check
    if 'bilateral' in text_lower or 'right and left' in text_lower:
        if pdx.endswith('1') or pdx.endswith('2'):
            corrections_made.append(f'WARNING: Unilateral code {pdx} used but documentation suggests bilateral disease - consider unspecified or bilateral code')
    
    # Add corrections to warnings
    if corrections_made:
        result['coding_warnings'] = result.get('coding_warnings', []) + corrections_made
    
    if result.get('confidence_score') not in ['High', 'Medium', 'Low']:
        result['confidence_score'] = 'Medium'
    
    return result

def analyze_clinical_notes(clinical_text):
    corrections_context = build_corrections_context()
    safe_text = clinical_text.replace("\\", "\\\\").replace('"', '\\"')

    prompt = f"""You are an expert Home Health ICD-10-CM Coding Specialist for OASIS and 485 coding with deep knowledge of PDGM payment model and all CMS guidelines.

Analyze this clinical documentation completely and return ONLY a valid JSON object with no markdown and no explanation.
{corrections_context}

JSON SCHEMA:
{{
  "patient_name": "full name from document or Not found",
  "patient_dob": "date of birth or Not found",
  "patient_age": "age or Not found",
  "patient_gender": "gender or Not found",
  "admission_date": "hospital admission date or Not found",
  "discharge_date": "hospital discharge date or Not found",
  "face_to_face_date": "face to face encounter date or Not found",
  "attending_physician": "attending physician full name and credentials or Not found",
  "referring_physician": "referring physician name or Not found",
  "qualifying_event": "exact qualifying event with date",
  "homebound_status": "specific evidence patient is homebound with quotes from notes",
  "change_in_condition": "specific symptoms and signs representing change in condition",
  "pdx_code": "primary ICD-10-CM code with highest specificity - MUST be definitive diagnosis",
  "pdx_description": "full official description of PDx code",
  "pdx_rationale": "detailed explanation of why this is correct PDx",
  "pdx_alternative": "alternative code if ambiguous or None",
  "confidence_score": "High or Medium or Low",
  "confidence_reason": "why this confidence level was assigned",
  "secondary_codes": [
    {{"code": "ICD-10-CM code", "description": "full description", "rationale": "why included and PDGM value"}}
  ],
  "queries_needed": [
    "specific physician query needed"
  ],
  "physician_query_letters": [
    {{"query_topic": "topic of query", "query_letter": "complete ready to send physician query letter text"}}
  ],
  "wound_care": {{
    "present": "Yes or No",
    "wound_type": "pressure ulcer or venous ulcer or surgical wound or diabetic wound or other",
    "location": "exact anatomical location",
    "stage": "stage 1 2 3 4 or unstageable or not documented",
    "size": "dimensions if documented or not documented",
    "details": "full wound description",
    "skilled_need": "specific skilled nursing interventions needed",
    "oasis_item": "M1300 or M1302 or M1306 or M1307 or M1308 as applicable"
  }},
  "lab_draw": {{
    "present": "Yes or No",
    "details": "specific labs ordered and frequency",
    "high_risk_monitoring": "specific lab monitoring needed for high risk medications"
  }},
  "skilled_need": {{
    "service": "SN or PT or OT or ST or combination",
    "rationale": "specific skilled need justification per Medicare guidelines",
    "frequency_suggestion": "suggested visit frequency"
  }},
  "medications": {{
    "high_risk": "list all high risk medications",
    "all_medications": "complete medication list if available",
    "medication_teaching_needed": "Yes or No with details",
    "reconciliation_needed": "Yes or No"
  }},
  "oasis_alerts": {{
    "m1033_hospitalization_risk": "High or Medium or Low with reason",
    "m1240_pain_assessment": "pain present Yes or No with details",
    "m1800_grooming": "independent or needs assistance or dependent",
    "m1910_fall_risk": "Yes or No with details",
    "mental_health_flags": "depression or anxiety or dementia if documented or None",
    "cardiac_rehab_indicated": "Yes or No with rationale",
    "diabetic_foot_care": "Yes or No with details",
    "pressure_ulcer_risk": "High or Medium or Low",
    "face_to_face_missing": "Yes or No",
    "homebound_documentation_sufficient": "Yes or No with reason"
  }},
  "therapy_needs": {{
    "pt_indicated": "Yes or No with specific functional deficits",
    "ot_indicated": "Yes or No with specific ADL deficits",
    "st_indicated": "Yes or No with specific speech or swallowing deficits",
    "therapy_goals": "specific measurable therapy goals"
  }},
  "coding_warnings": [
    "specific compliance warning"
  ],
  "pdgm_considerations": {{
    "clinical_group": "predicted PDGM clinical grouping",
    "comorbidity_adjustment": "relevant comorbidity codes for payment adjustment",
    "functional_impairment": "level based on documentation",
    "high_value_codes": "list high value secondary codes that trigger comorbidity adjustment"
  }},
  "documentation_gaps": [
    "specific missing documentation needed for compliance"
  ]
}}

CRITICAL ICD-10-CM HOME HEALTH CODING RULES - YOU MUST FOLLOW:
1. PDx must be definitive diagnosis - NEVER a symptom (R-code), NEVER a Z-code, NEVER history-of code
2. For post-surgical vascular patients: Code the CONDITION that required surgery, NOT the post-op status
3. For aortoiliac occlusion s/p bypass: Use I74.5 (Embolism/thrombosis of iliac artery) - NOT I70.2x
4. I70.2x codes are for NATIVE arteries of EXTREMITIES (below inguinal ligament) - NOT for aortoiliac disease
5. NEVER code possible, suspected, or rule-out diagnoses
6. NEVER code resolved conditions
7. Do NOT code symptoms integral to PDx
8. Use highest specificity with all required characters
9. Z-codes (Z95.828 for graft status) are SECONDARY codes only - NEVER primary

ANATOMICAL CODING RULES:
- Aorta and iliac arteries = I74.x (arterial embolism/thrombosis) or I77.x (other arterial disorders)
- Femoral, popliteal, tibial, peroneal arteries = I70.2x (atherosclerosis) or I74.3-I74.5 (embolism)
- Aortobifemoral bypass = I74.5 for the underlying occlusion
- Peripheral artery disease (PAD) of extremities = I70.2xx series

Clinical documentation:
{safe_text}

Return ONLY valid JSON starting with open brace and ending with close brace. No markdown, no explanation."""

    try:
        raw = call_api(prompt)
        cleaned = re.sub(r'```json|```', '', raw).strip()
        start = cleaned.find('{')
        end = cleaned.rfind('}') + 1
        if start == -1 or end <= start:
            raise Exception("No valid JSON found in response")
        
        cleaned = cleaned[start:end]
        result = json.loads(cleaned)
        result = validate_pdx_result(result, clinical_text)
        
        return result
        
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {str(e)}")
        st.text("Raw response (first 2000 chars):")
        st.text(raw[:2000])
        raise Exception(f"Failed to parse API response: {str(e)}")
    except Exception as e:
        raise Exception(f"Analysis failed: {str(e)}")

def generate_pdf_report(result):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('title', parent=styles['Title'], fontSize=18, textColor=colors.HexColor('#0066cc'))
    header_style = ParagraphStyle('header', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#1a1a2e'))
    body_style = ParagraphStyle('body', parent=styles['Normal'], fontSize=10, spaceAfter=6)

    story.append(Paragraph("CareBridge Home Health PDx Analysis Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Patient Information", header_style))
    patient_data = [
        ["Patient Name", result.get('patient_name', 'Not found')],
        ["Date of Birth", result.get('patient_dob', 'Not found')],
        ["Age / Gender", f"{result.get('patient_age', '')} {result.get('patient_gender', '')}"],
        ["Admission Date", result.get('admission_date', 'Not found')],
        ["Discharge Date", result.get('discharge_date', 'Not found')],
        ["Face to Face Date", result.get('face_to_face_date', 'Not found')],
        ["Attending Physician", result.get('attending_physician', 'Not found')],
        ["Referring Physician", result.get('referring_physician', 'Not found')],
        ["Qualifying Event", result.get('qualifying_event', 'Not found')],
    ]
    t = Table(patient_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4fd')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Primary Diagnosis (PDx)", header_style))
    story.append(Paragraph(f"<b>{result.get('pdx_code', '')} — {result.get('pdx_description', '')}</b>", body_style))
    story.append(Paragraph(f"Rationale: {result.get('pdx_rationale', '')}", body_style))
    story.append(Paragraph(f"Confidence: {result.get('confidence_score', '')} — {result.get('confidence_reason', '')}", body_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Change in Condition", header_style))
    story.append(Paragraph(result.get('change_in_condition', 'Not documented'), body_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Secondary Diagnoses", header_style))
    secondary = result.get('secondary_codes', [])
    if secondary:
        sec_data = [["Code", "Description", "Rationale"]]
        for code in secondary:
            sec_data.append([code.get('code', ''), code.get('description', ''), code.get('rationale', '')])
        t2 = Table(sec_data, colWidths=[1*inch, 2.5*inch, 2.5*inch])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t2)
    story.append(Spacer(1, 0.2*inch))

    queries = result.get('queries_needed', [])
    if queries:
        story.append(Paragraph("Physician Queries Needed", header_style))
        for q in queries:
            story.append(Paragraph(f"- {q}", body_style))
        story.append(Spacer(1, 0.2*inch))

    skilled = result.get('skilled_need', {})
    story.append(Paragraph("Skilled Need", header_style))
    story.append(Paragraph(f"Service: {skilled.get('service', '')}", body_style))
    story.append(Paragraph(f"Rationale: {skilled.get('rationale', '')}", body_style))
    story.append(Paragraph(f"Frequency: {skilled.get('frequency_suggestion', '')}", body_style))
    story.append(Spacer(1, 0.2*inch))

    oasis = result.get('oasis_alerts', {})
    story.append(Paragraph("OASIS Alerts", header_style))
    oasis_data = [
        ["M1033 Hospitalization Risk", oasis.get('m1033_hospitalization_risk', '')],
        ["M1240 Pain Assessment", oasis.get('m1240_pain_assessment', '')],
        ["M1910 Fall Risk", oasis.get('m1910_fall_risk', '')],
        ["Mental Health Flags", oasis.get('mental_health_flags', '')],
        ["Face to Face Missing", oasis.get('face_to_face_missing', '')],
        ["Homebound Documentation", oasis.get('homebound_documentation_sufficient', '')],
        ["Pressure Ulcer Risk", oasis.get('pressure_ulcer_risk', '')],
    ]
    t3 = Table(oasis_data, colWidths=[2.5*inch, 3.5*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3cd')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t3)
    story.append(Spacer(1, 0.2*inch))

    warnings = result.get('coding_warnings', [])
    if warnings:
        story.append(Paragraph("Coding Warnings", header_style))
        for w in warnings:
            story.append(Paragraph(f"- {w}", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

def render_results(result):
    warnings = result.get('coding_warnings', [])
    auto_corrected = [w for w in warnings if 'Auto-corrected' in w or 'auto-corrected' in w.lower()]
    
    # Auto-correction banner
    if auto_corrected:
        st.markdown(f'<div class="auto-correct">⚡ {auto_corrected[0]}</div>', unsafe_allow_html=True)
    
    # Confidence badge
    conf = result.get('confidence_score', 'Medium')
    conf_class = f'confidence-{conf.lower()}'
    st.markdown(f'<div style="text-align: center; margin-bottom: 1.5rem;"><span class="confidence-badge {conf_class}">● {conf} Confidence</span></div>', unsafe_allow_html=True)
    
    # PDx Display
    st.markdown(f'''
        <div class="pdx-display animate-in">
            <div class="pdx-code">{result.get("pdx_code", "—")}</div>
            <div class="pdx-description">{result.get("pdx_description", "")}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Rationale
    with st.expander("📖 View Rationale", expanded=True):
        st.markdown(f'<div class="info-card">{result.get("pdx_rationale", "No rationale provided")}</div>', unsafe_allow_html=True)
    
    # Alternative PDx
    if result.get("pdx_alternative") and result.get("pdx_alternative") != "None":
        st.markdown(f'<div class="warning-card"><strong>🔄 Alternative Consideration:</strong> {result.get("pdx_alternative")}</div>', unsafe_allow_html=True)
    
    # Patient Info Grid
    st.markdown('<div class="section-header">👤 Patient Information</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'''
            <div class="status-item">
                <div class="status-icon">👤</div>
                <div class="status-content">
                    <div class="status-label">Patient</div>
                    <div class="status-value">{result.get("patient_name", "Not found")}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="status-item">
                <div class="status-icon">🎂</div>
                <div class="status-content">
                    <div class="status-label">DOB / Age</div>
                    <div class="status-value">{result.get("patient_dob", "—")} ({result.get("patient_age", "—")})</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
            <div class="status-item">
                <div class="status-icon">🏥</div>
                <div class="status-content">
                    <div class="status-label">Admission</div>
                    <div class="status-value">{result.get("admission_date", "—")}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="status-item">
                <div class="status-icon">✅</div>
                <div class="status-content">
                    <div class="status-label">Discharge</div>
                    <div class="status-value">{result.get("discharge_date", "—")}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
            <div class="status-item">
                <div class="status-icon">📋</div>
                <div class="status-content">
                    <div class="status-label">F2F Date</div>
                    <div class="status-value">{result.get("face_to_face_date", "Not found")}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="status-item">
                <div class="status-icon">👨‍⚕️</div>
                <div class="status-content">
                    <div class="status-label">Attending</div>
                    <div class="status-value">{result.get("attending_physician", "—")}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    # OASIS Alerts
    oasis = result.get('oasis_alerts', {})
    missing_flags = []
    if oasis.get('face_to_face_missing') == 'Yes':
        missing_flags.append("Face to face encounter date is missing")
    if oasis.get('homebound_documentation_sufficient') == 'No':
        missing_flags.append("Homebound status not sufficiently documented")
    if result.get('face_to_face_date') == 'Not found':
        missing_flags.append("Face to face date not found in document")
    
    if missing_flags:
        st.markdown('<div class="section-header">🚨 OASIS Compliance Alerts</div>', unsafe_allow_html=True)
        for flag in missing_flags:
            st.markdown(f'<div class="alert-card">{flag}</div>', unsafe_allow_html=True)
    
    # Change in Condition
    st.markdown('<div class="section-header">📈 Change in Condition</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="glass-card">{result.get("change_in_condition", "Not documented")}</div>', unsafe_allow_html=True)
    
    # Secondary Codes
    st.markdown('<div class="section-header">📋 Secondary Diagnoses</div>', unsafe_allow_html=True)
    secondary = result.get("secondary_codes", [])
    if secondary:
        for code in secondary:
            st.markdown(f'''
                <div class="code-item">
                    <span class="code-number">{code.get("code", "")}</span>
                    <div class="code-details">
                        <div class="code-title">{code.get("description", "")}</div>
                        <div class="code-rationale">{code.get("rationale", "")}</div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No secondary codes identified")
    
    # PDGM Considerations
    pdgm = result.get("pdgm_considerations", {})
    if pdgm:
        st.markdown('<div class="section-header">💰 PDGM Considerations</div>', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="glass-card">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div><strong>Clinical Group:</strong> {pdgm.get("clinical_group", "—")}</div>
                    <div><strong>Comorbidity Adjustment:</strong> {pdgm.get("comorbidity_adjustment", "—")}</div>
                    <div><strong>Functional Impairment:</strong> {pdgm.get("functional_impairment", "—")}</div>
                    <div><strong>High Value Codes:</strong> {pdgm.get("high_value_codes", "—")}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    # Physician Queries
    queries = result.get("queries_needed", [])
    if queries:
        st.markdown('<div class="section-header">❓ Physician Queries Needed</div>', unsafe_allow_html=True)
        for query in queries:
            st.markdown(f'<div class="query-card">{query}</div>', unsafe_allow_html=True)
    
    query_letters = result.get("physician_query_letters", [])
    if query_letters:
        st.markdown('<div class="section-header">✉️ Query Letters</div>', unsafe_allow_html=True)
        for letter in query_letters:
            with st.expander(f"{letter.get('query_topic', 'Query')}"):
                st.text_area("Ready to send", letter.get("query_letter", ""), height=200, key=f"letter_{letter.get('query_topic', '')}")
    
    # Clinical Details
    col1, col2 = st.columns(2)
    
    with col1:
        # Wound Care
        wound = result.get("wound_care", {})
        if wound.get("present") == "Yes":
            st.markdown('<div class="section-header">🩹 Wound Care</div>', unsafe_allow_html=True)
            st.markdown(f'''
                <div class="glass-card">
                    <p><strong>Type:</strong> {wound.get("wound_type", "—")}</p>
                    <p><strong>Location:</strong> {wound.get("location", "—")}</p>
                    <p><strong>Stage:</strong> {wound.get("stage", "—")}</p>
                    <p><strong>Size:</strong> {wound.get("size", "—")}</p>
                    <p><strong>OASIS:</strong> {wound.get("oasis_item", "—")}</p>
                </div>
            ''', unsafe_allow_html=True)
        
        # Medications
        meds = result.get("medications", {})
        st.markdown('<div class="section-header">💊 Medications</div>', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="glass-card">
                <p><strong>High Risk:</strong> {meds.get("high_risk", "None noted")}</p>
                <p><strong>Teaching Needed:</strong> {meds.get("medication_teaching_needed", "—")}</p>
                <p><strong>Reconciliation:</strong> {meds.get("reconciliation_needed", "—")}</p>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        # Skilled Need
        skilled = result.get("skilled_need", {})
        st.markdown('<div class="section-header">🏥 Skilled Need</div>', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="glass-card">
                <p><strong>Service:</strong> {skilled.get("service", "—")}</p>
                <p><strong>Frequency:</strong> {skilled.get("frequency_suggestion", "—")}</p>
                <p><strong>Rationale:</strong> {skilled.get("rationale", "—")}</p>
            </div>
        ''', unsafe_allow_html=True)
        
        # Therapy
        therapy = result.get("therapy_needs", {})
        st.markdown('<div class="section-header">🏃 Therapy</div>', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="glass-card">
                <p><strong>PT:</strong> {therapy.get("pt_indicated", "—")}</p>
                <p><strong>OT:</strong> {therapy.get("ot_indicated", "—")}</p>
                <p><strong>ST:</strong> {therapy.get("st_indicated", "—")}</p>
            </div>
        ''', unsafe_allow_html=True)
        
        # Lab Draw
        lab = result.get("lab_draw", {})
        if lab.get("present") == "Yes":
            st.markdown('<div class="section-header">🧪 Lab Draw</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="glass-card">{lab.get("details", "—")}</div>', unsafe_allow_html=True)
    
    # OASIS Alerts Summary
    st.markdown('<div class="section-header">📊 OASIS Assessment</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="glass-card">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div><strong>M1033 Risk:</strong> {oasis.get("m1033_hospitalization_risk", "—")}</div>
                <div><strong>M1240 Pain:</strong> {oasis.get("m1240_pain_assessment", "—")}</div>
                <div><strong>M1910 Fall Risk:</strong> {oasis.get("m1910_fall_risk", "—")}</div>
                <div><strong>Mental Health:</strong> {oasis.get("mental_health_flags", "—")}</div>
                <div><strong>Pressure Ulcer Risk:</strong> {oasis.get("pressure_ulcer_risk", "—")}</div>
                <div><strong>M1800 Grooming:</strong> {oasis.get("m1800_grooming", "—")}</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Documentation Gaps
    doc_gaps = result.get("documentation_gaps", [])
    if doc_gaps:
        st.markdown('<div class="section-header">⚠️ Documentation Gaps</div>', unsafe_allow_html=True)
        for gap in doc_gaps:
            st.markdown(f'<div class="warning-card">{gap}</div>', unsafe_allow_html=True)
    
    # Other Warnings
    other_warnings = [w for w in warnings if 'Auto-corrected' not in w and 'auto-corrected' not in w.lower()]
    if other_warnings:
        st.markdown('<div class="section-header">🚨 Coding Warnings</div>', unsafe_allow_html=True)
        for warning in other_warnings:
            st.markdown(f'<div class="alert-card">{warning}</div>', unsafe_allow_html=True)
    
    # Interactive Correction Panel
    st.markdown('<div class="correction-panel">', unsafe_allow_html=True)
    st.markdown("### ✏️ Is this PDx correct? Help me learn!")
    
    col_corr1, col_corr2 = st.columns(2)
    with col_corr1:
        wrong_code = st.text_input("Current Suggested Code", value=result.get('pdx_code', ''), key="wrong_code_input")
    with col_corr2:
        correct_code = st.text_input("Your Corrected Code", placeholder="Enter correct ICD-10 code...", key="correct_code_input")
    
    correction_reason = st.text_area("Why is this correction needed?", placeholder="Explain the clinical reasoning...", height=100, key="correction_reason")
    
    col_save, col_cancel = st.columns([1, 4])
    with col_save:
        if st.button("💾 Save Correction", use_container_width=True, type="primary"):
            if correct_code:
                correction = {
                    "wrong_code": wrong_code,
                    "correct_code": correct_code,
                    "context": result.get('pdx_description', ''),
                    "reason": correction_reason or "Clinical correction",
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "patient": result.get('patient_name', 'Unknown'),
                    "clinical_text": result.get('change_in_condition', '')[:200]
                }
                st.session_state.corrections.append(correction)
                st.success(f"✅ Saved! I'll remember that {correct_code} is correct for similar cases.")
                st.balloons()
            else:
                st.warning("Please enter the correct code")
    
    # Show recent corrections for this case type
    if st.session_state.corrections:
        st.markdown("#### 🧠 Recently Learned Corrections")
        st.markdown('<div class="correction-history">', unsafe_allow_html=True)
        for corr in reversed(st.session_state.corrections[-5:]):
            st.markdown(f'''
                <div class="correction-item">
                    <div class="code-change">
                        <span style="color: #ef4444;">{corr['wrong_code']}</span>
                        <span class="arrow">→</span>
                        <span style="color: #10b981;">{corr['correct_code']}</span>
                    </div>
                    <div class="meta">{corr['date']} • {corr['patient']} • {corr['reason'][:60]}...</div>
                </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Download Buttons
    st.markdown('<div class="section-header">📥 Export Results</div>', unsafe_allow_html=True)
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    with col_dl1:
        st.download_button(
            label="📄 Download JSON",
            data=json.dumps(result, indent=2),
            file_name=f"pdx_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    with col_dl2:
        try:
            pdf_buffer = generate_pdf_report(result)
            st.download_button(
                label="📕 Download PDF",
                data=pdf_buffer,
                file_name=f"pdx_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"PDF error: {str(e)}")
    with col_dl3:
        if st.button("➕ Add to Comparison", use_container_width=True):
            st.session_state.comparison_cases.append(result)
            st.success("✅ Added to comparison")

# Premium Header
st.markdown('''
    <div class="main-header animate-in">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 3rem;">🏥</div>
            <div>
                <div class="logo-text">CareBridge AI</div>
                <div class="tagline">Intelligent Clinical Documentation & Coding Platform</div>
            </div>
        </div>
    </div>
''', unsafe_allow_html=True)

# Sidebar - Interactive Learning Hub
with st.sidebar:
    st.markdown('<div class="sidebar-title">🎓 Learning Hub</div>', unsafe_allow_html=True)
    
    # Quick stats
    st.metric("Cases Analyzed", len(st.session_state.history))
    st.metric("Corrections Made", len(st.session_state.corrections))
    
    st.markdown("---")
    
    # Quick correction from sidebar
    st.markdown("### ⚡ Quick Fix")
    st.markdown("If the AI got it wrong, fix it here:")
    
    quick_wrong = st.text_input("Wrong Code", placeholder="e.g., I70.201", key="quick_wrong")
    quick_right = st.text_input("Right Code", placeholder="e.g., I74.5", key="quick_right")
    quick_reason = st.text_area("Reason", placeholder="Why this is wrong...", height=80, key="quick_reason")
    
    if st.button("🚀 Submit Correction", use_container_width=True):
        if quick_wrong and quick_right:
            correction = {
                "wrong_code": quick_wrong,
                "correct_code": quick_right,
                "context": "Manual sidebar correction",
                "reason": quick_reason or "Quick fix",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "patient": "Manual entry"
            }
            st.session_state.corrections.append(correction)
            st.success("✅ Correction saved!")
        else:
            st.warning("Enter both codes")
    
    st.markdown("---")
    
    # Learning progress
    if st.session_state.corrections:
        st.markdown("### 📚 Learning Progress")
        st.markdown(f"**{len(st.session_state.corrections)}** corrections taught")
        
        # Most corrected codes
        from collections import Counter
        wrong_codes = [c['wrong_code'] for c in st.session_state.corrections]
        top_mistakes = Counter(wrong_codes).most_common(3)
        
        st.markdown("**Common AI Mistakes:**")
        for code, count in top_mistakes:
            st.markdown(f"- `{code}` ({count}x)")
    
    st.markdown("---")
    st.markdown("### 🎯 Tips")
    st.info("""
    • Green = High confidence  
    • Yellow = Review suggested  
    • Red = Manual review required  
    
    Always verify PDx before finalizing!
    """)

# Main Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔄 New Analysis", "📚 Case History", "⚖️ Compare Cases", "📊 Analytics", "❓ Help"])

with tab1:
    col_input, col_output = st.columns([1, 1.2])
    
    with col_input:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📤 Upload Clinical Documents</div>', unsafe_allow_html=True)
        
        uploaded_pdfs = st.file_uploader("PDF Documents", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
        uploaded_images = st.file_uploader("Image Files", type=["jpg", "jpeg", "png"], accept_multiple_files=True, label_visibility="collapsed")
        pasted_text = st.text_area("Or Paste Text Directly", height=150, placeholder="Paste discharge summary, progress notes, or clinical documentation here...")
        
        all_text = ""
        if uploaded_pdfs:
            for pdf in uploaded_pdfs:
                with st.spinner(f"Processing {pdf.name}..."):
                    extracted = extract_text_from_pdf(pdf)
                    all_text += f"\n\n--- {pdf.name} ---\n{extracted}"
            st.success(f"✅ {len(uploaded_pdfs)} PDF(s) processed")
        
        if uploaded_images:
            for img_file in uploaded_images:
                st.image(img_file, use_column_width=True)
                img_file.seek(0)
                with st.spinner(f"OCR on {img_file.name}..."):
                    extracted = extract_text_from_image(img_file)
                    all_text += f"\n\n--- {img_file.name} ---\n{extracted}"
            st.success(f"✅ {len(uploaded_images)} image(s) processed")
        
        if pasted_text:
            all_text += f"\n\n--- Direct Input ---\n{pasted_text}"
        
        if all_text:
            with st.expander("🔍 Preview Extracted Text"):
                st.text(all_text[:2000] + ("..." if len(all_text) > 2000 else ""))
        
        analyze_button = st.button(
            "🚀 Analyze with AI",
            type="primary",
            use_container_width=True,
            disabled=not bool(all_text)
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_output:
        st.markdown('<div class="glass-card" style="min-height: 600px;">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🎯 Analysis Results</div>', unsafe_allow_html=True)
        
        if analyze_button and all_text:
            with st.spinner("🧠 AI analyzing clinical documentation..."):
                try:
                    result = analyze_clinical_notes(all_text)
                    result["analyzed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.current_result = result
                    st.session_state.history.append(result)
                    render_results(result)
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.info("Please check your API key and try again")
        
        elif st.session_state.current_result:
            render_results(st.session_state.current_result)
        else:
            st.markdown('''
                <div style="text-align: center; padding: 4rem 2rem; color: #94a3b8;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">📋</div>
                    <h3 style="color: #f1f5f9; margin-bottom: 0.5rem;">Ready to Analyze</h3>
                    <p>Upload documents or paste clinical notes to begin AI-powered coding analysis</p>
                </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📚 Case History & Analytics</div>', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("No cases analyzed yet. Start by analyzing a new case.")
    else:
        search_term = st.text_input("🔍 Search cases...", placeholder="Patient name, diagnosis code, or date...")
        
        filtered = st.session_state.history
        if search_term:
            filtered = [c for c in st.session_state.history if
                search_term.lower() in c.get('patient_name', '').lower() or
                search_term.lower() in c.get('pdx_code', '').lower() or
                search_term.lower() in c.get('analyzed_at', '').lower()]
        
        st.markdown(f'<p style="color: #94a3b8; margin-bottom: 1rem;">Showing {len(filtered)} of {len(st.session_state.history)} cases</p>', unsafe_allow_html=True)
        
        for i, case in enumerate(reversed(filtered)):
            with st.expander(f"{case.get('patient_name', 'Unknown')} — {case.get('pdx_code', '')} — {case.get('analyzed_at', '')}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Patient:** {case.get('patient_name', '')}")
                    st.markdown(f"**DOB:** {case.get('patient_dob', '')}")
                    st.markdown(f"**Attending:** {case.get('attending_physician', '')}")
                with c2:
                    st.markdown(f"**PDx:** {case.get('pdx_code', '')}")
                    st.markdown(f"**Confidence:** {case.get('confidence_score', '')}")
                    st.markdown(f"**Qualifying Event:** {case.get('qualifying_event', '')}")
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    st.download_button("📄 JSON", json.dumps(case, indent=2), f"case_{i}.json", "application/json", key=f"json_{i}")
                with btn_col2:
                    try:
                        pdf_buf = generate_pdf_report(case)
                        st.download_button("📕 PDF", pdf_buf, f"case_{i}.pdf", "application/pdf", key=f"pdf_{i}")
                    except:
                        pass
        
        if st.session_state.corrections:
            st.markdown("---")
            st.markdown("### 📝 Learning History")
            for corr in st.session_state.corrections[-5:]:
                st.markdown(f"- **{corr['date']}**: `{corr['wrong_code']}` → `{corr['correct_code']}` ({corr['patient']})")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">⚖️ Side-by-Side Case Comparison</div>', unsafe_allow_html=True)
    
    if len(st.session_state.comparison_cases) < 2:
        st.info("Add at least 2 cases to comparison from the analysis results.")
        if st.session_state.comparison_cases:
            st.markdown(f'<p style="color: #94a3b8;">Currently have {len(st.session_state.comparison_cases)} case(s) queued</p>', unsafe_allow_html=True)
    else:
        case_a = st.session_state.comparison_cases[-2]
        case_b = st.session_state.comparison_cases[-1]
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown(f'''
                <div class="comparison-card">
                    <h4 style="color: #f1f5f9; margin-bottom: 1rem;">Case A: {case_a.get('patient_name', 'Unknown')}</h4>
                    <div class="pdx-code" style="font-size: 1.5rem; margin-bottom: 0.5rem;">{case_a.get('pdx_code', '')}</div>
                    <p style="color: #cbd5e1;">{case_a.get('pdx_description', '')}</p>
                    <hr style="border-color: #334155; margin: 1rem 0;">
                    <p style="color: #94a3b8;"><strong style="color: #f1f5f9;">Confidence:</strong> {case_a.get('confidence_score', '')}</p>
                    <p style="color: #94a3b8;"><strong style="color: #f1f5f9;">Date:</strong> {case_a.get('analyzed_at', '')}</p>
                    <p style="color: #94a3b8;"><strong style="color: #f1f5f9;">Event:</strong> {case_a.get('qualifying_event', '')}</p>
                </div>
            ''', unsafe_allow_html=True)
        
        with col_b:
            st.markdown(f'''
                <div class="comparison-card highlight">
                    <h4 style="color: #f1f5f9; margin-bottom: 1rem;">Case B: {case_b.get('patient_name', 'Unknown')}</h4>
                    <div class="pdx-code" style="font-size: 1.5rem; margin-bottom: 0.5rem;">{case_b.get('pdx_code', '')}</div>
                    <p style="color: #cbd5e1;">{case_b.get('pdx_description', '')}</p>
                    <hr style="border-color: #334155; margin: 1rem 0;">
                    <p style="color: #94a3b8;"><strong style="color: #f1f5f9;">Confidence:</strong> {case_b.get('confidence_score', '')}</p>
                    <p style="color: #94a3b8;"><strong style="color: #f1f5f9;">Date:</strong> {case_b.get('analyzed_at', '')}</p>
                    <p style="color: #94a3b8;"><strong style="color: #f1f5f9;">Event:</strong> {case_b.get('qualifying_event', '')}</p>
                </div>
            ''', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Comparison", use_container_width=True):
            st.session_state.comparison_cases = []
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 Monthly Analytics Dashboard</div>', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("No data available. Analyze cases to generate analytics.")
    else:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cases", len(st.session_state.history))
        with col2:
            high_conf = sum(1 for c in st.session_state.history if c.get('confidence_score') == 'High')
            st.metric("High Confidence", f"{high_conf} ({high_conf/len(st.session_state.history)*100:.0f}%)")
        with col3:
            st.metric("Corrections", len(st.session_state.corrections))
        with col4:
            unique_pdx = len(set(c.get('pdx_code') for c in st.session_state.history))
            st.metric("Unique Diagnoses", unique_pdx)
        
        # Charts data prep
        pdx_counts = {}
        for case in st.session_state.history:
            pdx = case.get('pdx_code', 'Unknown')
            pdx_counts[pdx] = pdx_counts.get(pdx, 0) + 1
        
        st.markdown("### 🏆 Most Common PDx Codes")
        top_pdx = sorted(pdx_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for code, count in top_pdx:
            percentage = count / len(st.session_state.history) * 100
            st.markdown(f'''
                <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                    <div style="width: 100px; font-family: monospace; color: #6366f1; font-weight: 700;">{code}</div>
                    <div style="flex: 1; background: #1e293b; border-radius: 4px; height: 24px; overflow: hidden;">
                        <div style="width: {percentage}%; background: linear-gradient(90deg, #6366f1, #ec4899); height: 100%; border-radius: 4px;"></div>
                    </div>
                    <div style="width: 60px; text-align: right; color: #94a3b8; font-weight: 600;">{count}</div>
                </div>
            ''', unsafe_allow_html=True)
        
        # Export
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "total_cases": len(st.session_state.history),
            "pdx_distribution": pdx_counts,
            "corrections_made": len(st.session_state.corrections),
            "cases": st.session_state.history
        }
        st.download_button(
            "📥 Export Full Report",
            json.dumps(report_data, indent=2),
            f"carebridge_report_{datetime.now().strftime('%Y%m')}.json",
            "application/json",
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">❓ Platform Guide</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🚀 Getting Started
    
    **1. Document Upload**
    - Drag & drop PDF discharge summaries
    - Upload photos of documents (AI-powered OCR)
    - Paste text directly from EHR
    
    **2. AI Analysis**
    - Automatic patient data extraction
    - Intelligent PDx suggestion with validation
    - OASIS compliance checking
    - PDGM grouping prediction
    
    **3. Review & Correct**
    - Confidence scoring (High/Medium/Low)
    - Auto-correction for common errors
    - Submit corrections to improve AI
    
    **4. Export & Share**
    - JSON for EHR integration
    - PDF reports for physicians
    - Case comparison for QA
    
    ### ⚡ Pro Tips
    
    - **High Confidence** = Green (ready to use)
    - **Medium Confidence** = Yellow (quick review)
    - **Low Confidence** = Red (detailed review needed)
    
    ### 🔒 Security Note
    
    This demo uses non-HIPAA infrastructure. For production use with PHI, contact us for HIPAA-compliant deployment.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
