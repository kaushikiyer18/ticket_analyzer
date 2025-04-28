import os
import pandas as pd
from datetime import datetime
from parser import parse_all_xmls
from analyzer import analyze_tickets
from conversation_analyzer import generate_insights

def job():
    folder_path = "/Users/kaushik.iyer/Documents/ticket_analyzer/xml_files"  # Your folder path

    tickets = parse_all_xmls(folder_path)
    if not tickets:
        print("No tickets found.")
        return

    df = analyze_tickets(tickets)
    
    today = datetime.today().strftime('%Y%m%d')
    output_csv = f"ticket_analysis_output_{today}.csv"
    df.to_csv(output_csv, index=False)

    print(f"✅ Ticket data saved to {output_csv}")

    insights = generate_insights(folder_path)
    output_txt = f"insights_report_{today}.txt"

    with open(output_txt, "w") as f:
        f.write("Customer Support Trends Report\n")
        f.write("="*60 + "\n\n")
        f.write(f"Generated on: {today}\n\n")
        f.write("Top Problem Patterns:\n")
        f.write("-"*30 + "\n")
        for phrase, count in insights:
            f.write(f"- {phrase} ({count} occurrences)\n")

    print(f"✅ Insights report saved to {output_txt}")

if __name__ == "__main__":
    job()
