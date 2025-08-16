import re
import spacy

nlp = spacy.blank('en')

PII_PATTERNS = {
    'aadhaar': r'\b\d{4}-\d{4}-\d{4}\b',
    'pan': r'\b[A-Z]{5}\d{4}[A-Z]\b',
    'dob': r'\b\d{2}/\d{2}/\d{4}\b',
    'email': r'\b[\w.-]+@[\w.-]+\.\w+\b',
    'phone': r'\b\d{10}\b',
}

def detect_pii(text):
    results = []
    for label, pattern in PII_PATTERNS.items():
        for match in re.finditer(pattern, text):
            results.append({'type': label, 'value': match.group(), 'confidence': 0.99})
    # Use spaCy for names (very basic)
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            results.append({'type': 'name', 'value': ent.text, 'confidence': 0.95})
    return results
