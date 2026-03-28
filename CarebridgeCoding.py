import streamlit as st
import pytesseract
import json
import requests
from PIL import Image
import re
from datetime import datetime
import fitz
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from io import BytesIO

st.set_page_config(page_title="CareBridge", layout="wide", initial_sidebar_state="collapsed")

# Premium Minimal CSS - Professional, Clean, No Wasted Space
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #ffffff;
    --bg-secondary: #f8f9fa;
    --border: #e9ecef;
    --text: #212529;
    --text-secondary: #6c757d;
    --accent: #0d6efd;
    --accent-light: #e7f1ff;
    --success: #198754;
    --warning: #ffc107;
    --danger: #dc3545;
    --radius: 6px;
    --shadow: 0 1px 3px rgba(0,0,0,0.08);
}

* { font-family: 'Inter', -apple-system, sans-serif; color: var(--text); }

.stApp { background: var(--bg); }

/* Header - Clean */
header {
    border-bottom: 1px solid var(--border);
    padding: 1rem 0;
    margin-bottom: 2rem;
}

.brand {
    font-size: 1.25rem;
    font-weight: 600;
    letter-spacing: -0.02em;
}

.brand span { color: var(--accent); font-weight: 700; }

/* Layout - Tight, No Waste */
.main-grid {
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 2rem;
    align-items: start;
}

/* Input Panel */
.input-panel {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
}

.section-label {
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
}

/* Upload Zone */
.upload-zone {
    border: 2px dashed var(--border);
    border-radius: var(--radius);
    padding: 2rem;
    text-align: center;
    transition: all 0.2s;
    cursor: pointer;
}

.upload-zone:hover {
    border-color: var(--accent);
    background: var(--accent-light);
}

/* Text Input */
.stTextArea textarea {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    font-size: 0.875rem !important;
    min-height: 120px !important;
}

/* Primary Button */
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 0.625rem 1.25rem !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    width: 100% !important;
}

/* Results Panel */
.results-panel {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    min-height: 600px;
}

.empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 600px;
    color: var(--text-secondary);
    font-size: 0.875rem;
}

/* PDX Header */
.pdx-header {
    padding: 2rem;
    border-bottom: 1px solid var(--border);
}

.pdx-code {
    font-family: 'SF Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.03em;
    line-height: 1;
}

.pdx-desc {
    font-size: 1.125rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
    font-weight: 400;
}

.confidence-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.875rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 1rem;
}

.conf-high { background: #d1fae5; color: #065f46; }
.conf-med { background: #fef3c7; color: #92400e; }
.conf-low { background: #fee2e2; color: #991b1b; }

/* Content Sections */
.content-section {
    padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--border);
}

.content-section:last-child { border-bottom: none; }

.section-title {
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}

/* Data Grid */
.data-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}

.data-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.data-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.data-value {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text);
}

/* AI Chat Interface - The Interactive Part */
.ai-chat {
    background: var(--bg-secondary);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-top: 1rem;
}

.ai-message {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.ai-avatar {
    width: 32px;
    height: 32px;
    background: var(--accent);
    color: white;
    border-radius: var(--radius);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
    font-weight: 600;
    flex-shrink: 0;
}

.ai-content {
    flex: 1;
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    font-size: 0.875rem;
    line-height: 1.6;
}

.ai-content strong { color: var(--accent); }

/* Correction Interface */
.correction-box {
    background: white;
    border: 2px solid var(--accent);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-top: 1rem;
}

.correction-title {
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.correction-inputs {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}

.correction-reason {
    margin-bottom: 1rem;
}

/* AI Response to Correction */
.ai-debate {
    background: #fffbeb;
    border-left: 3px solid var(--warning);
    padding: 1rem;
    margin: 1rem 0;
    font-size: 0.875rem;
    border-radius: 0 var(--radius) var(--radius) 0;
}

.ai-agreement {
    background: #f0fdf4;
    border-left: 3px solid var(--success);
    padding: 1rem;
    margin: 1rem 0;
    font-size: 0.875rem;
    border-radius: 0 var(--radius) var(--radius) 0;
}

/* Secondary Codes */
.code-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.code-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.875rem 1rem;
    background: var(--bg-secondary);
    border-radius: var(--radius);
    border-left: 3px solid var(--accent);
}

.code-value {
    font-family: monospace;
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--accent);
    min-width: 80px;
}

.code-text {
    font-size: 0.875rem;
    color: var(--text);
}

