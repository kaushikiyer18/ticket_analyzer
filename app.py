import streamlit as st
import pandas as pd
import os
import datetime
from parser import parse_ticket_xml
from analyzer import analyze_tickets
from conversation_analyzer import generate_insights

# Set page config
st.set_page_config(page_title="Customer Support Ticket Analyzer", page_icon="🎟️", layout="wide")

st.title("🎟️ Customer Support Ticket Analyzer")
st.subheader("Analyze Freshdesk ticket exports and uncover trends easily 🚀")
st.markdown("---")

# Layout columns
col1, col2 = st.columns([2, 3])

UPLOAD_FOLDER = "uploaded_xmls"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_uploaded_file(uploaded_file):
    with open(os.path.join(UPLOAD_FOLDER, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())

# LEFT: Upload files
with col1:
    st.header("📂 Upload XML Files")
    uploaded_files = st.file_uploader("Select one or more Freshdesk XML exports", type=["xml"], accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            save_uploaded_file(uploaded_file)

        analyze_button = st.button("🚀 Analyze Tickets")

# RIGHT: Ticket summary info
with col2:
    st.header("📊 Ticket Summary")
    if uploaded_files:
        st.info(f"✅ {len(uploaded_files)} files uploaded and ready for analysis.")
    else:
        st.warning("👈 Please upload XML files to begin.")

# MAIN: Run analysis when button clicked
if uploaded_files and 'analyze_button' in locals() and analyze_button:
    tickets = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith('.xml'):
            full_path = os.path.join(UPLOAD_FOLDER, filename)
            tickets.extend(parse_ticket_xml(full_path))

    if tickets:
        df = pd.DataFrame(tickets)

        today = datetime.datetime.now().strftime("%Y%m%d")
        csv_filename = f"ticket_analysis_output_{today}.csv"
        insights_filename = f"insights_report_{today}.txt"

        df.to_csv(csv_filename, index=False)
        generate_insights(UPLOAD_FOLDER)

        st.success("✅ Analysis completed successfully!")

        st.subheader("📄 Sample Ticket Data")
        st.dataframe(df.head(10))

        st.subheader("📈 Quick Metrics")
        st.metric("Total Tickets", len(df))
        st.metric("Date", today)

        st.subheader("📥 Download Results")

        # Download ticket data
        with open(csv_filename, "rb") as f:
            st.download_button(
                label="📥 Download Ticket Data (CSV)",
                data=f,
                file_name=csv_filename,
                mime="text/csv"
            )

        # Download insights file if it exists
        if os.path.exists(insights_filename):
            with open(insights_filename, "rb") as f:
                st.download_button(
                    label="📥 Download Insights Report (TXT)",
                    data=f,
                    file_name=insights_filename,
                    mime="text/plain"
                )
        else:
            st.warning("⚠️ No insights report found. Please check if it was generated correctly.")

        st.caption("Reports are generated based on uploaded XML ticket exports.")

    else:
        st.error("❗ No valid tickets found in the uploaded XML files.")
