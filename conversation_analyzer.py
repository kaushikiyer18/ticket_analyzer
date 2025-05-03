import os
import re
import datetime
import pandas as pd
from trend_categories import TREND_PATTERNS

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
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                content = f.read()

            tickets = re.findall(r"<helpdesk-ticket>(.*?)</helpdesk-ticket>", content, re.DOTALL)
            for ticket in tickets:
                desc_match = re.search(r"<description>(.*?)</description>", ticket, re.DOTALL)
                subj_match = re.search(r"<subject>(.*?)</subject>", ticket, re.DOTALL)
                id_match = re.search(r"<display-id>(.*?)</display-id>", ticket)
                created_match = re.search(r"<created-at>(.*?)</created-at>", ticket)
                priority_match = re.search(r"<priority>(.*?)</priority>", ticket)

                desc = desc_match.group(1).strip() if desc_match else ""
                subj = subj_match.group(1).strip() if subj_match else ""
                tid = id_match.group(1).strip() if id_match else "N/A"
                created = created_match.group(1).strip() if created_match else "N/A"
                priority = priority_match.group(1).strip() if priority_match else "N/A"

                combined = f"{subj} {desc}".strip()
                matched = False
                for category, patterns in TREND_PATTERNS.items():
                    if any(re.search(p, combined, re.IGNORECASE) for p in patterns):
                        trend_map.setdefault(category, []).append(combined)
                        map_rows.append({
                            "Category": category,
                            "Ticket ID": tid,
                            "Subject": subj,
                            "Created At": created,
                            "Priority": priority,
                            "Type": category
                        })
                        matched = True
                        break
                if not matched:
                    unmatched.append(combined)

    with open(output_file, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("="*40 + "\n")
        f.write(f"Generated on: {today}\n\n")
        f.write("Top Problem Categories:\n")
        f.write("-"*30 + "\n\n")
        for category, samples in trend_map.items():
            f.write(f"🔹 {category} ({len(samples)} occurrences)\n\n")

    if unmatched:
        with open(unmatched_file, "w") as f:
            f.write("Unmatched Samples\n")
            f.write("="*20 + "\n\n")
            for u in unmatched:
                f.write(f"{u}\n\n")

    if map_rows:
        pd.DataFrame(map_rows).to_csv(categorized_map_file, index=False)
