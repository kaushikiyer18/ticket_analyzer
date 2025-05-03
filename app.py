import streamlit as st
import pandas as pd
import os
import zipfile
import datetime
from pathlib import Path
from parser import parse_ticket_xml
from analyzer import analyze_tickets
from conversation_analyzer import generate_insights

st.set_page_config(page_title="Customer Support Ticket Analyzer", page_icon="🎟️", layout="wide")
st.title("🎟️ Customer Support Ticket Analyzer")
st.caption("Analyze Freshdesk XML ticket exports and uncover trends easily 🚀")
st.markdown("---")

UPLOAD_FOLDER = "uploaded_xmls"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_file(uploaded_file):
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

st.subheader("📂 Upload XML Files (you can upload a ZIP of multiple XMLs)")
uploaded_files = st.file_uploader("Drag and drop files here", type=["xml", "zip"], accept_multiple_files=True)

valid_files = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        path = save_file(uploaded_file)
        if uploaded_file.name.endswith(".zip"):
            with zipfile.ZipFile(path, "r") as zip_ref:
                zip_ref.extractall(UPLOAD_FOLDER)
        else:
            valid_files.append(path)

analyze_btn = st.button("🚀 Analyze Tickets")

if analyze_btn and uploaded_files:
    all_tickets = []
    for file in os.listdir(UPLOAD_FOLDER):
        if file.endswith(".xml"):
            full_path = os.path.join(UPLOAD_FOLDER, file)
            all_tickets.extend(parse_ticket_xml(full_path))

    if all_tickets:
        df = pd.DataFrame(all_tickets)
        today = datetime.datetime.now().strftime("%Y%m%d")
        csv_file = f"ticket_analysis_output_{today}.csv"
        df.to_csv(csv_file, index=False)

        generate_insights(UPLOAD_FOLDER)

        st.markdown("## 📥 Download Results")
        st.download_button("Download Ticket Data (CSV)", data=open(csv_file, "rb").read(), file_name=csv_file, mime="text/csv")

        insights_path = f"insights_report_{today}.txt"
        if Path(insights_path).exists():
            st.download_button("Download Insights Report (TXT)", data=open(insights_path, "rb").read(), file_name=insights_path, mime="text/plain")

        cat_map = f"categorized_ticket_map_{today}.csv"
        if Path(cat_map).exists():
            st.download_button("Download Categorized Tickets (CSV)", data=open(cat_map, "rb").read(), file_name=cat_map, mime="text/csv")

        unmatched_file = f"unmatched_samples_{today}.txt"
        if Path(unmatched_file).exists():
            st.download_button("Download Uncategorized Samples (TXT)", data=open(unmatched_file, "rb").read(), file_name=unmatched_file, mime="text/plain")

        st.caption("Reports are generated based on uploaded Freshdesk XML ticket exports.")
    else:
        st.error("❌ No valid tickets found. Please check your XML files.")
