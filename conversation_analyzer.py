import os
import re
from collections import defaultdict
from datetime import datetime
from trend_categories import TREND_CATEGORIES  # ✅ new import

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()

def match_category(text):
    for pattern, category in TREND_CATEGORIES.items():
        if re.search(pattern, text):
            return category
    return None

def generate_insights(folder_path):
    from parser import parse_ticket_xml

    all_tickets = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            full_path = os.path.join(folder_path, filename)
            tickets = parse_ticket_xml(full_path)
            all_tickets.extend(tickets)

    category_counts = defaultdict(int)
    example_texts = defaultdict(list)
    unmatched_messages = []

    for ticket in all_tickets:
        raw_text = ticket.get("combined_text", "")
        cleaned = clean_text(raw_text)
        category = match_category(cleaned)
        if category:
            category_counts[category] += 1
            if len(example_texts[category]) < 3:
                example_texts[category].append(cleaned[:150] + "...")
        else:
            unmatched_messages.append(cleaned)

    today = datetime.now().strftime("%Y%m%d")
    output_file = f"insights_report_{today}.txt"
    unmatched_file = "unmatched_samples.txt"

    with open(output_file, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("=============================================\n\n")
        f.write(f"Generated on: {today}\n\n")

        if not category_counts:
            f.write("⚠️ No trend categories matched.\n")
        else:
            f.write("Top Problem Categories:\n")
            f.write("------------------------\n")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"– {category} ({count} occurrences)\n")
                for example in example_texts[category]:
                    f.write(f"    • {example}\n")
                f.write("\n")

    if unmatched_messages:
        with open(unmatched_file, "w") as f:
            for msg in unmatched_messages:
                f.write(msg[:250] + "\n")

    return output_file
