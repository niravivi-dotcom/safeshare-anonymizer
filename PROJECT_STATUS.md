# SafeShare - Project Status

> **Last Updated:** 2026-02-01 19:30
> **Current Version:** 0.4.0
> **Status:** MVP Working - Multi-sheet Support Added

---

## IMPORTANT: Update Instructions for AI Assistants

**This file is the single source of truth for project status.**

### When to Update This File
Update this file IMMEDIATELY after:
1. Adding a new feature
2. Fixing a bug
3. Changing file structure
4. Adding/removing dependencies
5. Completing a task from "Next Steps"
6. Discovering a new issue

### What to Update
| Change Type | Sections to Update |
|-------------|-------------------|
| New feature | `Current State`, `Recent Changes` |
| Bug fix | `Known Issues`, `Recent Changes` |
| File added/removed | `File Structure`, `Recent Changes` |
| Dependency change | `Dependencies`, `Recent Changes` |
| Task completed | `Next Steps` (mark with ✅), `Recent Changes` |
| New bug found | `Known Issues` |

### How to Update `Recent Changes`
Add new entry at TOP with format:
```markdown
### YYYY-MM-DD - Version X.X.X
- **What changed** (brief description)
  - Detail 1
  - Detail 2
```

### Before Starting Work
1. Read this entire file first
2. Check `Current State` to understand what works
3. Check `Next Steps` for priorities
4. Check `Known Issues` for existing problems

---

## Quick Start

```bash
cd "C:\Users\nirav\Avivi-Solutions\ProdDev - SafeShare"
venv\Scripts\activate
streamlit run app_simple.py --server.port 8506
```

**Note:** Port 8506 recommended (8501-8505 may be in use)

---

## Current State

### What's Working
| Feature | Status | Notes |
|---------|--------|-------|
| **Multi-Sheet Excel Support** | ✅ Working | Select & process multiple sheets |
| **Type-Specific Formats** | ✅ Working | 7 distinct formats (ID, PERSON, etc.) |
| File Upload (Excel/CSV) | ✅ Working | Up to 10MB |
| Israeli ID Detection | ✅ Working | 9-digit with Luhn validation |
| Email Detection | ✅ Working | Standard regex |
| Phone Detection | ✅ Working | Israeli format (05x, 0x) |
| Hebrew Name Detection | ✅ Working | Dictionary + heuristics |
| Column Name Heuristics | ✅ Working | Auto-detect by column name |
| Consistent Anonymization | ✅ Working | Same value = same code |
| Download Anonymized File | ✅ Working | Multi-sheet Excel output |
| Streamlit UI | ✅ Working | 3-step workflow |
| Unit Tests | ✅ Working | 69 tests passing |

### What's Not Working / Missing
| Feature | Status | Priority |
|---------|--------|----------|
| English Name Detection | ❌ Not implemented | Low |
| Address Detection | ❌ Not implemented | Medium |
| Word/PDF Support | ❌ Not implemented | Phase 2 |
| .exe Packaging | ❌ Not done | High |
| De-anonymization UI | ❌ Not implemented | Low |
| Batch Processing | ❌ Not implemented | Phase 3 |

---

## File Structure

```
ProdDev - SafeShare/
├── app_simple.py          # Main app (USE THIS) - v0.3
├── app.py                 # Full version (more features, more deps)
├── src/
│   ├── __init__.py
│   ├── file_handler.py    # Excel I/O
│   ├── pii_detector.py    # PII detection (updated with Hebrew names)
│   ├── anonymizer.py      # Anonymization logic
│   ├── crypto_handler.py  # AES-256 encryption
│   └── hebrew_names.py    # Hebrew names dictionary (NEW)
├── tests/
│   ├── test_pii_detector.py   # 28 tests
│   ├── test_anonymizer.py     # 20 tests
│   └── test_hebrew_names.py   # 21 tests
├── data/
│   └── sample_files/      # Test files
├── docs/                  # Documentation
├── venv/                  # Python virtual environment
├── requirements.txt       # Dependencies
├── README.md             # User documentation
├── TECHNICAL_DESIGN.md   # Architecture docs
└── PROJECT_STATUS.md     # THIS FILE
```

---

## Recent Changes

