# Real-Time PII Detection & Necessity Analysis Web Platform

## Project Overview

A secure web platform for uploading documents (PDF, image, scanned copy, or text), detecting PII (Personally Identifiable Information) using OCR, regex, and NLP, checking if that PII is necessary for the selected service, and offering to mask or download masked versions of the document.

## Features

- Real-time PII detection using OCR (Tesseract), regex, and spaCy NLP
- Context-aware DOB detection to avoid false positives (e.g., ignores print dates)
- Business rules engine to determine if detected PII is required for the selected service
- Option to mask PII and download a masked version of the document
- Supports text, images, and scanned documents
- Chrome extension support for quick PII analysis

## Architecture

- **Backend:** Python Flask (handles file upload, OCR, PII detection, necessity analysis, masking, and download)
- **Frontend:** HTML/CSS/JS (UI for uploading, analyzing, and downloading masked files)
- **Config:** YAML file for service rules
- **OCR:** Tesseract via pytesseract and pdfplumber
- **PII Detection:** Regex for patterns (Aadhaar, PAN, email, phone, DOB), spaCy for names
- **Masking:** Detected PII is replaced with masked values in the downloadable file

## File/Module Descriptions

- `api/app.py`: Main Flask app, API endpoints `/upload`, `/redact`, `/download-masked`
- `api/ocr.py`: OCR utilities using Tesseract and pdfplumber
- `api/pii_detection.py`: PII detection logic (regex + spaCy), context-aware DOB detection, masking
- `api/rules_engine.py`: Business rules engine (loads YAML rules)
- `api/redaction.py`: Redaction utilities (placeholder)
- `config/service_rules.yaml`: Service-specific required PII fields
- `requirements.txt`: Python dependencies
- `api/sample.txt`: Example file for testing
- `ui/index.html`: Main frontend UI
- `chrome-extension/`: Chrome extension for PII detection

## How It Works

1. User uploads a document and selects a service type
2. Backend extracts text using OCR (if needed)
3. PII detection is performed using regex and NLP (with context-aware DOB detection)
4. Necessity analysis checks which PII is required for the selected service
5. Response includes detected PII (with masked values) and necessity info
6. User can download a masked version of the document as plain text

## How to Run

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
2. Install Tesseract OCR and add it to your system PATH
3. Start the Flask server:
   ```
   cd api
   python app.py
   ```
4. Open `ui/index.html` in your browser for the web UI
5. (Optional) Load the Chrome extension from `chrome-extension/` for browser-based PII detection

## Extending the Project

- Enhance redaction to actually mask/remove PII in PDFs and images
- Add support for more file types (DOCX, etc.)
- Improve NLP detection with advanced models or external PII libraries
- Add user authentication and audit logging
- Integrate with cloud storage or enterprise document management systems

---
