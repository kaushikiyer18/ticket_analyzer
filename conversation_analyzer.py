import os
import xml.etree.ElementTree as ET
from collections import Counter
import re
import html

def clean_text(text):
    text = html.unescape(text or "").lower()
    text = re.sub(r'<.*?>', '', text)  # remove html tags
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # keep only text and numbers
    junk_patterns = [
        r'thank.*', r'best regards.*', r'regards.*', r'hi team.*', r'dear team.*', r'dear .*', r'hello.*'
    ]
    for pattern in junk_patterns:
        text = re.sub(pattern, '', text)
    return text.strip()

def extract_subjects_and_first_complaints(folder_path):
    combined_texts = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            full_path = os.path.join(folder_path, filename)
            tree = ET.parse(full_path)
            root = tree.getroot()
            for ticket in root.findall('.//helpdesk-ticket'):
                subject_elem = ticket.find('subject')
                subject_text = clean_text(subject_elem.text) if subject_elem is not None else ""

                # Now also extract first conversation / note
                conversations = ticket.find('conversations')
                first_message = ""
                if conversations is not None:
                    first_conv = conversations.find('conversation')
                    if first_conv is not None:
                        body_elem = first_conv.find('body')
                        if body_elem is not None and body_elem.text:
                            first_message = clean_text(body_elem.text.split("\n")[0])  # take first line

                if subject_text or first_message:
                    combined_texts.append(subject_text + " " + first_message)
    return combined_texts

def generate_insights(folder_path):
    texts = extract_subjects_and_first_complaints(folder_path)
    word_counter = Counter()

    for text in texts:
        words = text.split()
        bigrams = [" ".join(words[i:i+2]) for i in range(len(words) - 1)]
        word_counter.update(bigrams)

    return word_counter.most_common(20)
