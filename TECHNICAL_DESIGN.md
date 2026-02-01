# SafeShare - Technical Design Document

**Version:** 0.1.0 (MVP)  
**Date:** February 2026  
**Status:** In Development

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Module Specifications](#module-specifications)
5. [Data Flow](#data-flow)
6. [Security Considerations](#security-considerations)
7. [Performance & Scalability](#performance--scalability)
8. [Testing Strategy](#testing-strategy)
9. [Deployment](#deployment)
10. [Future Enhancements](#future-enhancements)

---

## System Overview

### Purpose
SafeShare is a local-first data anonymization tool that enables users to safely share sensitive Excel files by automatically detecting and replacing Personally Identifiable Information (PII) with consistent anonymous identifiers.

### Key Requirements
- **Local Processing:** All data processing must occur locally - no external API calls
- **Consistency:** Same input value must always map to same anonymous ID
- **Format Preservation:** Output file maintains original Excel structure
- **User Control:** Manual review and approval before anonymization
- **Security:** Optional encrypted mapping for reversibility

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit UI Layer                    │
│                      (app.py)                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ├──────────────┬──────────────┬──────────┐
                 ▼              ▼              ▼          ▼
         ┌──────────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐
         │FileHandler   │ │PIIDetector│ │Anonymizer│ │CryptoHandler│
         │- load_excel  │ │- detect   │ │- anonymize│ │- encrypt   │
         │- save_excel  │ │- scan_df  │ │- mappings │ │- decrypt   │
         └──────────────┘ └──────────┘ └─────────┘ └─────────┘
                 │              │              │          │
                 └──────────────┴──────────────┴──────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Local File System    │
                    │  (temp/, data/)        │
                    └────────────────────────┘
```

### Design Principles

1. **Modularity:** Each component is independent and testable
2. **Single Responsibility:** Each module handles one specific concern
3. **Separation of Concerns:** UI logic separate from business logic
4. **Fail-Safe:** Errors are caught and communicated clearly to users

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.9+ | Main development language |
| **UI Framework** | Streamlit | 1.31+ | Web application interface |
| **Data Processing** | pandas | 2.1+ | DataFrame manipulation |
| **Excel I/O** | openpyxl | 3.1+ | Excel file handling (.xlsx) |
| **Excel I/O (legacy)** | xlrd | 2.0+ | Excel file handling (.xls) |
| **PII Detection** | Microsoft Presidio | 2.2+ | PII detection framework |
| **NLP** | spaCy | 3.7+ | Natural language processing |
| **Pattern Matching** | regex | 2023.10+ | Advanced regex patterns |
| **Cryptography** | cryptography | 41.0+ | AES-256 encryption |
| **Fake Data** | Faker | 20.0+ | Test data generation |
| **Logging** | loguru | 0.7+ | Enhanced logging |

### Development Tools

- **Testing:** pytest, pytest-cov
- **Code Quality:** black, flake8, mypy
- **Version Control:** Git + GitHub

---

## Module Specifications

### 1. FileHandler (`src/file_handler.py`)

**Purpose:** Handle all file I/O operations

**Key Functions:**

```python
validate_file(file_path: Path) -> Tuple[bool, Optional[str]]
    Validates file extension and size
    Returns: (is_valid, error_message)

load_excel(file_path: Path) -> pd.DataFrame
    Loads Excel file into DataFrame
    Supports: .xlsx, .xls
    Raises: ValueError if file cannot be read

save_excel(df: pd.DataFrame, output_path: Path) -> None
    Saves DataFrame to Excel file
    Uses openpyxl engine

secure_delete(file_path: Path) -> None
    Securely overwrites and deletes file
```

**Constraints:**
- Max file size: 10MB (MVP)
- Supported formats: .xlsx, .xls

---

### 2. PIIDetector (`src/pii_detector.py`)

**Purpose:** Detect PII in text and DataFrames

**Detection Methods:**

| PII Type | Method | Pattern/Algorithm |
|----------|--------|-------------------|
| Israeli ID | Regex + Validation | 9 digits + Luhn check |
| Email | Regex | Standard email pattern |
| Phone | Regex | Israeli phone patterns |
| Names | NLP (future) | spaCy NER |
| Addresses | NLP (future) | spaCy NER + patterns |

**Key Functions:**

```python
detect_israeli_id(text: str) -> bool
    Validates using Luhn algorithm

detect_email(text: str) -> bool
    Pattern matching

detect_phone(text: str) -> bool
    Israeli phone number patterns

scan_dataframe(df: pd.DataFrame, threshold: float = 0.1) -> Dict
    Scans all columns
    Returns: {column_name: {types, counts, ratios}}
```

**Algorithm:**
1. Sample first 100 rows of each column (performance)
2. Apply detection methods
3. Calculate ratio of PII found
4. Flag columns exceeding threshold (default 10%)

---

### 3. Anonymizer (`src/anonymizer.py`)

**Purpose:** Perform consistent anonymization

**Key Functions:**

```python
anonymize_value(value: Any, pii_type: str, deterministic: bool) -> str
    Anonymizes single value
    Maintains consistency (same input → same output)

anonymize_column(series: pd.Series, pii_type: str) -> pd.Series
    Anonymizes entire column

anonymize_dataframe(df: pd.DataFrame, column_types: Dict) -> pd.DataFrame
    Anonymizes multiple columns
    Returns new DataFrame (doesn't modify original)
```

**Mapping Strategy:**

```python
# Internal mapping structure
self.mappings = {
    'israeli_id': {
        '123456789': 'ID-001',
        '987654321': 'ID-002',
        '123456789': 'ID-001',  # Same ID → same anon value
    },
    'email': {
        'david@example.com': 'EMAIL-001@anon.com',
    }
}
```

**Prefix Mapping:**
- `israeli_id` → `ID-XXX`
- `email` → `EMAIL-XXX@anon.com`
- `phone` → `PHONE-XXX`
- `name` → `PERSON-XXX`
- `address` → `ADDRESS-XXX`

---

### 4. CryptoHandler (`src/crypto_handler.py`)

**Purpose:** Encrypt/decrypt mapping files

**Encryption Spec:**
- Algorithm: AES-256 (Fernet)
- Key Derivation: PBKDF2 with SHA-256
- Salt: 16 random bytes
- Iterations: 100,000

**Key Functions:**

```python
encrypt_mapping(mapping: Dict, password: str, output_path: Path) -> None
    Encrypts mapping to file
    File format: [16-byte salt][encrypted JSON]

decrypt_mapping(encrypted_path: Path, password: str) -> Dict
    Decrypts and returns mapping
```

---

## Data Flow

### Complete Workflow

```
1. User uploads Excel file
   ↓
2. FileHandler.validate_file()
   ↓ (if valid)
3. FileHandler.load_excel() → pd.DataFrame
   ↓
4. PIIDetector.scan_dataframe()
   ↓
5. User reviews detected columns
   User selects columns to anonymize
   ↓
6. Anonymizer.anonymize_dataframe()
   ├─ For each selected column:
   │  ├─ Get unique values
   │  ├─ Map to anonymous IDs
   │  └─ Replace in DataFrame
   ↓
7. FileHandler.save_excel() → anonymized file
   ↓
8. (Optional) CryptoHandler.encrypt_mapping()
   ↓
9. User downloads:
   ├─ Anonymized Excel file
   └─ (Optional) Encrypted mapping file
```

### Session State Management (Streamlit)

```python
st.session_state = {
    'step': int,                    # Current UI step (1, 2, or 3)
    'df': pd.DataFrame,             # Original DataFrame
    'pii_results': Dict,            # Detection results
    'selected_columns': Dict,       # {col_name: pii_type}
}
```

---

## Security Considerations

### 1. Local-First Architecture
- **No Network Calls:** All processing happens locally
- **No External APIs:** No data sent to external services
- **No Telemetry:** No usage tracking or analytics

### 2. Data Protection
- **In-Memory Only:** Data stored in memory during processing
- **Temporary Files:** Cleaned up after session
- **Secure Delete:** Overwrite before deletion (optional)

### 3. Mapping File Security
- **Encryption:** AES-256 with password
- **Key Derivation:** PBKDF2 (100k iterations)
- **Storage:** User responsible for secure storage

### 4. Code Security
- **Input Validation:** All user inputs validated
- **Error Handling:** No sensitive data in error messages
- **Logging:** PII never logged

### 5. Compliance
- **GDPR:** Article 4(5) Pseudonymization
- **Privacy by Design:** Article 25
- **Israeli Privacy Law:** Amendment 13

---

## Performance & Scalability

### MVP Constraints
- Max file size: 10MB
- Max rows: ~50,000 (typical)
- Processing time: <30 seconds

### Performance Optimizations

1. **Sampling:** PII detection samples first 100 rows
2. **Vectorization:** pandas operations (no Python loops)
3. **Lazy Loading:** Data loaded only when needed
4. **Chunking (future):** For larger files

### Bottlenecks (Identified)

| Operation | Estimated Time | Optimization Strategy |
|-----------|----------------|----------------------|
| Excel Loading | 2-5s | Acceptable for MVP |
| PII Detection | 10-20s | Sampling + caching |
| Anonymization | 5-10s | Vectorized operations |
| Excel Saving | 2-5s | Acceptable for MVP |

---

## Testing Strategy

### Unit Tests

```python
tests/
├── test_file_handler.py
│   ├── test_validate_file_valid()
│   ├── test_validate_file_too_large()
│   ├── test_load_excel_valid()
│   └── test_save_excel()
├── test_pii_detector.py
│   ├── test_detect_israeli_id_valid()
│   ├── test_detect_israeli_id_invalid()
│   ├── test_detect_email()
│   └── test_scan_dataframe()
├── test_anonymizer.py
│   ├── test_anonymize_value()
│   ├── test_consistency()
│   └── test_anonymize_dataframe()
└── test_crypto_handler.py
    ├── test_encrypt_decrypt()
    └── test_wrong_password()
```

### Integration Tests
- End-to-end workflow with sample data
- Verify no PII remains after anonymization
- Validate Excel format preservation

### Test Data
- Faker-generated PII (safe for testing)
- Never use real sensitive data

---

## Deployment

### Local Installation

```bash
# Clone repository
git clone https://github.com/niravivi-dotcom/safeshare-anonymizer.git

# Install dependencies
pip install -r requirements.txt

# Download NLP models (future)
python -m spacy download en_core_web_sm
python -m spacy download he_core_news_sm

# Run application
streamlit run app.py
```

### System Requirements
- Python 3.9+
- 4GB RAM (8GB recommended)
- 500MB disk space
- Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+)

### Future Deployment Options
- **Desktop App:** PyInstaller .exe (no Python required)
- **Docker:** Containerized deployment
- **Cloud:** SaaS version (enterprise security)

---

## Future Enhancements

### Phase 2 (v0.2)
- Advanced NLP with Presidio + spaCy
- Hebrew name detection
- Address detection
- Bank account patterns
- Validation scan (detect remaining PII)

### Phase 3 (v0.3)
- CSV support
- Word (.docx) support
- PDF support (with OCR)
- Batch processing

### Phase 4 (v0.4+)
- De-anonymization UI
- Partial masking option
- Fake data generation (Faker)
- API for integrations
- Desktop app (.exe)
- Cloud SaaS version

---

## References

- [Microsoft Presidio Documentation](https://microsoft.github.io/presidio/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [GDPR Guidelines on Pseudonymization](https://gdpr-info.eu/)

---

## Changelog

### v0.1.0 (Current - MVP)
- Initial release
- Excel support (.xlsx, .xls)
- Basic PII detection (ID, email, phone)
- Consistent anonymization
- Encrypted mapping files
- Streamlit UI

---

**Document Maintained By:** Avivi Solutions  
**Last Updated:** February 2026  
**Next Review:** After MVP completion
