import schedule
import time
from parser import parse_all_xmls
from analyzer import analyze_tickets

def job():
    folder_path = "/Users/kaushik.iyer/Downloads"  # <-- Change this!
    tickets = parse_all_xmls(folder_path)
    if not tickets:
        print("No tickets found.")
        return
    df = analyze_tickets(tickets)
    df.to_csv('ticket_analysis_output.csv', index=False)
    print("✅ Analysis completed and saved to ticket_analysis_output.csv!")

if __name__ == "__main__":
    schedule.every().day.at("01:00").do(job)  # runs daily at 1 AM

    print("🚀 Ticket analyzer started. Waiting for schedule...")
    while True:
        schedule.run_pending()
        time.sleep(60)
