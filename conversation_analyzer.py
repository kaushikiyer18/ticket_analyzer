import re
from trend_categories import TREND_CATEGORIES
from collections import defaultdict
from pathlib import Path
import pandas as pd

def generate_insights(tickets, output_prefix="insights_report"):
    categorized = defaultdict(list)
    unmatched = []

    for ticket in tickets:
        match_found = False
        for category, patterns in TREND_CATEGORIES.items():
            if any(re.search(pat, ticket["combined_text"], re.IGNORECASE) for pat in patterns):
                categorized[category].append(ticket)
                match_found = True
                break
        if not match_found:
            unmatched.append(ticket)

    # Generate Insights Report
    today = pd.Timestamp.today().strftime("%Y%m%d")
    insights_path = f"{output_prefix}_{today}.txt"
    with open(insights_path, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Generated on: {today}\n\n")
        f.write("Top Problem Categories:\n")
        f.write("-" * 30 + "\n")

        for category, items in categorized.items():
            f.write(f"\n➡️ {category} ({len(items)} occurrences)\n")
            for item in items[:3]:  # Top 3 examples per category
                example = item["combined_text"].strip().replace("\n", " ")[:250]
                f.write(f"• {example}...\n")

    # Save unmatched samples
    unmatched_path = "unmatched_samples.txt"
    if unmatched:
        with open(unmatched_path, "w") as f:
            for item in unmatched:
                f.write(item["combined_text"].strip().replace("\n", " ") + "\n")

    # Categorized ticket map
    map_rows = []
    for category, items in categorized.items():
        for item in items:
            map_rows.append({
                "Category": category,
                "Ticket ID": item.get("ticket_id", "N/A"),
                "Subject": item.get("subject", "N/A"),
                "Created At": item.get("created_at", "N/A"),
                "Priority": item.get("priority", "N/A"),
                "Type": category
            })
    map_df = pd.DataFrame(map_rows)
    map_df.to_csv(f"categorized_ticket_map_{today}.csv", index=False)

    print("✅ Insight report and categorized ticket map generated successfully.")
