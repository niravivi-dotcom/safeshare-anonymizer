"""
SafeShare - Main Streamlit Application
Local-first data anonymization tool
"""

import streamlit as st
from pathlib import Path
import pandas as pd
from loguru import logger
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from file_handler import FileHandler, get_file_info
from pii_detector import PIIDetector
from anonymizer import Anonymizer
from crypto_handler import CryptoHandler


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="SafeShare - Data Anonymization",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Custom CSS
# ============================================================================

st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        color: #856404;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        color: #0c5460;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# Session State Initialization
# ============================================================================

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'df' not in st.session_state:
    st.session_state.df = None
if 'pii_results' not in st.session_state:
    st.session_state.pii_results = None
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = {}

# ============================================================================
# Header
# ============================================================================

st.markdown('<div class="main-header">🔒 SafeShare</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Local Data Anonymization Tool</div>', unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.header("📋 About")
    st.info("""
    **SafeShare** helps you anonymize sensitive data in Excel files 
    for safe sharing with AI tools and external parties.
    
    ✅ 100% Local - No data uploaded  
    ✅ Smart PII Detection  
    ✅ Consistent Anonymization  
    ✅ GDPR Compliant
    """)
    
    st.markdown("---")
    
    st.header("🚀 Quick Guide")
    st.markdown("""
    1. **Upload** Excel file
    2. **Review** detected PII
    3. **Anonymize** with one click
    4. **Download** safe file
    """)
    
    st.markdown("---")
    
    st.markdown("**Version:** 0.1.0 (MVP)")
    st.markdown("[GitHub](https://github.com/niravivi-dotcom/safeshare-anonymizer)")

# ============================================================================
# Main Content
# ============================================================================

# Step 1: File Upload
if st.session_state.step == 1:
    st.header("📁 Step 1: Upload File")
    
    st.markdown('<div class="info-box">Upload your Excel file containing sensitive data. All processing happens locally on your computer.</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file (.xlsx, .xls)",
        type=['xlsx', 'xls'],
        help="Maximum file size: 10MB (MVP limit)"
    )
    
    if uploaded_file is not None:
        try:
            # Save temporarily
            temp_path = Path("temp") / uploaded_file.name
            temp_path.parent.mkdir(exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Validate
            is_valid, error_msg = FileHandler.validate_file(temp_path)
            
            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                # Load file
                with st.spinner("Loading file..."):
                    df = FileHandler.load_excel(temp_path)
                    st.session_state.df = df
                
                # Show file info
                file_info = get_file_info(df)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Rows", file_info['rows'])
                col2.metric("Columns", file_info['columns'])
                col3.metric("Size", f"{file_info['memory_usage_mb']:.2f} MB")
                
                # Show preview
                st.subheader("📊 Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Next button
                if st.button("🔍 Scan for PII →", type="primary", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")

# Step 2: PII Detection
elif st.session_state.step == 2:
    st.header("🔍 Step 2: Review Detected PII")
    
    if st.session_state.df is None:
        st.warning("No file loaded. Please go back to Step 1.")
        if st.button("← Back to Upload"):
            st.session_state.step = 1
            st.rerun()
    else:
        # Perform PII detection
        if st.session_state.pii_results is None:
            with st.spinner("Scanning for PII... This may take a moment."):
                detector = PIIDetector()
                pii_results = detector.scan_dataframe(st.session_state.df)
                st.session_state.pii_results = pii_results
        
        pii_results = st.session_state.pii_results
        
        if not pii_results:
            st.success("✅ No PII detected! Your file appears to be clean.")
            st.info("You can still proceed to manually select columns to anonymize.")
        else:
            total_fields = sum(
                sum(result['counts'].values()) 
                for result in pii_results.values()
            )
            
            st.markdown(f'<div class="warning-box">⚠️ Found approximately <strong>{total_fields}</strong> sensitive fields in <strong>{len(pii_results)}</strong> columns.</div>', unsafe_allow_html=True)
        
        # Show detected columns
        st.subheader("Select Columns to Anonymize")
        
        for col, result in pii_results.items():
            with st.expander(f"📌 {col} - {', '.join(result['types']).replace('_', ' ').title()}", expanded=True):
                # Checkbox to include this column
                include = st.checkbox(
                    f"Anonymize this column",
                    value=True,
                    key=f"cb_{col}"
                )
                
                if include:
                    # Show PII type selector
                    pii_type = st.selectbox(
                        "PII Type:",
                        options=['israeli_id', 'email', 'phone', 'name', 'address'],
                        index=['israeli_id', 'email', 'phone', 'name', 'address'].index(result['types'][0]) if result['types'][0] in ['israeli_id', 'email', 'phone', 'name', 'address'] else 0,
                        key=f"type_{col}"
                    )
                    
                    # Show samples
                    samples = detector.get_sample_values(st.session_state.df[col], n=3)
                    st.markdown(f"**Sample values:** `{', '.join(samples)}`")
                    
                    # Store selection
                    st.session_state.selected_columns[col] = pii_type
                else:
                    # Remove from selection
                    if col in st.session_state.selected_columns:
                        del st.session_state.selected_columns[col]
        
        # Manual column addition
        st.subheader("➕ Add Column Manually")
        remaining_cols = [c for c in st.session_state.df.columns if c not in pii_results]
        if remaining_cols:
            manual_col = st.selectbox("Select column:", [""] + remaining_cols)
            if manual_col:
                manual_type = st.selectbox("PII Type:", ['israeli_id', 'email', 'phone', 'name', 'address'])
                if st.button("Add to anonymization list"):
                    st.session_state.selected_columns[manual_col] = manual_type
                    st.success(f"✅ Added {manual_col}")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Upload"):
                st.session_state.step = 1
                st.session_state.pii_results = None
                st.rerun()
        
        with col2:
            if st.session_state.selected_columns:
                if st.button("🔒 Anonymize Now →", type="primary", use_container_width=True):
                    st.session_state.step = 3
                    st.rerun()
            else:
                st.warning("Please select at least one column to anonymize")

# Step 3: Anonymization
elif st.session_state.step == 3:
    st.header("🔒 Step 3: Anonymize & Download")
    
    if st.session_state.df is None or not st.session_state.selected_columns:
        st.warning("Something went wrong. Please start over.")
        if st.button("← Start Over"):
            st.session_state.step = 1
            st.rerun()
    else:
        st.info(f"Anonymizing {len(st.session_state.selected_columns)} columns...")
        
        # Settings
        with st.expander("⚙️ Settings", expanded=True):
            save_mapping = st.checkbox("Save encrypted mapping file (allows de-anonymization later)", value=False)
            if save_mapping:
                mapping_password = st.text_input("Mapping file password:", type="password")
            
            delete_original = st.checkbox("Delete original file after anonymization", value=False)
            if delete_original:
                st.warning("⚠️ Original file will be permanently deleted!")
        
        # Anonymize button
        if st.button("🚀 Start Anonymization", type="primary", use_container_width=True):
            try:
                with st.spinner("Anonymizing data..."):
                    # Perform anonymization
                    anonymizer = Anonymizer()
                    df_anon = anonymizer.anonymize_dataframe(
                        st.session_state.df,
                        st.session_state.selected_columns,
                        deterministic=False
                    )
                    
                    # Get statistics
                    stats = anonymizer.get_statistics()
                    
                    # Show results
                    st.success("✅ Anonymization complete!")
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Columns Anonymized", len(st.session_state.selected_columns))
                    col2.metric("Values Replaced", stats['total_values_mapped'])
                    
                    # Show preview
                    st.subheader("📊 Anonymized Data Preview")
                    st.dataframe(df_anon.head(10), use_container_width=True)
                    
                    # Save anonymized file
                    output_path = Path("temp") / "anonymized_output.xlsx"
                    FileHandler.save_excel(df_anon, output_path)
                    
                    # Download button
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Anonymized File",
                            data=f,
                            file_name="anonymized_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    # Save mapping if requested
                    if save_mapping and mapping_password:
                        mapping_path = Path("temp") / "mapping.enc"
                        CryptoHandler.encrypt_mapping(
                            anonymizer.get_mappings(),
                            mapping_password,
                            mapping_path
                        )
                        
                        with open(mapping_path, "rb") as f:
                            st.download_button(
                                label="🔑 Download Encrypted Mapping",
                                data=f,
                                file_name="anonymization_mapping.enc",
                                mime="application/octet-stream",
                                use_container_width=True
                            )
                    
                    st.markdown("---")
                    st.markdown('<div class="success-box">✅ Your file is now safe to share with AI tools, consultants, or external parties!</div>', unsafe_allow_html=True)
                    
                    # Start over button
                    if st.button("🔄 Anonymize Another File"):
                        st.session_state.step = 1
                        st.session_state.df = None
                        st.session_state.pii_results = None
                        st.session_state.selected_columns = {}
                        st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error during anonymization: {str(e)}")
                logger.error(f"Anonymization error: {e}")

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    Made with ❤️ by Avivi Solutions | 
    <a href="https://github.com/niravivi-dotcom/safeshare-anonymizer" target="_blank">GitHub</a> | 
    Version 0.1.0 (MVP)
</div>
""", unsafe_allow_html=True)
