import streamlit as st
import pandas as pd
import os
import zipfile
import datetime
from pathlib import Path
from parser import parse_ticket_xml
from analyzer import analyze_tickets
from conversation_analyzer import generate_insights
import xml.etree.ElementTree as ET

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

# Upload XML or ZIP files
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

# Extract group IDs and ticket types before analysis
group_ids = set()
ticket_types = set()
for file in os.listdir(UPLOAD_FOLDER):
    if file.endswith(".xml"):
        tree = ET.parse(os.path.join(UPLOAD_FOLDER, file))
        root = tree.getroot()
        for ticket in root.findall(".//helpdesk-ticket"):
            group_id = ticket.findtext("group-id", default="unassigned").strip()
            group_ids.add(group_id)
            ttype = ticket.findtext("ticket-type", default="Other").strip()
            ticket_types.add(ttype)

# Replace with your actual group mapping
GROUP_MAPPING = {
    "17000127117": "App Integration",
    "17000123004": "Bandwidth Team",
    "17000130793": "BFDL",
    "17000110678": "Campaign Team",
    "17000127820": "CPAAS Team",
    "17000120858": "DE Team",
    "17000127015": "DE US Team",
    "17000124233": "Dev Ops",
    "17000128583": "Europe DE",
    "17000127748": "Helpdesk T100",
    "17000119961": "Helpdesk team",
    "17000130127": "IS Team",
    "17000127195": "IS-Sysadmin",
    "17000121073": "MIS Team (Internal Request)",
    "17000123941": "NDNC Group",
    "17000126034": "Office Infra",
    "17000118813": "Onboarding Team",
    "17000126857": "Pepipost Delivery",
    "17000126858": "Pepipost Devops",
    "17000126859": "Pepipost Enterprise",
    "17000126860": "Pepipost Online",
    "17000126861": "Pepipost US",
    "17000124388": "Publisher Team",
    "17000127259": "Regulatory Team",
    "17000128058": "Research Team",
    "17000127451": "Sysadmin-Task",
    "17000126035": "Sysadmins",
    "17000123052": "Tender Group",
    "17000126258": "US Team",
    "17000128001": "Web Integration",
    "17000128876": "WhatsApp",
    "All": "All Groups"
}

group_ids = list(group_ids)
group_names = [GROUP_MAPPING.get(gid, f"Unknown ({gid})") for gid in group_ids]
group_selection = st.multiselect("👥 Select Freshdesk Groups to Analyze", options=group_names)
ticket_type_selection = st.multiselect("🎯 Select Ticket Types to Include", options=list(ticket_types))

analyze_btn = st.button("🚀 Analyze Tickets")

if analyze_btn and uploaded_files:
    selected_ids = [gid for gid, name in GROUP_MAPPING.items() if name in group_selection]
    selected_types = set(ticket_type_selection)

    all_tickets = []
    for file in os.listdir(UPLOAD_FOLDER):
        if file.endswith(".xml"):
            full_path = os.path.join(UPLOAD_FOLDER, file)
            all_tickets.extend(parse_ticket_xml(full_path))

    # Apply group & type filters
    filtered_tickets = []
    for ticket in all_tickets:
        if (ticket["group_id"] in selected_ids or "All" in group_selection) and ticket["type"] in selected_types:
            filtered_tickets.append(ticket)

    if filtered_tickets:
        df = pd.DataFrame(filtered_tickets)
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
        st.error("❌ No tickets matched the selected group and type filters.")