### 2026-02-01 Evening - Version 0.4.0 (Cursor AI)
- **Added multi-sheet Excel support**
  - Users can now select which sheets to anonymize
  - Each sheet processed separately
  - Combined output with all sheets
- **Improved anonymization formats** (v0.2 changes)
  - Added 7 distinct formats: ID, PERSON, ADDRESS, PHONE, EMAIL, ACCOUNT, OTHER
  - Clear prefixes instead of generic ID-XXX
  - Auto-detection of column types by name + content
- **Enhanced UI**
  - Type selection with descriptions
  - Preview of anonymization format
  - Summary by type
  - Validation section

### 2026-02-01 Afternoon - Version 0.3.0 (Claude Code)
- **Added Hebrew name detection**
  - New `src/hebrew_names.py` with ~300 common names
  - Updated `pii_detector.py` with name detection methods
  - Updated `app_simple.py` with inline name detection
- **Added unit tests**
  - Created `tests/test_pii_detector.py`
  - Created `tests/test_anonymizer.py`
  - Created `tests/test_hebrew_names.py`
  - All 69 tests passing
- **Updated anonymizer**
  - Added `hebrew_name` to prefix map

### Previous - Version 0.2.0
- Basic PII detection (ID, email, phone)
- Streamlit UI with 3-step workflow
- Excel/CSV support
- Consistent anonymization

---

## Dependencies

### Installed in venv
- streamlit 1.53+
- pandas 2.3+
- openpyxl 3.1+
- pytest 9.0+
- loguru 0.7+

### To Install
```bash
venv\Scripts\pip install -r requirements.txt
```

---

## Running Tests

```bash
cd "C:\Users\nirav\Avivi-Solutions\ProdDev - SafeShare"
venv\Scripts\python -m pytest tests/ -v
```

Expected: **69 tests passed**

---

## Next Steps (Prioritized)

### High Priority
1. [ ] Test multi-sheet functionality with real files
2. [ ] Create .exe with PyInstaller for easy distribution
3. [ ] Test with real customer data
4. [ ] Fix any bugs found in testing

### Medium Priority
4. [ ] Add more Hebrew names to dictionary
5. [ ] Improve UX (better error messages, RTL support)
6. [ ] Add address detection

### Low Priority
7. [ ] Word document support
8. [ ] PDF support
9. [ ] De-anonymization UI
10. [ ] Batch processing

---

## Known Issues

| Issue | Severity | Workaround |
|-------|----------|------------|
| Hebrew console output encoding | Low | Use file output instead |
| Multiple Streamlit instances conflict | Low | Use different ports |

---

## Contacts

- **Project Owner:** Avivi Solutions
- **Repository:** Local only (not on GitHub yet)

---

## Notes for AI Assistants (Claude/Cursor)

### Critical Rules
1. **READ THIS FILE FIRST** before any work
2. **UPDATE THIS FILE** after any significant change
3. **Main app file:** `app_simple.py` (NOT `app.py`)
4. **Always use venv:** `venv\Scripts\python` or activate first

### Code Locations
| Component | Location | Notes |
|-----------|----------|-------|
| Main UI | `app_simple.py` | Streamlit app, standalone |
| Hebrew Names (inline) | `app_simple.py` lines 17-38 | Used by app |
| Hebrew Names (module) | `src/hebrew_names.py` | Full dictionary, used by tests |
| PII Detection | `src/pii_detector.py` | Class-based detection |
| Anonymization | `src/anonymizer.py` | Mapping logic |
| Tests | `tests/test_*.py` | 69 tests total |

### Common Commands
```bash
# Activate venv
cd "C:\Users\nirav\Avivi-Solutions\ProdDev - SafeShare"
venv\Scripts\activate

# Run app
streamlit run app_simple.py --server.port 8510

# Run tests
venv\Scripts\python -m pytest tests/ -v

# Check syntax
venv\Scripts\python -c "import ast; ast.parse(open('app_simple.py', encoding='utf-8').read()); print('OK')"
```

### Port Conflicts
Default port 8501 may be in use. Use `--server.port 8510` or higher.

### Sync Between Claude and Cursor
- Both AI assistants work on this project
- This file ensures both have the same context
- **Always update `Recent Changes` with date and details**
- If you see outdated info, update it before proceeding
