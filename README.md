# 🔒 SafeShare - Local Data Anonymization Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Local-first tool to anonymize PII in Excel files for safe sharing with AI and external parties**

Share your sensitive data with ChatGPT, consultants, or colleagues without exposing personal information. SafeShare runs entirely on your local machine - **zero data leaves your computer during anonymization**.

---

## 🎯 Why SafeShare?

### The Problem
You have Excel files with sensitive data (IDs, names, emails, phone numbers) and want to:
- ✅ Analyze them with ChatGPT or other AI tools
- ✅ Share with external consultants
- ✅ Create training datasets
- ✅ Use for development/testing

But you **can't** because of:
- ❌ Privacy laws (GDPR, local regulations)
- ❌ Legal liability
- ❌ Company policies
- ❌ Customer trust

### The Solution
SafeShare **automatically detects and replaces** all PII with consistent anonymous identifiers:
- `123456789` (ID) → `ID-001` (same ID always becomes `ID-001`)
- `David Cohen` → `PERSON-042`
- `david@email.com` → `EMAIL-005@anon.com`
- `050-1234567` → `PHONE-012`

**Result:** A clean, analyzable file with **zero personal information** that maintains all relationships and patterns.

---

## ✨ Key Features

### 🏠 100% Local
- All processing happens on **your computer**
- **No internet connection** required (after installation)
- **No data uploaded** to any server
- Complete privacy and control

### 🧠 Smart Detection
- **Automatic PII detection** using Microsoft Presidio + custom patterns
- Supports **Hebrew & English**
- Detects: IDs, names, emails, phones, addresses, bank accounts
- Manual review & editing before anonymization

### 🔄 Consistent Anonymization
- Same value = same anonymous ID throughout the file
- Preserves data relationships for meaningful analysis
- Maintains data structure and format

### 🔐 Optional Reversibility
- Encrypted mapping file (AES-256)
- Allows de-anonymization with password (future feature)

### 📊 Format Support
- **MVP:** Excel (.xlsx, .xls) up to 10MB
- **Future:** CSV, Word, PDF, larger files

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)
- 4GB RAM (8GB recommended)
- 500MB disk space

### Installation

```bash
# Clone the repository
git clone https://github.com/niravivi-dotcom/safeshare-anonymizer.git
cd safeshare-anonymizer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy models
python -m spacy download en_core_web_sm
python -m spacy download he_core_news_sm
```

### Usage

```bash
# Run the app
streamlit run app.py
```

Then:
1. Open your browser to `http://localhost:8501`
2. Drag & drop your Excel file
3. Review detected PII fields
4. Click "Anonymize Now"
5. Download your anonymized file

**That's it! 2 minutes from sensitive to safe.** ⚡

---

## 📖 How It Works

```
┌─────────────────────────────────────────────────────────┐
│  1. Upload Excel file (stays local)                     │
│     ↓                                                    │
│  2. Scan & detect PII (Presidio + Regex)                │
│     ↓                                                    │
│  3. Show preview → User confirms                         │
│     ↓                                                    │
│  4. Replace values consistently                          │
│     • 123456789 → ID-001 (every occurrence)             │
│     • Same logic for names, emails, etc.                │
│     ↓                                                    │
│  5. Generate outputs:                                    │
│     • Anonymized Excel file                             │
│     • Encrypted mapping file (optional)                 │
│     ↓                                                    │
│  6. Secure delete original (with user consent)          │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ Project Structure

```
safeshare-anonymizer/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── app.py                      # Streamlit main application
├── TECHNICAL_DESIGN.md         # Technical documentation
├── PRD_Data_Anonymization_Tool.html  # Product Requirements Document
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── file_handler.py         # Excel read/write operations
│   ├── pii_detector.py         # PII detection engine
│   ├── anonymizer.py           # Anonymization logic
│   └── crypto_handler.py       # Encryption/decryption
│
├── tests/                      # Unit & integration tests
│   ├── __init__.py
│   ├── test_file_handler.py
│   ├── test_pii_detector.py
│   └── test_anonymizer.py
│
└── data/                       # Sample data & outputs
    ├── sample_files/           # Example Excel files for testing
    └── README.md               # Data directory documentation
