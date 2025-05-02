import streamlit as st
import pandas as pd
import os
import datetime
from parser import parse_ticket_xml
from analyzer import analyze_tickets
from conversation_analyzer import generate_insights

# Streamlit page settings
st.set_page_config(page_title="Customer Support Ticket Analyzer", page_icon="🎟️", layout="wide")

# Title and Subheader
st.title("🎟️ Customer Support Ticket Analyzer")
st.subheader("Analyze Freshdesk ticket exports and uncover trends easily 🚀")
st.markdown("---")

# Upload folder
UPLOAD_FOLDER = "uploaded_xmls"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Save uploaded file
def save_uploaded_file(uploaded_file):
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

# Columns for layout
col1, col2 = st.columns([2, 3])

# LEFT: Upload XML files
with col1:
    st.header("📂 Upload XML Files")
    uploaded_files = st.file_uploader("Select one or more Freshdesk XML exports", type=["xml"], accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            save_uploaded_file(uploaded_file)

        analyze_button = st.button("🚀 Analyze Tickets")

# RIGHT: Display file status
with col2:
    st.header("📊 Ticket Summary")
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded. Ready for analysis.")
    else:
        st.warning("👈 Please upload XML files to proceed.")

# MAIN: Run analysis
if uploaded_files and 'analyze_button' in locals() and analyze_button:
    folder_path = UPLOAD_FOLDER
    tickets = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            full_path = os.path.join(folder_path, filename)
            tickets.extend(parse_ticket_xml(full_path))

    if tickets:
        df = pd.DataFrame(tickets)

        # Generate file names
        today = datetime.datetime.now().strftime("%Y%m%d")
        csv_filename = f"ticket_analysis_output_{today}.csv"
        insights_filename = f"insights_report_{today}.txt"

        # Save CSV
        df.to_csv(csv_filename, index=False)

        # Generate insights
        generate_insights(folder_path)

        # Display metrics
        st.success("✅ Analysis completed successfully!")
        st.subheader("📄 Sample Ticket Data")
        st.dataframe(df.head(10))

        st.subheader("📈 Quick Metrics")
        st.metric(label="Total Tickets", value=len(df))
        st.metric(label="Date", value=today)

        # 📥 Download buttons
        st.subheader("📥 Download Results")

        # CSV download
        with open(csv_filename, "rb") as f:
            st.download_button(
                label="Download Ticket Data (CSV)",
                data=f,
                file_name=csv_filename,
                mime="text/csv"
            )

        # TXT download
        insights_path = insights_filename
        if insights_path and os.path.exists(insights_path):
            with open(insights_path, "rb") as f:
                st.download_button(
                    label="Download Insights Report (TXT)",
                    data=f,
                    file_name=os.path.basename(insights_path),
                    mime="text/plain"
                )
                st.caption("Reports are generated based on uploaded XML ticket exports.")
        else:
            st.warning("⚠️ No insights report was generated.")
    else:
        st.error("❗ No valid tickets found. Please check your XML files.")
