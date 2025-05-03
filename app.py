import streamlit as st
import pandas as pd
import os
import datetime
import zipfile
from pathlib import Path

from parser import parse_ticket_xml
from analyzer import analyze_tickets
from conversation_analyzer import generate_insights

st.set_page_config(page_title="Customer Support Ticket Analyzer", page_icon="🎟️", layout="wide")

st.title("🎟️ Customer Support Ticket Analyzer")
st.subheader("Analyze Freshdesk ticket exports and uncover trends easily 🚀")
st.markdown("---")

UPLOAD_FOLDER = "uploaded_xmls"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Upload files
uploaded_files = st.file_uploader("Upload XML files (you can upload a ZIP of multiple XMLs)", type=["xml", "zip"], accept_multiple_files=True)

def save_uploaded_file(uploaded_file):
    filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filepath

def extract_zip_if_needed(file_path):
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(UPLOAD_FOLDER)

# Button to trigger analysis
if uploaded_files:
    for uploaded_file in uploaded_files:
        path = save_uploaded_file(uploaded_file)
        extract_zip_if_needed(path)

    if st.button("🚀 Analyze Tickets"):
        tickets = []
        for file in os.listdir(UPLOAD_FOLDER):
            if file.endswith(".xml"):
                full_path = os.path.join(UPLOAD_FOLDER, file)
                tickets.extend(parse_ticket_xml(full_path))

        if tickets:
            df = pd.DataFrame(tickets)

            today = datetime.datetime.now().strftime("%Y%m%d")
            csv_filename = f"ticket_analysis_output_{today}.csv"
            insights_filename = f"insights_report_{today}.txt"
            unmatched_filename = f"unmatched_samples_{today}.txt"
            categorized_map_file = f"categorized_ticket_map_{today}.csv"

            df.to_csv(csv_filename, index=False)

            generate_insights(tickets)

            # Save state for persistent downloads
            st.session_state["csv_filename"] = csv_filename
            st.session_state["insights_filename"] = insights_filename
            st.session_state["unmatched_filename"] = unmatched_filename
            st.session_state["categorized_map_file"] = categorized_map_file

            st.success("✅ Analysis completed successfully!")
            st.subheader("📄 Sample Ticket Data")
            st.dataframe(df.head(10))

            st.subheader("📈 Quick Metrics")
            st.metric(label="Total Tickets", value=len(df))
            st.metric(label="Date", value=today)

# Show download buttons if session state is present
if "csv_filename" in st.session_state:
    st.subheader("📥 Download Results")

    if Path(st.session_state["csv_filename"]).exists():
        with open(st.session_state["csv_filename"], "rb") as f:
            st.download_button("Download Ticket Data (CSV)", f, file_name=st.session_state["csv_filename"], mime="text/csv")

    if Path(st.session_state["insights_filename"]).exists():
        with open(st.session_state["insights_filename"], "rb") as f:
            st.download_button("Download Insights Report (TXT)", f, file_name=st.session_state["insights_filename"], mime="text/plain")

    if Path(st.session_state["unmatched_filename"]).exists():
        with open(st.session_state["unmatched_filename"], "rb") as f:
            st.download_button("Download Uncategorized Samples (TXT)", f, file_name=st.session_state["unmatched_filename"], mime="text/plain")

    if Path(st.session_state["categorized_map_file"]).exists():
        with open(st.session_state["categorized_map_file"], "rb") as f:
            st.download_button("Download Categorized Tickets (CSV)", f, file_name=st.session_state["categorized_map_file"], mime="text/csv")

    st.caption("Reports are generated based on uploaded Freshdesk XML ticket exports.")
