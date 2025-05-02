import streamlit as st
import pandas as pd
import os
import datetime
import zipfile
from pathlib import Path
from parser import parse_ticket_xml
from analyzer import analyze_tickets
from conversation_analyzer import generate_insights

# Streamlit settings
st.set_page_config(page_title="Customer Support Ticket Analyzer", page_icon="🎟️", layout="wide")
st.title("🎟️ Customer Support Ticket Analyzer")
st.subheader("Analyze Freshdesk ticket exports and uncover trends easily 🚀")
st.markdown("---")

# Constants
UPLOAD_FOLDER = "uploaded_xmls"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper functions
def save_uploaded_file(uploaded_file):
    with open(os.path.join(UPLOAD_FOLDER, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())

def extract_zip(uploaded_zip):
    zip_path = os.path.join(UPLOAD_FOLDER, uploaded_zip.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_zip.getbuffer())
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(UPLOAD_FOLDER)

# Layout columns
col1, col2 = st.columns([2, 3])

# LEFT: Upload files
with col1:
    st.header("📂 Upload XML or ZIP Files")
    uploaded_files = st.file_uploader(
        "Select Freshdesk XML exports or ZIP file",
        type=["xml", "zip"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith(".zip"):
                extract_zip(uploaded_file)
            elif uploaded_file.name.endswith(".xml"):
                save_uploaded_file(uploaded_file)

        analyze_button = st.button("🚀 Analyze Tickets")

# RIGHT: Status
with col2:
    st.header("📊 Ticket Summary")
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded. Ready for analysis.")
    else:
        st.warning("👈 Please upload XML or ZIP files to proceed.")

# Main analysis
if uploaded_files and 'analyze_button' in locals() and analyze_button:
    folder_path = UPLOAD_FOLDER
    tickets = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            full_path = os.path.join(folder_path, filename)
            tickets.extend(parse_ticket_xml(full_path))

    if tickets:
        df = pd.DataFrame(tickets)
        today = datetime.datetime.now().strftime("%Y%m%d")

        csv_filename = f"ticket_analysis_output_{today}.csv"
        insights_filename = f"insights_report_{today}.txt"
        unmatched_filename = "unmatched_samples.txt"

        df.to_csv(csv_filename, index=False)
        generate_insights(folder_path)

        # Success Message
        st.success("✅ Analysis completed successfully!")

        # Sample data
        st.subheader("📄 Sample Ticket Data")
        st.dataframe(df.head(10))

        # Quick metrics
        st.subheader("📈 Quick Metrics")
        st.metric("Total Tickets", len(df))
        st.metric("Date", today)

        # 📥 Download Buttons
        st.subheader("📥 Download Results")

        if Path(csv_filename).exists():
            csv_bytes = Path(csv_filename).read_bytes()
            st.download_button(
                label="Download Ticket Data (CSV)",
                data=csv_bytes,
                file_name=csv_filename,
                mime="text/csv"
            )

        if Path(insights_filename).exists():
            insights_bytes = Path(insights_filename).read_bytes()
            st.download_button(
                label="Download Insights Report (TXT)",
                data=insights_bytes,
                file_name=insights_filename,
                mime="text/plain"
            )

        if Path(unmatched_filename).exists():
            unmatched_bytes = Path(unmatched_filename).read_bytes()
            st.download_button(
                label="Download Uncategorized Samples (TXT)",
                data=unmatched_bytes,
                file_name=unmatched_filename,
                mime="text/plain"
            )

        # Categorized ticket map CSV
        categorized_map_file = f"categorized_ticket_map_{today}.csv"

        if Path(categorized_map_file).exists():
            cat_map_bytes = Path(categorized_map_file).read_bytes()
            st.download_button(
                label="Download Categorized Tickets (CSV)",
                data=cat_map_bytes,
                file_name=categorized_map_file,
                mime="text/csv"
            )
        
        st.caption("Reports are generated based on uploaded Freshdesk XML ticket exports.")
    else:
        st.error("❗ No valid tickets found. Please check your XML files.")
