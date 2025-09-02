import re
import spacy
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

# Load custom trained NER model if available
try:
    nlp = spacy.load("custom_pii_ner_model")
except Exception:
    nlp = spacy.blank('en')

# Load HuggingFace transformer NER model
NER_MODEL = 'dslim/bert-base-NER'  # You can change to a PII-specialized model if available
ner_tokenizer = AutoTokenizer.from_pretrained(NER_MODEL)
ner_model = AutoModelForTokenClassification.from_pretrained(NER_MODEL)
ner_pipeline = pipeline('ner', model=ner_model, tokenizer=ner_tokenizer, aggregation_strategy="simple")

PII_PATTERNS = {
    # Aadhaar: labeled and label-free (12 digits, allow spaces or dashes)
    'aadhaar': r'(?i)(aadhaar( no| number)?\s*[:\-]?\s*)?(\d{4}[- ]\d{4}[- ]\d{4})',
    # PAN: labeled only
    'pan': r'(?i)(pan\s*[:\-]?\s*)([A-Z]{5}\d{4}[A-Z])',
    # DOB: labeled and label-free (dd/mm/yyyy)
    'dob': r'(?i)(dob|date of birth)?\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})',
    'email': r'(?i)(email\s*[:\-]?\s*)([\w.-]+@[\w.-]+\.\w+)',
    'phone': r'(?i)(phone\s*[:\-]?\s*)(\d{10}|\d{3}[- ]\d{3}[- ]\d{4}|\d{3} \d{3} \d{4})',
    'name': r'(?i)((name|s/o|d/o|w/o|c/o)\s*[:\-]?\s*)([A-Z][a-z]+( [A-Z][a-z]+)+)',
    'certificate_no': r'(?i)(certificate no\s*[:\-]?\s*)([A-Z]{2}-\d{12})',
    'application_no': r'(?i)(application no\s*[:\-]?\s*)([A-Z0-9\-]{8,20})',
    'voter_id': r'(?i)(voter id\s*[:\-]?\s*)([A-Z]{3}[0-9]{7})',
    'passport': r'(?i)(passport( no| number)?\s*[:\-]?\s*)([A-Z][0-9]{7})',
    'driving_license': r'(?i)(driving license( no| number)?\s*[:\-]?\s*)([A-Z]{2}[0-9]{13})',
    'ifsc': r'(?i)(ifsc\s*[:\-]?\s*)([A-Z]{4}0[A-Z0-9]{6})',
    'account_no': r'(?i)(account( no| number)?\s*[:\-]?\s*)([0-9]{9,18})',
    'student_id': r'(?i)(student id\s*[:\-]?\s*)([A-Z0-9\-]{6,20})',
}

# List of official/government email domains to ignore as PII
OFFICIAL_EMAIL_DOMAINS = [
    '@uidai.gov.in', '@gov.in', '@nic.in', '@india.gov.in', '@mygov.in', '@aadhaarindia.gov.in'
]

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
    if pii_type == 'person' or pii_type == 'name':
        # Context-aware masking for names: keep first and last character
        if len(value) > 2:
            return value[0] + 'X' * (len(value)-2) + value[-1]
        return 'X' * len(value)
    # Default: mask all but first and last char
    if len(value) > 2:
        return value[0] + 'X' * (len(value)-2) + value[-1]
    return 'X' * len(value)

def detect_pii(text):
    print("[DEBUG] OCR Extracted Text:\n", text)  # Debug: print OCR output
    results = []
    norm_text = re.sub(r'[\n\r\t]+', ' ', text)  # Normalize whitespace
    # Regex-based detection (for Aadhaar, PAN, email, phone, DOB, NAME, etc.)
    for label, pattern in PII_PATTERNS.items():
        for match in re.finditer(pattern, text):
            value = match.groups()[-1] if hasattr(match, 'groups') and match.groups() else match.group()
            # Aadhaar context filter: skip if 'print date' or 'prnt date' nearby
            if label == 'aadhaar':
                start = max(0, match.start() - 50)
                context = text[start:match.start()].lower()
                if 'print date' in context or 'prnt date' in context:
                    continue
            # DOB context filter: skip if 'print date' or 'prnt date' nearby
            if label == 'dob':
                start = max(0, match.start() - 50)
                context = text[start:match.start()].lower()
                if 'print date' in context or 'prnt date' in context:
                    continue
            # Filter out official/government emails
            if label == 'email':
                if any(value.lower().endswith(domain) for domain in OFFICIAL_EMAIL_DOMAINS):
                    continue
            # Improved DOB detection: flexible context check for OCR variations
            if label == 'dob':
                norm_match = re.search(re.escape(match.group()), norm_text)
                if norm_match:
                    start = max(0, norm_match.start() - 50)
                    context = norm_text[start:norm_match.start()].lower()
                    # Flexible context: allow spaces, colons, and ignore case
                    if 'print date' in context:
                        continue
                    if not re.search(r'dob|d\\.o\\.b|date\\s*:?\\s*of\\s*:?\\s*birth', context):
                        continue
            masked = mask_value(match.group(), label)
            if not any(r['value'] == value and r['type'] == label for r in results):
                results.append({'type': label, 'value': value, 'masked': masked, 'confidence': 0.99})
    # Transformer-based NER for general entities (PERSON, LOCATION)
    ner_results = ner_pipeline(text)
    for ent in ner_results:
        ent_type = ent['entity_group'].lower()
        if ent_type in ['person', 'location']:
            masked = mask_value(ent['word'], ent_type)
            # Avoid duplicates (don't add if already found by regex)
            if not any(r['value'] == ent['word'] and r['type'] == ent_type for r in results):
                results.append({'type': ent_type, 'value': ent['word'], 'masked': masked, 'confidence': float(ent['score'])})
    return results
