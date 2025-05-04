
import os
import datetime
import pandas as pd
import xml.etree.ElementTree as ET
from trend_categories import TREND_KEYWORDS

def score_keywords(text, keywords):
    text_lower = text.lower()
    return sum(1 for word in keywords if word.lower() in text_lower)

def generate_insights(folder_path):
    today = datetime.datetime.now().strftime("%Y%m%d")
    output_file = f"insights_report_{today}.txt"
    unmatched_file = f"unmatched_samples_{today}.txt"
    categorized_map_file = f"categorized_ticket_map_{today}.csv"

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

                    combined = f"{subject} {description}".strip().lower()
                    best_match = None
                    best_score = 0

                    for category, keywords in TREND_KEYWORDS.items():
                        score = score_keywords(combined, keywords)
                        if score >= 3 and score > best_score:
                            best_match = category
                            best_score = score

                    if best_match:
                        trend_map.setdefault(best_match, []).append(combined)
                        map_rows.append({
                            "Category": best_match,
                            "Ticket ID": tid,
                            "Subject": subject,
                            "Created At": created,
                            "Priority": priority,
                            "Type": best_match
                        })
                    else:
                        unmatched.append(combined)
            except Exception as e:
                print(f"Failed to parse {xml_path}: {e}")

    with open(output_file, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("="*40 + "\n")
        f.write(f"Generated on: {today}\n\n")
        f.write("Top Problem Categories:\n")
        f.write("-"*30 + "\n\n")
        for category, samples in sorted(trend_map.items(), key=lambda x: len(x[1]), reverse=True):
            f.write(f"🔹 {category} ({len(samples)} occurrences)\n\n")

    if unmatched:
        with open(unmatched_file, "w") as f:
            f.write("Unmatched Samples\n")
            f.write("="*20 + "\n\n")
            for u in unmatched:
                f.write(f"{u}\n\n")

    if map_rows:
        pd.DataFrame(map_rows).to_csv(categorized_map_file, index=False)
