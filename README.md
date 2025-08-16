# Real-Time PII Detection & Necessity Analysis Web Platform

## Project Overview

A secure web platform for uploading documents (PDF, image, scanned copy, or text), detecting PII (Personally Identifiable Information), checking if that PII is necessary for the selected service, and offering to mask/remove unnecessary information.

## Features

- Real-time PII detection using OCR, regex, and NLP
- Business rules engine to determine if detected PII is required for the selected service
- Option to redact/mask unnecessary PII
- Supports text, images, and scanned documents

## Architecture

- **Backend:** Python Flask (handles file upload, OCR, PII detection, necessity analysis, redaction)
- **Frontend:** (Not included in this scaffold)
- **Config:** YAML file for service rules

## File/Module Descriptions

- `api/app.py`: Main Flask app, API endpoints `/upload` and `/redact`
- `api/ocr.py`: OCR utilities using Tesseract
- `api/pii_detection.py`: PII detection logic (regex + spaCy)
- `api/rules_engine.py`: Business rules engine (loads YAML rules)
- `api/redaction.py`: Redaction utilities (placeholder)
- `config/service_rules.yaml`: Service-specific required PII fields
- `requirements.txt`: Python dependencies
- `api/sample.txt`: Example file for testing

## How It Works

1. User uploads a document and selects a service type
2. Backend extracts text using OCR (if needed)
3. PII detection is performed using regex and NLP
4. Necessity analysis checks which PII is required for the selected service
5. Response includes detected PII and which are necessary
6. User can request redaction of unnecessary PII (feature to be implemented)

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
4. Test the API using Postman or curl

## Extending the Project

- Implement frontend (React, Angular, etc.)
- Enhance redaction to actually mask/remove PII in files
- Add support for more file types (PDF, DOCX)
- Improve NLP detection with advanced models

---
