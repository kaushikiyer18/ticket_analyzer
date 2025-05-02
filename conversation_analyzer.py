import os
import re
import xml.etree.ElementTree as ET
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
import html

# Issue-focused keywords
ISSUE_KEYWORDS = [
    "error", "issue", "problem", "fail", "failed", "unable", "not working",
    "rejected", "missing", "delay", "incorrect", "denied", "does not", "can't",
    "cannot", "down", "bug", "escalation", "approval", "timeout"
]

# Ignore common polite or non-informative patterns
EXCLUDE_PATTERNS = [
    "hi team", "thanks", "regards", "thank you", "please find", "dear team",
    "this email", "click here", "email id", "for your reference", "you have",
    "you are", "we have", "if you", "of the", "at your", "in case"
]


def extract_conversations(folder_path):
    conversations = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            tree = ET.parse(os.path.join(folder_path, filename))
            root = tree.getroot()

            for note in root.iter("helpdesk-note"):
                body_elem = note.find("body")
                if body_elem is not None and body_elem.text:
                    text = html.unescape(body_elem.text).strip().lower()

                    # Filter only issue-relevant sentences
                    issue_sentences = []
                    for sentence in re.split(r"[.!?\n]", text):
                        sentence = sentence.strip()
                        if any(k in sentence for k in ISSUE_KEYWORDS):
                            if not any(p in sentence for p in EXCLUDE_PATTERNS):
                                issue_sentences.append(sentence)

                    conversations.extend(issue_sentences)

    return conversations


def clean_text(text):
    # Basic cleanup
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def generate_insights(folder_path):
    conversations = extract_conversations(folder_path)
    cleaned_sentences = [clean_text(text) for text in conversations if text.strip()]

    if not cleaned_sentences:
        with open("insights_report_latest.txt", "w") as f:
            f.write("No actionable problem patterns found.\n")
        return

    vectorizer = CountVectorizer(ngram_range=(2, 3), max_features=30)
    X = vectorizer.fit_transform(cleaned_sentences)
    feature_names = vectorizer.get_feature_names_out()
    counts = X.toarray().sum(axis=0)

    pattern_counts = list(zip(feature_names, counts))
    pattern_counts.sort(key=lambda x: x[1], reverse=True)

    today = datetime_now_string()
    output_file = f"insights_report_{today}.txt"

    with open(output_file, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("==================================\n\n")
        f.write(f"Generated on: {today}\n\n")
        f.write("Top Problem Patterns:\n")
        f.write("---------------------------\n")
        for pattern, count in pattern_counts:
            f.write(f"– {pattern} ({count} occurrences)\n")


def datetime_now_string():
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d")
