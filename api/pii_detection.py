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
    'aadhaar': r'\b\d{4}[- ]\d{4}[- ]\d{4}\b',
    'pan': r'\b[A-Z]{5}\d{4}[A-Z]\b',
    'dob': r'\b\d{2}/\d{2}/\d{4}\b',
    'email': r'\b[\w.-]+@[\w.-]+\.\w+\b',
    'phone': r'\b(?:\d{10}|\d{3}[- ]\d{3}[- ]\d{4}|\d{3} \d{3} \d{4})\b',
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
    # Regex-based detection (for Aadhaar, PAN, email, phone, DOB)
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
                    if not re.search(r'dob|d\\.o\\.b|date\\s*:?\\s*of\\s*:?\\s*birth', context):
                        continue
            masked = mask_value(match.group(), label)
            results.append({'type': label, 'value': match.group(), 'masked': masked, 'confidence': 0.99})
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
