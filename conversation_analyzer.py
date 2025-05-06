import os
import datetime
import pandas as pd
import xml.etree.ElementTree as ET
from trend_categories import TREND_KEYWORDS
from tagging_reference import TICKET_TYPE_REFERENCE, ISSUE_TYPE_REFERENCE

def score_keywords(text, keywords):
    text_lower = text.lower()
    return sum(1 for word in keywords if word.lower() in text_lower)

def auto_tag_ticket_type(text):
    text = text.lower()
    for ref in TICKET_TYPE_REFERENCE:
        keywords = ref.lower().split(" - ")[-1].split()  # focus on end part
        if any(word in text for word in keywords):
            return ref
    return "Uncategorized"

def auto_tag_issue_type(resolution_text):
    resolution_text = resolution_text.lower()
    for ref in ISSUE_TYPE_REFERENCE:
        if ref.lower() in resolution_text:
            return ref
    return "Uncategorized"

def generate_insights(folder_path):
    today = datetime.datetime.now().strftime("%Y%m%d")
    output_file = f"insights_report_{today}.txt"
    unmatched_file = f"unmatched_samples_{today}.txt"
    categorized_map_file = f"categorized_ticket_map_{today}.csv"
    enriched_file = f"ticket_analysis_output_{today}.csv"

    trend_map = {}
    unmatched = []
    map_rows = []

    for file in os.listdir(folder_path):
        if file.endswith(".xml"):
            xml_path = os.path.join(folder_path, file)
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                for ticket in root.findall(".//helpdesk-ticket"):
                    tid = ticket.findtext("display-id", default="N/A").strip()
                    created = ticket.findtext("created-at", default="N/A").strip()
                    priority = ticket.findtext("priority", default="N/A").strip()
                    subject = ticket.findtext("subject", default="").strip()
                    description = ticket.findtext("description", default="").strip()
                    ticket_type = ticket.findtext("ticket-type", default="N/A").strip()
                    issue_type = ticket.findtext("issue-type", default="N/A").strip()

                    # Get agent replies from <helpdesk-note><body>
                    agent_notes = ticket.findall(".//helpdesk-note/body")
                    agent_response = " ".join([note.text.strip() for note in agent_notes if note.text]) or "N/A"

                    combined = f"{subject} {description}".strip().lower()

                    # Auto-tagging
                    ticket_type_tagged = auto_tag_ticket_type(combined)
                    issue_type_tagged = auto_tag_issue_type(agent_response)

                    # Trend scoring
                    best_match = None
                    best_score = 0
                    for category, keywords in TREND_KEYWORDS.items():
                        score = score_keywords(combined, keywords)
                        if score >= 3 and score > best_score:
                            best_match = category
                            best_score = score

                    if best_match:
                        trend_map.setdefault(best_match, []).append(combined)
                    else:
                        unmatched.append(combined)

                    # Final output row
                    map_rows.append({
                        "Ticket ID": tid,
                        "Subject": subject,
                        "Summary of Problem Statement": description,
                        "Created": created,
                        "Current Ticket Type": ticket_type,
                        "Ticket Type (Auto Tagged)": ticket_type_tagged,
                        "Priority": priority,
                        "Priority (Auto Tagged)": "",  # Placeholder if needed later
                        "Current Issue Type": issue_type,
                        "Issue Type (Auto Tagged)": issue_type_tagged,
                        "Summary of Resolution (by agent)": agent_response
                    })

            except Exception as e:
                print(f"Failed to parse {xml_path}: {e}")

    # Write Insights Report
    with open(output_file, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("=" * 40 + "\n")
        f.write(f"Generated on: {today}\n\n")
        f.write("Top Problem Categories:\n")
        f.write("-" * 30 + "\n\n")
        for category, samples in sorted(trend_map.items(), key=lambda x: len(x[1]), reverse=True):
            f.write(f"🔹 {category} ({len(samples)} occurrences)\n\n")

    # Write Unmatched Samples
    if unmatched:
        with open(unmatched_file, "w") as f:
            f.write("Unmatched Samples\n")
            f.write("=" * 20 + "\n\n")
            for u in unmatched:
                f.write(f"{u}\n\n")

    # Final Enhanced CSV
    if map_rows:
        pd.DataFrame(map_rows).to_csv(categorized_map_file, index=False)
        pd.DataFrame(map_rows).to_csv(enriched_file, index=False)
