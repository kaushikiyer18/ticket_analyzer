import streamlit as st
import pandas as pd
import os
import datetime
import zipfile
from parser import parse_ticket_xml
from analyzer import analyze_tickets
from conversation_analyzer import generate_insights

# Streamlit config
st.set_page_config(page_title="Customer Support Ticket Analyzer", page_icon="🎟️", layout="wide")
st.title("🎟️ Customer Support Ticket Analyzer")
st.subheader("Analyze Freshdesk ticket exports and uncover trends easily 🚀")
st.markdown("---")

col1, col2 = st.columns([2, 3])
UPLOAD_FOLDER = "uploaded_xmls"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_uploaded_file(uploaded_file):
    with open(os.path.join(UPLOAD_FOLDER, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())

def extract_zip(uploaded_zip):
    zip_path = os.path.join(UPLOAD_FOLDER, uploaded_zip.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_zip.getbuffer())
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(UPLOAD_FOLDER)

with col1:
    st.header("📂 Upload XML Files")
    uploaded_files = st.file_uploader(
        "Select Freshdesk XML exports or a ZIP file", 
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

with col2:
    st.header("📊 Ticket Summary")

    if uploaded_files:
        st.info(f"**{len(uploaded_files)} files uploaded.** Ready for analysis! ✅")
    else:
        st.warning("👈 Please upload XML or ZIP files to proceed.")

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
        insights_path = os.path.join(os.getcwd(), insights_filename)

        df.to_csv(csv_filename, index=False)
        generate_insights(folder_path)

        st.success("✅ Analysis completed successfully!")

        st.subheader("📄 Sample Ticket Data")
        st.dataframe(df.head(10))

        st.subheader("📈 Quick Metrics")
        st.metric(label="Total Tickets", value=len(df))
        st.metric(label="Date", value=today)

        st.subheader("📥 Download Results")

        # CSV Download
        with open(csv_filename, "rb") as f:
            st.download_button(
                label="Download Ticket Data (CSV)",
                data=f,
                file_name=csv_filename,
                mime="text/csv"
            )

        # TXT Download
        if insights_path and os.path.exists(insights_path):
            with open(insights_path, "rb") as f:
                st.download_button(
                    label="Download Insights Report (TXT)",
                    data=f,
                    file_name=os.path.basename(insights_path),
                    mime="text/plain"
                )
        else:
            st.warning("⚠️ No insights report was generated.")

        st.caption("Reports are generated based on uploaded XML ticket exports.")
    else:
        st.error("❗ No valid tickets found. Please verify your XML files.")
