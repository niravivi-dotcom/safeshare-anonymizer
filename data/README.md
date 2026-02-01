# Data Directory

This directory contains sample data files for testing SafeShare.

## Structure

- `sample_files/` - Example Excel files with fake PII for testing

## ⚠️ Important Security Note

**NEVER commit real sensitive data to this repository!**

The `.gitignore` is configured to exclude:
- All `.xlsx` and `.xls` files (except in `sample_files/`)
- Mapping files
- Any file in `sensitive/` or `real_data/` directories

## Creating Test Data

To create test data for development:

```python
from faker import Faker
import pandas as pd

fake = Faker(['he_IL', 'en_US'])

# Generate fake data
data = {
    'Name': [fake.name() for _ in range(100)],
    'ID': [fake.random_number(digits=9) for _ in range(100)],
    'Email': [fake.email() for _ in range(100)],
    'Phone': [fake.phone_number() for _ in range(100)],
}

df = pd.DataFrame(data)
df.to_excel('data/sample_files/test_data.xlsx', index=False)
```

## Testing Workflow

1. Place sample files in `sample_files/`
2. Run SafeShare on them
3. Verify anonymization worked correctly
4. Check no PII remains in output
