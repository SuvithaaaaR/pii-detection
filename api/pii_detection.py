import re
import spacy

nlp = spacy.blank('en')

PII_PATTERNS = {
    'aadhaar': r'\b\d{4}[- ]\d{4}[- ]\d{4}\b',
    'pan': r'\b[A-Z]{5}\d{4}[A-Z]\b',
    'dob': r'\b\d{2}/\d{2}/\d{4}\b',
    'email': r'\b[\w.-]+@[\w.-]+\.\w+\b',
    'phone': r'\b\d{10}\b',
}

def mask_value(value, pii_type):
    if pii_type == 'aadhaar':
        return value[:2] + 'XX-XXXX-XXXX'
    if pii_type == 'pan':
        return value[:2] + 'XXXXX' + value[-1]
    if pii_type == 'dob':
        return 'XX/XX/' + value[-4:]
    if pii_type == 'email':
        parts = value.split('@')
        return parts[0][0] + 'X' * (len(parts[0])-2) + parts[0][-1] + '@' + parts[1] if len(parts[0]) > 2 else 'X@' + parts[1]
    if pii_type == 'phone':
        return 'XXXXXX' + value[-4:]
    # Default: mask all but first and last char
    if len(value) > 2:
        return value[0] + 'X' * (len(value)-2) + value[-1]
    return 'X' * len(value)

def detect_pii(text):
    results = []
    norm_text = re.sub(r'[\n\r\t]+', ' ', text)  # Normalize whitespace
    for label, pattern in PII_PATTERNS.items():
        for match in re.finditer(pattern, text):
            # Improved DOB detection: flexible context check for OCR variations
            if label == 'dob':
                norm_match = re.search(re.escape(match.group()), norm_text)
                if norm_match:
                    start = max(0, norm_match.start() - 50)
                    context = norm_text[start:norm_match.start()].lower()
                    # Flexible context: allow spaces, colons, and ignore case
                    if 'print date' in context:
                        continue
                    if not re.search(r'dob|d\.o\.b|date\s*:?\s*of\s*:?\s*birth', context):
                        continue
            masked = mask_value(match.group(), label)
            results.append({'type': label, 'value': match.group(), 'masked': masked, 'confidence': 0.99})
    # Use spaCy for names (very basic)
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            masked = mask_value(ent.text, 'name')
            results.append({'type': 'name', 'value': ent.text, 'masked': masked, 'confidence': 0.95})
    return results
