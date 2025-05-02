import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from html import unescape

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
    text = unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)  # remove HTML
    text = re.sub(r"http\S+", "", text)   # remove links
    text = re.sub(r"\s+", " ", text)      # normalize whitespace
    return text.strip().lower()

def extract_conversations(folder_path):
    conversations = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            tree = ET.parse(os.path.join(folder_path, filename))
            root = tree.getroot()
            for note in root.findall(".//helpdesk-note"):
                body = note.findtext("body") or ""
                conversations.append(clean_text(body))

    return conversations

def match_category(text):
    for pattern, category in TREND_CATEGORIES.items():
        if re.search(pattern, text):
            return category
    return None

def generate_insights(folder_path):
    all_texts = extract_conversations(folder_path)
    category_counts = defaultdict(int)
    example_texts = defaultdict(list)

    for text in all_texts:
        category = match_category(text)
        if category:
            category_counts[category] += 1
            if len(example_texts[category]) < 3:
                example_texts[category].append(text)

    today = datetime.now().strftime("%Y%m%d")
    output_file = f"insights_report_{today}.txt"

    with open(output_file, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("=============================================\n\n")
        f.write(f"Generated on: {today}\n\n")
        f.write("Top Problem Categories:\n")
        f.write("------------------------\n")

        if not category_counts:
            f.write("No major trends found.\n")
        else:
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"– {category} ({count} occurrences)\n")
                for ex in example_texts[category]:
                    f.write(f"    • {ex[:120]}...\n")
                f.write("\n")

    return output_file
