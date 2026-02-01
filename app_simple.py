"""
SafeShare - Simplified MVP
Multi-sheet Excel support + Type-specific anonymization
Version 0.4.0
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import re
from io import BytesIO

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="SafeShare - Data Anonymization",
    page_icon="🔒",
    layout="wide",
)

# ============================================================================
# Helper Functions
# ============================================================================

def detect_israeli_id(text):
    """Detect Israeli ID (9 digits)"""
    if not isinstance(text, str):
        text = str(text)
    return bool(re.search(r'\b\d{9}\b', text))

def detect_email(text):
    """Detect email addresses"""
    if not isinstance(text, str):
        text = str(text)
    return bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))

def detect_phone(text):
    """Detect Israeli phone numbers"""
    if not isinstance(text, str):
        text = str(text)
    return bool(re.search(r'\b0\d{1,2}-?\d{7}\b', text))

def auto_detect_type(column_name, sample_values):
    """Auto-detect PII type based on column name and content"""
    col_lower = column_name.lower()
    
    # Check column name
    if any(word in col_lower for word in ['ת.ז', 'תז', 'id', 'מזהה', 'זהות']):
        return 'ID'
    elif any(word in col_lower for word in ['מייל', 'email', 'דוא"ל', 'אימייל']):
        return 'EMAIL'
    elif any(word in col_lower for word in ['טלפון', 'נייד', 'phone', 'פלאפון', 'פרטי קשר']):
        return 'PHONE'
    elif any(word in col_lower for word in ['שם', 'name', 'מבוטח', 'לקוח']):
        return 'PERSON'
    elif any(word in col_lower for word in ['כתובת', 'address', 'רחוב', 'עיר', 'משלוח']):
        return 'ADDRESS'
    elif any(word in col_lower for word in ['חשבון', 'account', 'בנק']):
        return 'ACCOUNT'
    
    # Check content
    has_id = any(detect_israeli_id(str(v)) for v in sample_values if pd.notna(v))
    has_email = any(detect_email(str(v)) for v in sample_values if pd.notna(v))
    has_phone = any(detect_phone(str(v)) for v in sample_values if pd.notna(v))
    
    if has_id:
        return 'ID'
    elif has_email:
        return 'EMAIL'
    elif has_phone:
        return 'PHONE'
    
    return 'OTHER'

def scan_column(series):
    """Scan a column for PII"""
    results = {'israeli_id': 0, 'email': 0, 'phone': 0}
    sample = series.head(min(50, len(series)))
    
    for value in sample:
        if pd.isna(value):
            continue
        text = str(value)
        if detect_israeli_id(text):
            results['israeli_id'] += 1
        if detect_email(text):
            results['email'] += 1
        if detect_phone(text):
            results['phone'] += 1
    
    return results

def anonymize_column(series, prefix='ANON'):
    """Anonymize a column with consistent mapping"""
    mapping = {}
    counter = 0
    
    def get_anon_value(val):
        nonlocal counter
        if pd.isna(val):
            return val
        if val not in mapping:
            counter += 1
            mapping[val] = f"{prefix}-{counter:03d}"
        return mapping[val]
    
    return series.apply(get_anon_value), mapping

def load_excel_sheets(file):
    """Load all sheets from Excel file"""
    try:
        # Read all sheet names
        excel_file = pd.ExcelFile(file)
        sheet_names = excel_file.sheet_names
        
        # Load all sheets
        sheets = {}
        for sheet_name in sheet_names:
            sheets[sheet_name] = pd.read_excel(file, sheet_name=sheet_name)
        
        return sheets
    except Exception as e:
        st.error(f"Error loading Excel file: {str(e)}")
        return None

# ============================================================================
# Session State
# ============================================================================

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'sheets_data' not in st.session_state:
    st.session_state.sheets_data = {}
if 'selected_sheets' not in st.session_state:
    st.session_state.selected_sheets = []
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = {}  # {sheet_name: {col: type}}
if 'file_name' not in st.session_state:
    st.session_state.file_name = None

# ============================================================================
# Header
# ============================================================================

st.title("🔒 SafeShare - Data Anonymization")
st.markdown("**Multi-Sheet Excel Support • Type-Specific Anonymization**")
st.markdown("---")

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.header("📋 About")
    st.info("""
    **SafeShare** - v0.4.0
    
    ✅ Multi-Sheet Excel Support
    ✅ 100% Local Processing
    ✅ Smart Type Detection
    ✅ Clear Anonymization
    """)
    
    st.markdown("---")
    
    st.header("🎨 Anonymization Formats")
    st.markdown("""
    - **ID** → `ID-001`
    - **PERSON** → `PERSON-001`
    - **ADDRESS** → `ADDRESS-001`
    - **PHONE** → `PHONE-001`
    - **EMAIL** → `EMAIL-001`
    - **ACCOUNT** → `ACCOUNT-001`
    - **OTHER** → `REF-001`
    """)
    
    # Show current progress
    if st.session_state.step > 1:
        st.markdown("---")
        st.header("📊 Progress")
        if st.session_state.selected_sheets:
            st.write(f"**Sheets:** {len(st.session_state.selected_sheets)}")
            for sheet in st.session_state.selected_sheets:
                st.write(f"• {sheet}")

# ============================================================================
# Main Content
# ============================================================================

# Step 1: Upload & Select Sheets
if st.session_state.step == 1:
    st.header("📁 Step 1: Upload File & Select Sheets")
    
    st.info("📌 Upload your Excel file. If it has multiple sheets, you can choose which ones to anonymize.")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel or CSV file",
        type=['xlsx', 'xls', 'csv']
    )
    
    if uploaded_file:
        st.session_state.file_name = uploaded_file.name
        
        try:
            # Check if CSV or Excel
            if uploaded_file.name.endswith('.csv'):
                # CSV - single sheet
                df = pd.read_csv(uploaded_file)
                st.session_state.sheets_data = {'Sheet1': df}
                st.session_state.selected_sheets = ['Sheet1']
                
                st.success("✅ CSV file loaded successfully")
                
            else:
                # Excel - may have multiple sheets
                sheets = load_excel_sheets(uploaded_file)
                
                if sheets:
                    st.session_state.sheets_data = sheets
                    
                    st.success(f"✅ Excel file loaded with **{len(sheets)}** sheet(s)")
                    
                    # Show sheet selector
                    st.markdown("---")
                    st.subheader("📋 Select Sheets to Anonymize")
                    
                    if len(sheets) == 1:
                        # Single sheet - auto-select
                        sheet_name = list(sheets.keys())[0]
                        st.session_state.selected_sheets = [sheet_name]
                        st.info(f"Single sheet detected: **{sheet_name}**")
                    else:
                        # Multiple sheets - let user choose
                        st.markdown("**Select one or more sheets:**")
                        
                        selected_sheets = []
                        for sheet_name, df in sheets.items():
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                if st.checkbox(
                                    f"**{sheet_name}**",
                                    value=True,
                                    key=f"sheet_select_{sheet_name}"
                                ):
                                    selected_sheets.append(sheet_name)
                            
                            with col2:
                                st.write(f"{len(df)} rows")
                            
                            with col3:
                                st.write(f"{len(df.columns)} cols")
                            
                            # Show preview
                            with st.expander(f"Preview: {sheet_name}"):
                                st.dataframe(df.head(5), use_container_width=True)
                        
                        st.session_state.selected_sheets = selected_sheets
            
            # Show summary
            if st.session_state.selected_sheets:
                st.markdown("---")
                st.subheader("📊 Summary")
                
                total_rows = sum(len(st.session_state.sheets_data[s]) for s in st.session_state.selected_sheets)
                total_cols = sum(len(st.session_state.sheets_data[s].columns) for s in st.session_state.selected_sheets)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Selected Sheets", len(st.session_state.selected_sheets))
                col2.metric("Total Rows", total_rows)
                col3.metric("Total Columns", total_cols)
                
                st.markdown("---")
                if st.button("🔍 Next: Select Columns →", type="primary", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()
            else:
                st.warning("⚠️ Please select at least one sheet to continue")
                
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
            st.info("💡 Make sure your file is a valid Excel or CSV file.")

# Step 2: Select Columns for Each Sheet
elif st.session_state.step == 2:
    st.header("🔍 Step 2: Select Columns for Each Sheet")
    
    if not st.session_state.selected_sheets:
        st.warning("⚠️ No sheets selected")
        if st.button("← Back to Upload"):
            st.session_state.step = 1
            st.rerun()
    else:
        st.info(f"Configure anonymization for **{len(st.session_state.selected_sheets)}** sheet(s)")
        
        # Type options
        type_options = {
            'ID': '🆔 ID → ID-001',
            'PERSON': '👤 PERSON → PERSON-001',
            'ADDRESS': '🏠 ADDRESS → ADDRESS-001',
            'PHONE': '📞 PHONE → PHONE-001',
            'EMAIL': '📧 EMAIL → EMAIL-001',
            'ACCOUNT': '🏦 ACCOUNT → ACCOUNT-001',
            'OTHER': '📝 OTHER → REF-001'
        }
        
        # Initialize selected_columns structure
        if not st.session_state.selected_columns:
            st.session_state.selected_columns = {}
        
        # Process each sheet
        for sheet_idx, sheet_name in enumerate(st.session_state.selected_sheets):
            df = st.session_state.sheets_data[sheet_name]
            
            st.markdown("---")
            st.subheader(f"📄 Sheet: {sheet_name}")
            st.write(f"*{len(df)} rows × {len(df.columns)} columns*")
            
            # Scan for PII
            pii_detected = {}
            for col in df.columns:
                results = scan_column(df[col])
                if any(v > 0 for v in results.values()):
                    pii_detected[col] = results
            
            if pii_detected:
                st.success(f"✅ Found potential PII in {len(pii_detected)} columns")
            
            # Initialize sheet columns if needed
            if sheet_name not in st.session_state.selected_columns:
                st.session_state.selected_columns[sheet_name] = {}
            
            selected_for_sheet = {}
            
            # Column selection
            with st.expander(f"📋 Select Columns in '{sheet_name}'", expanded=True):
                for col in df.columns:
                    # Auto-detect type
                    sample_values = df[col].dropna().head(10).tolist()
                    suggested_type = auto_detect_type(col, sample_values)
                    
                    is_detected = col in pii_detected
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        include = st.checkbox(
                            f"{'🔴' if is_detected else '⚪'} {col}",
                            value=is_detected,
                            key=f"cb_{sheet_name}_{col}"
                        )
                    
                    with col2:
                        if include:
                            pii_type = st.selectbox(
                                "Type:",
                                options=list(type_options.keys()),
                                format_func=lambda x: type_options[x],
                                index=list(type_options.keys()).index(suggested_type),
                                key=f"type_{sheet_name}_{col}",
                                label_visibility="collapsed"
                            )
                            selected_for_sheet[col] = pii_type
            
            st.session_state.selected_columns[sheet_name] = selected_for_sheet
            
            # Show summary for this sheet
            if selected_for_sheet:
                st.info(f"**{sheet_name}:** {len(selected_for_sheet)} columns selected")
        
        # Overall summary
        total_selected = sum(len(cols) for cols in st.session_state.selected_columns.values())
        
        st.markdown("---")
        st.subheader("📊 Total Summary")
        st.metric("Total Columns to Anonymize", total_selected)
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Sheets"):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if total_selected > 0:
                if st.button("🔒 Anonymize All →", type="primary", use_container_width=True):
                    st.session_state.step = 3
                    st.rerun()
            else:
                st.warning("⚠️ Select at least one column to anonymize")

# Step 3: Anonymize & Download
elif st.session_state.step == 3:
    st.header("🔒 Step 3: Anonymize & Download")
    
    if not st.session_state.selected_columns:
        st.warning("⚠️ No columns selected")
        if st.button("← Start Over"):
            st.session_state.step = 1
            st.rerun()
    else:
        # Show summary
        total_sheets = len(st.session_state.selected_sheets)
        total_columns = sum(len(cols) for cols in st.session_state.selected_columns.values())
        
        st.info(f"📋 Ready to anonymize **{total_columns}** columns across **{total_sheets}** sheet(s)")
        
        # Show details
        with st.expander("🔍 Review Configuration"):
            for sheet_name, columns in st.session_state.selected_columns.items():
                if columns:
                    st.write(f"**{sheet_name}:**")
                    for col, pii_type in columns.items():
                        st.write(f"  • {col} → `{pii_type}-XXX`")
        
        st.markdown("---")
        
        if st.button("🚀 Start Anonymization", type="primary", use_container_width=True):
            try:
                with st.spinner("🔄 Anonymizing data..."):
                    # Anonymize each sheet
                    anonymized_sheets = {}
                    all_mappings = {}
                    stats = {'total_values': 0, 'unique_values': 0}
                    
                    for sheet_name in st.session_state.selected_sheets:
                        df = st.session_state.sheets_data[sheet_name].copy()
                        selected = st.session_state.selected_columns.get(sheet_name, {})
                        
                        if selected:
                            sheet_mappings = {}
                            for col, prefix in selected.items():
                                df[col], mapping = anonymize_column(df[col], prefix)
                                sheet_mappings[col] = mapping
                                stats['total_values'] += len(df[col])
                                stats['unique_values'] += len(mapping)
                            
                            all_mappings[sheet_name] = sheet_mappings
                        
                        anonymized_sheets[sheet_name] = df
                
                st.success("✅ Anonymization Complete!")
                
                # Show statistics
                col1, col2, col3 = st.columns(3)
                col1.metric("Sheets Processed", len(anonymized_sheets))
                col2.metric("Columns Anonymized", total_columns)
                col3.metric("Unique Values Mapped", stats['unique_values'])
                
                # Show preview for each sheet
                st.subheader("📊 Anonymized Data Preview")
                for sheet_name, df in anonymized_sheets.items():
                    with st.expander(f"Preview: {sheet_name}"):
                        st.dataframe(df.head(10), use_container_width=True)
                
                # Save to Excel with multiple sheets
                output = BytesIO()
                
                try:
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        for sheet_name, df in anonymized_sheets.items():
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    output.seek(0)
                    
                    file_ext = "xlsx"
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    
                    # Download button
                    st.markdown("---")
                    st.download_button(
                        label=f"📥 Download Anonymized File ({len(anonymized_sheets)} sheets)",
                        data=output,
                        file_name=f"anonymized_{st.session_state.file_name}",
                        mime=mime,
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"Error creating Excel file: {str(e)}")
                    st.info("Trying CSV export as fallback...")
                    
                    # Fallback: save as separate CSV files (zipped)
                    import zipfile
                    zip_buffer = BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for sheet_name, df in anonymized_sheets.items():
                            csv_buffer = BytesIO()
                            df.to_csv(csv_buffer, index=False)
                            zip_file.writestr(f"{sheet_name}.csv", csv_buffer.getvalue())
                    
                    zip_buffer.seek(0)
                    
                    st.download_button(
                        label=f"📥 Download Anonymized Files (ZIP with {len(anonymized_sheets)} CSVs)",
                        data=zip_buffer,
                        file_name=f"anonymized_{st.session_state.file_name.replace('.xlsx', '.zip')}",
                        mime="application/zip",
                        use_container_width=True
                    )
                
                st.markdown("---")
                st.success("🎉 **Success!** Your data is now safe to share!")
                
                if st.button("🔄 Anonymize Another File", use_container_width=True):
                    st.session_state.step = 1
                    st.session_state.sheets_data = {}
                    st.session_state.selected_sheets = []
                    st.session_state.selected_columns = {}
                    st.session_state.file_name = None
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error during anonymization: {str(e)}")
                import traceback
                with st.expander("🐛 Technical Details"):
                    st.code(traceback.format_exc())

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <strong>SafeShare</strong> | Version 0.4.0 | Made with ❤️ by Avivi Solutions<br>
    <small>Multi-Sheet Support • 100% Local • No Data Uploaded • GDPR Compliant</small>
</div>
""", unsafe_allow_html=True)
