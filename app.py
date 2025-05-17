import io
import openai
import streamlit as st

# PDF/DOCX parsing
from PyPDF2 import PdfReader
import docx

# — Page config —
st.set_page_config(
    page_title="AI Cover Letter Maker",
    page_icon="✉️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# — Load API key from Streamlit secrets —
openai.api_key = st.secrets["OPENAI_API_KEY"]

# — Sidebar branding/info —
with st.sidebar:
    st.markdown("## 📄 AI Cover Letter Maker")
    st.write(
        "Generate tailored cover letters in seconds.\n\n"
        "Upload your resume and fill out the job details below."
    )
    st.markdown("---")

# — Main header —
st.header("🖋️ Create Your Cover Letter")

# 1. Job description input
job_text = st.text_area("1. Job Description (URL or text)", height=150)

# 2. Resume uploader
uploaded_file = st.file_uploader("2. Upload Your Resume (PDF or DOCX)", type=["pdf", "docx"])

def extract_text(file) -> str:
    """Extracts all text from PDF or DOCX."""
    name = file.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n\n".join(p.text for p in doc.paragraphs)
    return ""

resume_text = ""
if uploaded_file:
    with st.spinner("Extracting resume text…"):
        resume_text = extract_text(uploaded_file)
    st.success("Resume loaded")
    st.text_area("Resume Preview", resume_text, height=300)

# 3. Personal details
your_name  = st.text_input("3. Your Full Name")
your_email = st.text_input("4. Your Email Address")

# 4. Style & length controls
col1, col2 = st.columns(2)
with col1:
    tone       = st.selectbox("Tone", ["Professional","Friendly","Enthusiastic","Confident","Concise"])
    complexity = st.slider("Complexity", 1, 10, 5, help="1 = simple wording, 10 = elaborate phrasing")
with col2:
    length           = st.selectbox("Length", ["Short (1–2 paragraphs)", "Standard (3 paragraphs)", "Detailed (4–5 paragraphs)"])
    include_greeting = st.checkbox("Customize Greeting")
    if include_greeting:
        recipient_name = st.text_input("Recipient’s Name")
    else:
        recipient_name = None

# 5. Optional settings
with st.expander("Optional Settings"):
    company_name   = st.text_input("Company Name")
    position_title = st.text_input("Position Title")
    closing_remark = st.text_input("Custom Closing Phrase", placeholder="e.g. Warm regards")
    add_export     = st.checkbox("Enable DOCX Export", value=False)

# 6. Generate button
if st.button("🚀 Generate Cover Letter"):
    if not (job_text and resume_text and your_name and your_email):
        st.error("Please fill all required fields and upload your resume.")
    else:
        # Build prompt
        parts = [
            f"Write a {length.lower()} cover letter in a {tone.lower()} tone.",
            f"Complexity: {complexity}/10.",
            f"Job description: {job_text}",
            f"My resume:\n{resume_text}",
            f"Name: {your_name}, Email: {your_email}."
        ]
        if company_name:
            parts.append(f"Address to {company_name}.")
        if position_title:
            parts.append(f"Position: {position_title}.")
        if recipient_name:
            parts.append(f"Greeting: 'Dear {recipient_name},'")
        if closing_remark:
            parts.append(f"Closing: '{closing_remark}, {your_name}.'")
        prompt = "\n".join(parts)

        # Call OpenAI
        with st.spinner("Generating…"):
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content":prompt}],
                temperature=0.7,
                max_tokens=600,
            )
        letter = resp.choices[0].message.content.strip()
        st.success("✅ Done!")
        st.text_area("Your Cover Letter", letter, height=300)

        # Optional DOCX export
        if add_export:
            from io import BytesIO
            from docx import Document
            from docx.shared import Pt

            doc = Document()
            for line in letter.split("\n"):
                p = doc.add_paragraph(line)
                p.style.font.size = Pt(11)
            buf = BytesIO()
            doc.save(buf)
            buf.seek(0)
            st.download_button(
                "📄 Download as .docx",
                data=buf,
                file_name="cover_letter.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
