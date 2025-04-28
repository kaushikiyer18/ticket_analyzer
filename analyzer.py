import pandas as pd

def analyze_tickets(tickets):
    df = pd.DataFrame(tickets)

    print(f"\nTotal tickets: {len(df)}")

    if 'priority' in df.columns:
        print("\nTickets by Priority:")
        print(df['priority'].value_counts())

    if 'ticket_type' in df.columns:
        print("\nTickets by Ticket Type:")
        print(df['ticket_type'].value_counts())

    if 'issue_type' in df.columns:
        print("\nTickets by Issue Type:")
        print(df['issue_type'].value_counts())

    return df
