import os
import re
import csv
from collections import defaultdict, Counter
from datetime import datetime
from trend_categories import TREND_CATEGORIES

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def categorize_ticket(text):
    text_clean = clean_text(text)
    for category, patterns in TREND_CATEGORIES.items():
        for pattern in patterns:
            if re.search(rf'\b{re.escape(pattern)}\b', text_clean):
                return category
    return "Uncategorized"

def generate_insights(folder_path):
    categorized = defaultdict(list)
    unmatched = []
    today = datetime.now().strftime("%Y%m%d")
    insights_filename = f"insights_report_{today}.txt"
    unmatched_filename = "unmatched_samples.txt"
    categorized_map_filename = f"categorized_ticket_map_{today}.csv"

    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                xml = f.read()

            # Extract <helpdesk-ticket> blocks
            blocks = re.findall(r"<helpdesk-ticket>(.*?)</helpdesk-ticket>", xml, re.DOTALL)

            for block in blocks:
                ticket_id = re.search(r"<display-id>(.*?)</display-id>", block)
                subject = re.search(r"<subject>(.*?)</subject>", block)
                created_at = re.search(r"<created-at>(.*?)</created-at>", block)
                priority = re.search(r"<priority>(.*?)</priority>", block)
                ticket_type = re.search(r"<ticket-type>(.*?)</ticket-type>", block)
                description = re.search(r"<description>(.*?)</description>", block)

                ticket_text = " ".join([
                    subject.group(1) if subject else "",
                    description.group(1) if description else "",
                ])

                category = categorize_ticket(ticket_text)
                ticket_info = {
                    "ticket_id": ticket_id.group(1) if ticket_id else "N/A",
                    "subject": subject.group(1).strip() if subject else "N/A",
                    "created_at": created_at.group(1) if created_at else "N/A",
                    "priority": priority.group(1) if priority else "N/A",
                    "type": ticket_type.group(1) if ticket_type else "N/A",
                    "description": clean_text(description.group(1)) if description else ""
                }

                if category == "Uncategorized":
                    unmatched.append(ticket_info["description"])
                else:
                    categorized[category].append(ticket_info)

    # Write Insights Report
    with open(insights_filename, "w", encoding="utf-8") as f:
        f.write("Customer Support Trends Report\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Generated on: {today}\n\n")
        f.write("Top Problem Categories:\n")
        f.write("-" * 30 + "\n\n")
        for category, tickets in categorized.items():
            f.write(f"→ {category} ({len(tickets)} occurrences)\n")
            for t in tickets[:3]:  # Sample 3 entries
                f.write(f"• {t['description'][:300]}...\n")
            f.write("\n")

    # Write Unmatched Samples
    if unmatched:
        with open(unmatched_filename, "w", encoding="utf-8") as f:
            for line in unmatched:
                f.write(line + "\n")

    # Write ticket-category mapping CSV
    with open(categorized_map_filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Ticket ID", "Subject", "Created At", "Priority", "Type"])
        for category, tickets in categorized.items():
            for t in tickets:
                writer.writerow([category, t["ticket_id"], t["subject"], t["created_at"], t["priority"], t["type"]])
