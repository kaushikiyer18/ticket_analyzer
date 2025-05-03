import os
import re
import pandas as pd
from trend_categories import TREND_CATEGORIES
from datetime import datetime

def generate_insights(xml_folder):
    categorized = {}
    uncategorized = []

    all_tickets = []

    # Collect all parsed data
    for filename in os.listdir(xml_folder):
        if filename.endswith(".xml"):
            df = pd.read_csv("ticket_analysis_output_" + datetime.now().strftime("%Y%m%d") + ".csv")
            all_tickets.extend(df.to_dict("records"))
            break  # Only load once (for now)

    for ticket in all_tickets:
        matched = False
        combined_text = ticket.get("combined_text", "")

        for category, patterns in TREND_CATEGORIES.items():
            if isinstance(patterns, list) and any(re.search(pat, combined_text, re.IGNORECASE) for pat in patterns):
                categorized.setdefault(category, []).append(ticket)
                matched = True
                break

        if not matched:
            uncategorized.append(ticket)

    # Save insights report
    report_filename = f"insights_report_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(report_filename, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y%m%d')}\n\n")
        f.write("Top Problem Categories:\n")
        f.write("-" * 30 + "\n\n")

        for category, tickets in categorized.items():
            f.write(f"🔹 {category} ({len(tickets)} occurrences)\n\n")

    # Save unmatched samples
    unmatched_filename = "unmatched_samples.txt"
    with open(unmatched_filename, "w") as f:
        for ticket in uncategorized:
            f.write(f"[{ticket.get('ticket_id', 'N/A')}] {ticket.get('combined_text', '')}\n\n")

    # Save CSV with Category Mapping
    map_filename = f"categorized_ticket_map_{datetime.now().strftime('%Y%m%d')}.csv"
    rows = []

    for category, tickets in categorized.items():
        for ticket in tickets:
            rows.append({
                "Category": category,
                "Ticket ID": ticket.get("ticket_id", "N/A"),
                "Subject": ticket.get("subject", "N/A"),
                "Created At": ticket.get("created_at", "N/A"),
                "Priority": ticket.get("priority", "N/A"),
                "Type": ticket.get("type", "N/A"),
            })

    df_map = pd.DataFrame(rows)
    df_map.to_csv(map_filename, index=False)
