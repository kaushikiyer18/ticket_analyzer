
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

# --- HEADER ---
st.markdown("""
# 🎫 <span style='color:#FF4B4B;'>Customer Support Ticket Analyzer</span>
<small>Analyze Freshdesk XML ticket exports and uncover trends easily 🚀</small>
""", unsafe_allow_html=True)
st.markdown("---")

UPLOAD_FOLDER = "uploaded_xmls"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_file(uploaded_file):
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# --- UPLOAD SECTION ---
with st.container():
    st.markdown("### 📂 Upload XML Files")
    st.caption("You can upload XML or a ZIP of multiple XMLs (Max 200MB)")
    uploaded_files = st.file_uploader("Drag and drop files here", type=["xml", "zip"], accept_multiple_files=True, label_visibility="collapsed")

valid_files = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        path = save_file(uploaded_file)
        if uploaded_file.name.endswith(".zip"):
            with zipfile.ZipFile(path, "r") as zip_ref:
                zip_ref.extractall(UPLOAD_FOLDER)
        else:
            valid_files.append(path)

# --- ANALYZE BUTTON ---
if st.button("🚀 Analyze Tickets") and uploaded_files:
    with st.spinner("Analyzing tickets... Please wait."):
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

            st.success("✅ Analysis complete! Download your results below.")
            st.markdown("## 📥 Download Results")

            with st.expander("📄 Ticket Data CSV"):
                st.dataframe(df)
                st.download_button("⬇️ Download Ticket Data", data=open(csv_file, "rb").read(), file_name=csv_file, mime="text/csv")

            insights_path = f"insights_report_{today}.txt"
            if Path(insights_path).exists():
                with st.expander("🧠 Insights Report"):
                    st.text(open(insights_path).read())
                    st.download_button("⬇️ Download Insights Report", data=open(insights_path, "rb").read(), file_name=insights_path, mime="text/plain")

            cat_map = f"categorized_ticket_map_{today}.csv"
            if Path(cat_map).exists():
                cat_df = pd.read_csv(cat_map)
                with st.expander("📊 Categorized Ticket Map"):
                    st.dataframe(cat_df)
                    st.download_button("⬇️ Download Categorized Map", data=open(cat_map, "rb").read(), file_name=cat_map, mime="text/csv")

            unmatched_file = f"unmatched_samples_{today}.txt"
            if Path(unmatched_file).exists():
                with st.expander("❓ Unmatched Issues"):
                    st.text(open(unmatched_file).read())
                    st.download_button("⬇️ Download Unmatched Samples", data=open(unmatched_file, "rb").read(), file_name=unmatched_file, mime="text/plain")

            st.caption("Reports are generated based on uploaded Freshdesk XML ticket exports.")
        else:
            st.error("❌ No valid tickets found. Please check your XML files.")
