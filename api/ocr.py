import pytesseract
from PIL import Image
import io
import pdfplumber
# Add docx support
try:
    from docx import Document
except ImportError:
    Document = None

def extract_text_from_file(file):
    filename = file.filename.lower()
    # For PDF files
    if filename.endswith('.pdf'):
        file.stream.seek(0)
        with pdfplumber.open(file.stream) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() or ''
        return text
    # For DOCX files
    if filename.endswith('.docx'):
        if Document is None:
            raise ImportError('python-docx is not installed. Please install it with pip install python-docx')
        file.stream.seek(0)
        doc = Document(file.stream)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
    # For images
    try:
        image = Image.open(file.stream)
        text = pytesseract.image_to_string(image)
        return text
    except Exception:
        # For text-based files
        file.stream.seek(0)
        return file.stream.read().decode(errors='ignore')
