import PyPDF2
import docx
import re

def extract_text_from_resume(resume_file):
    text = ""

    if resume_file.name.endswith('.pdf'):
        reader = PyPDF2.PdfReader(resume_file)
        for page in reader.pages:
            text += page.extract_text() or ""

    elif resume_file.name.endswith('.docx'):
        doc = docx.Document(resume_file)
        for para in doc.paragraphs:
            text += para.text + " "

    # CLEAN TEXT
    return text.lower().replace('\n', ' ')


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
