import os
import re
from collections import defaultdict
from datetime import datetime

# Trend category mapping: keywords → category name
TREND_CATEGORIES = {
    "dlt|netcore certified|sms failure|sender id": "DLT Configuration Issues",
    "approval|submitted|approval pending": "Approval Delays",
    "escalation matrix|urgent|escalated|follow up": "High Escalation Volume",
    "email error|not received|smtp|bounce|email delivery": "Email Delivery Issues",
    "not working|failed|bug|error|issue|unable": "Generic System Errors",
    "configuration|setup|access denied|not able to login": "Account Access or Configuration",
    "order issue|order not received|invoice": "Order or Billing Issues",
}

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)      # remove HTML tags
    text = re.sub(r"http\S+", "", text)       # remove URLs
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)  # remove punctuation
    text = re.sub(r"\s+", " ", text)          # normalize whitespace
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

    for ticket in all_tickets:
        raw_text = ticket.get("combined_text", "")
        cleaned = clean_text(raw_text)
        category = match_category(cleaned)
        if category:
            category_counts[category] += 1
            if len(example_texts[category]) < 3:
                example_texts[category].append(cleaned[:150] + "...")

    today = datetime.now().strftime("%Y%m%d")
    output_file = f"insights_report_{today}.txt"

    with open(output_file, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("=============================================\n\n")
        f.write(f"Generated on: {today}\n\n")

        if not category_counts:
            f.write("⚠️ No clear trend categories were detected.\n")
            return output_file

        f.write("Top Problem Categories:\n")
        f.write("------------------------\n")

        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"– {category} ({count} occurrences)\n")
            for example in example_texts[category]:
                f.write(f"    • {example}\n")
            f.write("\n")

    return output_file
