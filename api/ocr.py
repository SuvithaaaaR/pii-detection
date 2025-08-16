import pytesseract
from PIL import Image
import io
import pdfplumber

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
    # For images
    try:
        image = Image.open(file.stream)
        text = pytesseract.image_to_string(image)
        return text
    except Exception:
        # For text-based files
        file.stream.seek(0)
        return file.stream.read().decode(errors='ignore')
