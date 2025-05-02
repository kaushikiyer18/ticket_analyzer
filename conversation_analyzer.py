import os
import xml.etree.ElementTree as ET
from collections import Counter
import re
import html
import datetime

def extract_conversations(folder_path):
    all_texts = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            full_path = os.path.join(folder_path, filename)
            tree = ET.parse(full_path)
            root = tree.getroot()
            for ticket_elem in root.findall(".//helpdesk-ticket"):
                # Check for description
                desc = ticket_elem.findtext("description")
                if desc:
                    all_texts.append(clean_text(desc))
                # Check for helpdesk-notes
                for note in ticket_elem.findall(".//helpdesk-note"):
                    note_text = note.findtext("body")
                    if note_text:
                        all_texts.append(clean_text(note_text))
    return all_texts

def clean_text(text):
    # Basic cleaning for analysis
    text = html.unescape(text)
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"\s+", " ", text)     # normalize whitespace
    text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
    return text.lower().strip()

def generate_insights(folder_path):
    all_texts = extract_conversations(folder_path)
    bigrams = []

    for text in all_texts:
        words = text.split()
        bigrams.extend([" ".join(pair) for pair in zip(words, words[1:])])

    bigram_freq = Counter(bigrams)
    most_common = bigram_freq.most_common(20)

    today = datetime.datetime.now().strftime("%Y%m%d")
    insights_filename = f"insights_report_{today}.txt"

    with open(insights_filename, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("=====================================\n\n")
        f.write(f"Generated on: {today}\n\n")
        f.write("Top Problem Patterns:\n")
        f.write("———————————————\n")
        for phrase, count in most_common:
            f.write(f"- {phrase} ({count} occurrences)\n")

    return insights_filename
