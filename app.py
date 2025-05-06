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

# Group ID to Name mapping
group_options = {
    "17000127117": "App Integration", "17000123004": "Bandwidth Team", "17000130793": "BFDL",
    "17000110678": "Campaign Team", "17000127820": "CPAAS Team", "17000120858": "DE Team",
    "17000127015": "DE US Team", "17000124233": "Dev Ops", "17000128583": "Europe DE",
    "17000127748": "Helpdesk T100", "17000119961": "Helpdesk team", "17000127195": "IS-Sysadmin",
    "17000121073": "MIS Team (Internal Request)", "17000123941": "NDNC Group", "17000126034": "Office Infra",
    "17000118813": "Onboarding Team", "17000126857": "Pepipost Delivery", "17000126858": "Pepipost Devops",
    "17000126859": "Pepipost Enterprise", "17000126860": "Pepipost Online", "17000126861": "Pepipost US",
    "17000124388": "Publisher Team", "17000127259": "Regulatory Team", "17000128058": "Research Team",
    "17000127451": "Sysadmin-Task", "17000126035": "Sysadmins", "17000123052": "Tender Group",
    "17000126258": "US Team", "17000128001": "Web Integration", "17000128876": "WhatsApp",
    "17000130127": "IS Team",
}

# Upload
def save_file(uploaded_file):
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

st.subheader("📂 Upload XML Files (you can upload a ZIP of multiple XMLs)")
uploaded_files = st.file_uploader("Drag and drop files here", type=["xml", "zip"], accept_multiple_files=True)

# Select Freshdesk Groups
group_names = [name for _, name in group_options.items()]
group_selection = st.multiselect("👥 Select Freshdesk Groups to Analyze", options=["All"] + group_names, default=["All"])

# Select Ticket Types
ticket_type_options = [
    "Campaign Execution", "Integration", "Onboarding", "Product Feedback", "Billing", "Support",
    "Bug", "Query", "Training", "Automation", "WhatsApp Setup", "Webhooks", "Dashboard Access"
]
selected_types = st.multiselect("🎯 Select Ticket Types to Include", options=["All"] + ticket_type_options, default=["All"])

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
        # Filter by selected Group(s) and Ticket Type(s)
        selected_ids = [gid for gid, name in group_options.items() if name in group_selection]
        filtered_tickets = [
            ticket for ticket in all_tickets
            if (
                "All" in group_selection or ticket["group_id"] in selected_ids
            ) and (
                "All" in selected_types or ticket.get("type") in selected_types
            )
        ]

        df = pd.DataFrame(filtered_tickets)
        today = datetime.datetime.now().strftime("%Y%m%d")
        csv_file = f"ticket_analysis_output_{today}.csv"
        df.to_csv(csv_file, index=False)

        # Generate insights and enriched file
        generate_insights(UPLOAD_FOLDER)

        st.success("✅ Analysis complete! Download your results below.")
        st.markdown("## 📥 Download Results")

        # Path variables
        insights_path = f"insights_report_{today}.txt"
        map_path = f"categorized_ticket_map_{today}.csv"
        enriched_path = f"ticket_analysis_output_{today}.csv"
        unmatched_file = f"unmatched_samples_{today}.txt"

        # Download: Raw Parsed CSV
        if Path(csv_file).exists():
            st.download_button("📄 Ticket Data CSV", data=open(csv_file, "rb").read(), file_name=csv_file, mime="text/csv")

        # Download: Enriched Auto-Tagged CSV
        if Path(enriched_path).exists():
            st.download_button("📩 Enriched Ticket CSV (Auto–Tagged)", data=open(enriched_path, "rb").read(), file_name=enriched_path, mime="text/csv")

        # Download: Trend Summary
        if Path(insights_path).exists():
            st.download_button("🧠 Insights Report", data=open(insights_path, "rb").read(), file_name=insights_path, mime="text/plain")

        # Download: Categorized Ticket Map
        if Path(map_path).exists():
            st.download_button("📊 Categorized Ticket Map", data=open(map_path, "rb").read(), file_name=map_path, mime="text/csv")

        # Download: Unmatched Issues
        if Path(unmatched_file).exists():
            st.download_button("❓ Unmatched Issues", data=open(unmatched_file, "rb").read(), file_name=unmatched_file, mime="text/plain")

        st.caption("Reports are generated based on uploaded Freshdesk XML ticket exports.")
    else:
        st.error("❌ No valid tickets found. Please check your XML files.")
