# Real-Time PII Detection & Necessity Analysis Web Platform

## Project Overview

A secure web platform for uploading documents (PDF, image, scanned copy, or text), detecting PII (Personally Identifiable Information) using OCR, regex, and advanced NLP, checking if that PII is necessary for the selected service, and offering to mask or download masked versions of the document.

## Features

- Real-time PII detection using OCR (Tesseract), regex, and spaCy NLP (upgradeable to transformer-based models)
- Context-aware DOB detection to avoid false positives (e.g., ignores print dates)
- Business rules engine to determine if detected PII is required for the selected service
- Option to mask PII and download a masked version of the document
- Supports text, images, and scanned documents
- Chrome extension support for quick PII analysis and masked file download

## Architecture

- **Backend:** Python Flask (handles file upload, OCR, PII detection, necessity analysis, masking, and download)
- **Frontend:** HTML/CSS/JS (UI for uploading, analyzing, and downloading masked files)
- **Config:** YAML file for service rules
- **OCR:** Tesseract via pytesseract and pdfplumber
- **PII Detection:** Regex for patterns (Aadhaar, PAN, email, phone, DOB), spaCy for names (upgradeable to transformer-based NER for better accuracy)
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
- `chrome-extension/`: Chrome extension for PII detection and masked file download

## How It Works (Step by Step)

1. **User uploads a document and selects a service type.**
   - Handled by the frontend (`ui/index.html` or Chrome extension) which sends the file and service type to the backend.
2. **Backend extracts text using OCR** (if the file is an image or PDF).
   - Implemented in `api/ocr.py` using Tesseract (for images) and pdfplumber (for PDFs).
3. **PII detection is performed** in `api/pii_detection.py`:
   - Regex is used for structured patterns (Aadhaar, PAN, email, phone, DOB).
   - spaCy NLP is used for names (PERSON) and can be upgraded to transformer-based NER for better accuracy.
   - Context-aware logic (e.g., for DOB) is applied to avoid false positives.
   - Masking is applied to detected PII values using the `mask_value` function.
4. **Necessity analysis** is performed in `api/rules_engine.py`:
   - Checks which PII is required for the selected service using business rules from the YAML config (`config/service_rules.yaml`).
5. **Response includes detected PII** (with masked values) and necessity info:
   - Returned by the Flask API in `api/app.py` to the frontend.
6. **User can download a masked version** of the document as plain text:
   - Handled by the `/download-masked` endpoint in `api/app.py`, available in both the web UI and Chrome extension.

## How to Run

1. Create and activate a Python virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate   # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```
2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
3. Install Tesseract OCR and add it to your system PATH.
4. Start the Flask server:
   ```
   cd api
   python app.py
   ```
5. Open `ui/index.html` in your browser for the web UI.
6. (Optional) Load the Chrome extension from `chrome-extension/` for browser-based PII detection and masked file download.

## Extending the Project

- Fine-tune or replace the spaCy NLP model with transformer-based models (e.g., DeBERTa-v3, BERT) specialized for PII detection.
- Use synthetic PII data generation and domain adaptation to boost real-world detection accuracy.
- Combine pattern matching with machine learning classifiers for hybrid detection.
- Enhance redaction to actually mask/remove PII in PDFs and images.
- Add support for more file types (DOCX, etc.).
- Add user authentication and audit logging.
- Integrate with cloud storage or enterprise document management systems.

---