```

---

## 🛡️ Security & Privacy

### Privacy by Design
- ✅ **Local-first:** No data transmission during anonymization
- ✅ **Zero Trust:** Assumes all fields may contain PII
- ✅ **Secure deletion:** Original files securely wiped (optional)
- ✅ **Encrypted mapping:** AES-256 with user-chosen password
- ✅ **No logs:** Sensitive data never written to logs

### Compliance
- ✅ **GDPR compliant:** Pseudonymization (Article 4(5))
- ✅ **Privacy by Design:** Article 25
- ✅ **Israeli Privacy Law:** Amendment 13 compliant

### Best Practices
1. **Always review** detected PII before confirming
2. **Manually check** the anonymized file before sharing
3. **Store mapping files** separately from anonymized data
4. **Keep backups** of original files in secure location
5. **Test first** with non-critical data

---

## 🗺️ Roadmap

### ✅ MVP (v0.1) - Weeks 1-3 [Current]
- [x] Excel support (.xlsx, .xls)
- [x] Hebrew + English PII detection
- [x] Consistent anonymization
- [x] Streamlit UI
- [ ] Basic documentation
- [ ] Initial release

### 🔄 Phase 2 (v0.2) - Weeks 4-6
- [ ] Enhanced UX (animations, error messages)
- [ ] Validation (scan anonymized file for remaining PII)
- [ ] Performance optimization (up to 50MB files)
- [ ] Beta user testing

### 🚀 Phase 3 (v0.3) - Weeks 7-10
- [ ] CSV support
- [ ] Word (.docx) support
- [ ] PDF support (OCR optional)
- [ ] Batch processing (multiple files)

### 🌟 Future
- [ ] De-anonymization UI
- [ ] Additional anonymization methods (partial masking, fake data)
- [ ] API for integrations
- [ ] Desktop app (.exe) - no Python required
- [ ] Cloud version (SaaS with enterprise security)

---

## 🧪 Development

### Setup Development Environment

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Code formatting
black src/ tests/ app.py

# Linting
flake8 src/ tests/ app.py
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_pii_detector.py

# With coverage
pytest --cov=src tests/
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Guidelines
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**TL;DR:** You can use, modify, and distribute this software freely. Just keep the license notice.

---

## 📞 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/niravivi-dotcom/safeshare-anonymizer/issues)
- **Email:** [Contact via GitHub]
- **Documentation:** See `TECHNICAL_DESIGN.md` for architecture details

---

## ⚠️ Disclaimer

**Important:** While SafeShare uses advanced detection methods, no automated tool is 100% perfect. Users are responsible for:
- Reviewing detection results before anonymization
- Manually verifying anonymized files before external sharing
- Complying with applicable privacy laws and regulations

**Recommendation:** Always test with non-critical data first and perform manual spot-checks.

---

## 🙏 Acknowledgments

Built with these amazing open-source projects:
- [Microsoft Presidio](https://github.com/microsoft/presidio) - PII detection framework
- [Streamlit](https://streamlit.io/) - UI framework
- [spaCy](https://spacy.io/) - NLP for Hebrew/English
- [pandas](https://pandas.pydata.org/) - Data manipulation
- [cryptography](https://cryptography.io/) - Encryption

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/niravivi-dotcom/safeshare-anonymizer?style=social)
![GitHub forks](https://img.shields.io/github/forks/niravivi-dotcom/safeshare-anonymizer?style=social)
![GitHub issues](https://img.shields.io/github/issues/niravivi-dotcom/safeshare-anonymizer)
![GitHub last commit](https://img.shields.io/github/last-commit/niravivi-dotcom/safeshare-anonymizer)

---

<div align="center">
Made with ❤️ by <a href="https://github.com/niravivi-dotcom">Avivi Solutions</a>
<br>
<sub>Empowering safe data sharing since 2026</sub>
</div>
