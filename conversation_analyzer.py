import os
import datetime
import pandas as pd
import xml.etree.ElementTree as ET
from trend_categories import TREND_KEYWORDS
from ticket_tagging_rules import TICKET_TYPE_RULES, ISSUE_TYPE_RULES
import openai

# Load OpenAI key (injected by Streamlit Cloud)
openai.api_key = os.getenv("OPENAI_API_KEY")

def score_keywords(text, keywords):
    text_lower = text.lower()
    return sum(1 for word in keywords if word.lower() in text_lower)

def classify_tag(text, rules):
    text = text.lower()
    best_match = None
    best_score = 0
    for tag, keywords in rules.items():
        score = score_keywords(text, keywords)
        if score > best_score and score >= 1:
            best_match = tag
            best_score = score
    return best_match if best_match else "Unknown"

def summarize_text_gpt(content, instruction):
    if not content or len(content.strip()) < 10:
        return "Not enough content"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": content}
            ],
            max_tokens=100,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ GPT summarization failed: {e}")
        return "Could not summarize"

def generate_insights(folder_path):
    today = datetime.datetime.now().strftime("%Y%m%d")
    enriched_csv_file = f"ticket_analysis_output_{today}.csv"
    categorized_map_file = f"categorized_ticket_map_{today}.csv"
    insights_file = f"insights_report_{today}.txt"
    unmatched_file = f"unmatched_samples_{today}.txt"

    trend_map = {}
    unmatched = []
    enriched_rows = []
    categorized_rows = []

    for file in os.listdir(folder_path):
        if file.endswith(".xml"):
            try:
                tree = ET.parse(os.path.join(folder_path, file))
                root = tree.getroot()
                for ticket in root.findall(".//helpdesk-ticket"):
                    tid = ticket.findtext("display-id", default="N/A").strip()
                    created = ticket.findtext("created-at", default="N/A").strip()
                    priority = ticket.findtext("priority", default="N/A").strip()
                    subject = ticket.findtext("subject", default="").strip()
                    description = ticket.findtext("description", default="").strip()
                    current_type = ticket.findtext("ticket-type", default="N/A").strip()
                    current_issue = ticket.findtext("issue-type", default="N/A").strip()

                    # Agent replies
                    agent_text = " ".join([
                        note.findtext("body", default="").strip()
                        for note in ticket.findall(".//helpdesk-note")
                        if note.findtext("body", default="").strip()
                    ])

                    combined_text = f"{subject} {description}".strip()

                    # Summarize using GPT
                    summary_problem = summarize_text_gpt(combined_text, "Summarize the user's problem in 1-2 lines.")
                    summary_resolution = summarize_text_gpt(agent_text, "Summarize the agent's resolution in 1-2 lines.")

                    # Auto-tagging
                    ticket_type_tagged = classify_tag(combined_text, TICKET_TYPE_RULES)
                    issue_type_tagged = classify_tag(agent_text, ISSUE_TYPE_RULES)

                    # Trend detection
                    best_match = None
                    best_score = 0
                    for category, keywords in TREND_KEYWORDS.items():
                        score = score_keywords(combined_text.lower(), keywords)
                        if score >= 3 and score > best_score:
                            best_match = category
                            best_score = score

                    if best_match:
                        trend_map.setdefault(best_match, []).append(combined_text)
                        categorized_rows.append({
                            "Category": best_match,
                            "Ticket ID": tid,
                            "Subject": subject,
                            "Created At": created,
                            "Priority": priority,
                            "Type": best_match
                        })
                    else:
                        unmatched.append(combined_text)

                    # Final enriched row
                    enriched_rows.append({
                        "Ticket ID": tid,
                        "Subject": subject,
                        "Summary of Problem Statement": summary_problem,
                        "Created": created,
                        "Current Ticket Type": current_type,
                        "Ticket Type (Auto Tagged)": ticket_type_tagged,
                        "Priority (Auto Tagged)": priority,
                        "Current Issue Type": current_issue,
                        "Issue Type (Auto Tagged)": issue_type_tagged,
                        "Summary of Resolution (by agent)": summary_resolution
                    })

            except Exception as e:
                print(f"Error processing file {file}: {e}")

    # Save files
    if enriched_rows:
        pd.DataFrame(enriched_rows).to_csv(enriched_csv_file, index=False)

    if categorized_rows:
        pd.DataFrame(categorized_rows).to_csv(categorized_map_file, index=False)

    if unmatched:
        with open(unmatched_file, "w") as f:
            f.write("Unmatched Samples\n" + "=" * 20 + "\n\n")
            for line in unmatched:
                f.write(f"{line}\n\n")

    with open(insights_file, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("=" * 40 + "\n")
        f.write(f"Generated on: {today}\n\n")
        for category, samples in sorted(trend_map.items(), key=lambda x: len(x[1]), reverse=True):
            f.write(f"🔹 {category} ({len(samples)} occurrences)\n\n")