/* Warnings */
.warning-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.875rem;
    background: #fef2f2;
    border-radius: var(--radius);
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
    color: #991b1b;
}

/* Action Buttons */
.action-bar {
    display: flex;
    gap: 0.75rem;
    padding: 1.5rem 2rem;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border);
}

.stButton > button {
    border-radius: var(--radius) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
}

/* Hide Defaults */
#MainMenu, footer, header { visibility: hidden; }
.stTabs [data-baseweb="tab-list"] { display: none; }
</style>
""", unsafe_allow_html=True)

# Configuration
API_KEY = "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"
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "corrections" not in st.session_state:
    st.session_state.corrections = []
if "current" not in st.session_state:
    st.session_state.current = None
if "ai_conversation" not in st.session_state:
    st.session_state.ai_conversation = []
if "learning_context" not in st.session_state:
    st.session_state.learning_context = ""

def call_ai(messages):
    """Call AI with conversation history"""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": messages,
        "max_tokens": 1500,
        "temperature": 0.3
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"]
    except:
        return None

def extract_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "".join([p.get_text() for p in doc])
    except:
        return ""

def extract_image(file):
    try:
        return pytesseract.image_to_string(Image.open(file))
    except:
        return ""

def analyze_with_ai(text):
    """Initial analysis with learning context"""
    context = st.session_state.learning_context
    
    system_msg = f"""You are an expert Home Health ICD-10-CM coding specialist. 
    You have learned from these previous corrections: {context}
    Analyze the case and respond in this exact format:
    
    PDX_CODE: [code]
    PDX_DESC: [description]
    CONFIDENCE: [High/Medium/Low]
    RATIONALE: [explanation]
    SECONDARY: [code: description, code: description]
    WARNINGS: [any coding warnings]
    OASIS: [key oasis considerations]
    
    If you see patterns from your learned corrections, apply them and note it."""
    
    user_msg = f"Analyze this discharge summary:\n\n{text[:6000]}"
    
    result = call_ai([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ])
    
    return parse_ai_response(result, text)

def parse_ai_response(text, source_text):
    """Parse AI response into structured data"""
    if not text:
        return None
    
    result = {
        "raw_response": text,
        "source_text": source_text[:500],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    lines = text.split('\n')
    for line in lines:
        if line.startswith('PDX_CODE:'):
            result['pdx_code'] = line.split(':', 1)[1].strip()
        elif line.startswith('PDX_DESC:'):
            result['pdx_desc'] = line.split(':', 1)[1].strip()
        elif line.startswith('CONFIDENCE:'):
            result['confidence'] = line.split(':', 1)[1].strip()
        elif line.startswith('RATIONALE:'):
            result['rationale'] = line.split(':', 1)[1].strip()
        elif line.startswith('SECONDARY:'):
            result['secondary'] = line.split(':', 1)[1].strip()
        elif line.startswith('WARNINGS:'):
            result['warnings'] = line.split(':', 1)[1].strip()
        elif line.startswith('OASIS:'):
            result['oasis'] = line.split(':', 1)[1].strip()
    
    return result

def debate_correction(original, proposed, reason):
    """AI debates the correction - interactive"""
    context = st.session_state.learning_context
    
    debate_prompt = f"""You previously coded this case as {original['pdx_code']}.
    The user suggests it should be {proposed} because: {reason}
    
    Previous context you learned: {context}
    
    Respond as the AI coder:
    1. Acknowledge the suggestion
    2. Explain why you chose {original['pdx_code']} (your reasoning)
    3. Analyze if {proposed} might be better and why/why not
    4. If they convince you, admit it and explain what you'll learn
    5. If you disagree, explain why with clinical evidence
    
    Be conversational but professional. This is a learning dialogue."""
    
    response = call_ai([
        {"role": "system", "content": "You are an AI coding assistant learning from expert coders. Be honest about your reasoning."},
        {"role": "user", "content": debate_prompt}
    ])
    
    return response

def update_learning(original, corrected, reason, ai_response):
    """Update AI's learning context based on interaction"""
    # Extract the lesson
    lesson = f"""
    Case pattern: {original.get('source_text', '')[:100]}...
    I suggested: {original['pdx_code']}
    Correct code: {corrected}
    Reason: {reason}
    AI reflection: {ai_response[:200]}
    """
    
    st.session_state.learning_context += f"\n{lesson}"
    
    # Store correction
    st.session_state.corrections.append({
        "original": original['pdx_code'],
        "corrected": corrected,
        "reason": reason,
        "ai_agreement": "agreed" if "you are right" in ai_response.lower() or "correct" in ai_response.lower() else "debated",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

# Header
st.markdown('<div class="brand">Care<span>Bridge</span> Clinical Intelligence</div>', unsafe_allow_html=True)

# Main Layout - Compact Grid
col_input, col_output = st.columns([1, 2])

with col_input:
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    
    st.markdown('<div class="section-label">Source Documents</div>', unsafe_allow_html=True)
    
    # File uploads
    pdf_files = st.file_uploader("PDF", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    img_files = st.file_uploader("Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True, label_visibility="collapsed")
    
    # Text input
    st.markdown('<div class="section-label" style="margin-top: 1rem;">Or Paste Text</div>', unsafe_allow_html=True)
    raw_text = st.text_area("", height=150, placeholder="Paste discharge summary, progress notes, or clinical documentation...", label_visibility="collapsed")
    
    # Compile text
    full_text = raw_text or ""
    for pdf in pdf_files:
        full_text += f"\n\n[PDF: {pdf.name}]\n" + extract_pdf(pdf)
    for img in img_files:
        img.seek(0)
        full_text += f"\n\n[IMG: {img.name}]\n" + extract_image(img)
    
    # Analyze button
    if st.button("Analyze with AI", type="primary", disabled=not full_text.strip()):
        with st.spinner("AI analyzing..."):
            result = analyze_with_ai(full_text)
            if result:
                st.session_state.current = result
                st.session_state.ai_conversation = []
                st.rerun()
    
    # Learning summary
    if st.session_state.corrections:
        st.markdown('<div class="section-label" style="margin-top: 1.5rem;">AI Learning</div>', unsafe_allow_html=True)
        st.markdown(f"**{len(st.session_state.corrections)}** corrections taught")
        st.caption("The AI learns from your corrections and applies them to future cases.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_output:
    if not st.session_state.current:
        st.markdown('<div class="results-panel empty-state">Upload documents to begin analysis</div>', unsafe_allow_html=True)
    else:
        result = st.session_state.current
        
        st.markdown('<div class="results-panel">', unsafe_allow_html=True)
        
        # PDX Header
        conf_class = f"conf-{result.get('confidence', 'med').lower()}"
        st.markdown(f'''
            <div class="pdx-header">
                <div class="pdx-code">{result.get('pdx_code', '---')}</div>
                <div class="pdx-desc">{result.get('pdx_desc', '')}</div>
                <span class="confidence-pill {conf_class}">● {result.get('confidence', 'Medium')} Confidence</span>
            </div>
        ''', unsafe_allow_html=True)
        
        # Patient Data
        st.markdown('''
            <div class="content-section">
                <div class="section-title">Patient Information</div>
                <div class="data-grid">
                    <div class="data-item">
                        <span class="data-label">Attending</span>
                        <span class="data-value">Dr. Smith</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">Admission</span>
                        <span class="data-value">Jan 27, 2026</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">Discharge</span>
                        <span class="data-value">Feb 2, 2026</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">F2F Date</span>
                        <span class="data-value" style="color: var(--danger);">Not Found</span>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        # AI Rationale
        st.markdown('''
            <div class="content-section">
                <div class="section-title">AI Reasoning</div>
        ''', unsafe_allow_html=True)
        
        with st.expander("View full rationale", expanded=True):
            st.markdown(f'<div style="font-size: 0.875rem; line-height: 1.7;">{result.get("rationale", "No rationale provided")}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Secondary Codes
        if result.get('secondary'):
            st.markdown('''
                <div class="content-section">
                    <div class="section-title">Secondary Diagnoses</div>
                    <div class="code-list">
            ''', unsafe_allow_html=True)
            
            # Parse secondary codes
            secondaries = result['secondary'].split(',') if isinstance(result['secondary'], str) else []
            for sec in secondaries[:5]:
                if ':' in sec:
                    code, desc = sec.split(':', 1)
                    st.markdown(f'''
                        <div class="code-item">
                            <span class="code-value">{code.strip()}</span>
                            <span class="code-text">{desc.strip()}</span>
                        </div>
                    ''', unsafe_allow_html=True)
            
            st.markdown('</div></div>', unsafe_allow_html=True)
        
        # Warnings
        if result.get('warnings'):
            st.markdown('''
                <div class="content-section">
                    <div class="section-title">Coding Alerts</div>
            ''', unsafe_allow_html=True)
            st.markdown(f'<div class="warning-item">⚠️ {result["warnings"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # INTERACTIVE AI CORRECTION SECTION
        st.markdown('''
            <div class="content-section" style="background: var(--bg-secondary);">
                <div class="section-title">Interactive Correction</div>
        ''', unsafe_allow_html=True)
        
        # Show conversation history
        for msg in st.session_state.ai_conversation:
            if msg['type'] == 'user':
                st.markdown(f'''
                    <div class="ai-message">
                        <div class="ai-avatar" style="background: var(--text-secondary);">You</div>
                        <div class="ai-content">
                            <strong>Suggested:</strong> {msg['proposed_code']}<br>
                            <strong>Reason:</strong> {msg['reason']}
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                # AI response styling based on agreement
                is_agreement = "you are right" in msg['response'].lower() or "agree" in msg['response'].lower()
                box_class = "ai-agreement" if is_agreement else "ai-debate"
                st.markdown(f'''
                    <div class="{box_class}">
                        <strong>AI:</strong> {msg['response'][:500]}...
                    </div>
                ''', unsafe_allow_html=True)
        
        # Correction form
        st.markdown('<div class="correction-box">', unsafe_allow_html=True)
        st.markdown('<div class="correction-title">✏️ Suggest a Different Code</div>', unsafe_allow_html=True)
        
        col_code, col_desc = st.columns([1, 2])
        with col_code:
            new_code = st.text_input("ICD-10 Code", placeholder="e.g., I74.5", key="corr_code")
        with col_desc:
            new_desc = st.text_input("Description", placeholder="e.g., Embolism of iliac artery", key="corr_desc")
        
        reason = st.text_area("Clinical Reasoning", placeholder="Explain why this code is more accurate based on the documentation...", height=80, key="corr_reason")
        
        col_submit, col_apply = st.columns(2)
        
        with col_submit:
            if st.button("💬 Discuss with AI", use_container_width=True):
                if new_code and reason:
                    with st.spinner("AI thinking..."):
                        # Get AI's opinion
                        ai_response = debate_correction(result, new_code, reason)
                        
                        # Store in conversation
                        st.session_state.ai_conversation.append({
                            'type': 'user',
                            'proposed_code': new_code,
                            'reason': reason
                        })
                        st.session_state.ai_conversation.append({
                            'type': 'ai',
                            'response': ai_response
                        })
                        
                        # If AI agrees, offer to apply
                        if "you are right" in ai_response.lower() or "correct" in ai_response.lower():
                            st.session_state.suggested_correction = {
                                'code': new_code,
                                'desc': new_desc,
                                'reason': reason,
                                'ai_agreement': True
                            }
                        
                        st.rerun()
        
        with col_apply:
            if st.button("✓ Apply & Teach AI", type="primary", use_container_width=True):
                if new_code:
                    # Apply immediately
                    old_code = result['pdx_code']
                    result['pdx_code'] = new_code
                    result['pdx_desc'] = new_desc or result['pdx_desc']
                    result['rationale'] = f"[CORRECTED] {reason}"
                    result['confidence'] = 'High'
                    
                    # Update learning
                    ai_resp = st.session_state.ai_conversation[-1]['response'] if st.session_state.ai_conversation else "Manual correction"
                    update_learning(st.session_state.current, new_code, reason, ai_resp)
                    
                    # Reset conversation for this case
                    st.session_state.ai_conversation = []
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action bar
        st.markdown('''
            <div class="action-bar">
        ''', unsafe_allow_html=True)
        
        col_json, col_pdf, col_spacer = st.columns([1, 1, 2])
        with col_json:
            st.download_button("Export JSON", json.dumps(result, indent=2), "case.json", "application/json")
        with col_pdf:
            # Simple PDF generation
            try:
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                doc.build([
                    Paragraph(f"<b>CareBridge Report</b><br/><br/>PDX: {result['pdx_code']}<br/>{result['pdx_desc']}<br/><br/>Confidence: {result['confidence']}", 
                    st.session_state.get('style', None) or getSampleStyleSheet()['Normal'])
                ])
                buffer.seek(0)
                st.download_button("Export PDF", buffer, "case.pdf", "application/pdf")
            except:
                st.button("PDF Unavailable", disabled=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# History sidebar (collapsible bottom section)
if st.session_state.history:
    with st.expander(f"📚 Case History ({len(st.session_state.history)} cases)"):
        for h in reversed(st.session_state.history[-5:]):
            st.caption(f"{h.get('pdx_code')} | {h.get('timestamp', '')}")
