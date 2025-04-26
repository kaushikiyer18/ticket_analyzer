import pandas as pd

def analyze_tickets(tickets):
    df = pd.DataFrame(tickets)
    print(f"Total tickets: {len(df)}")
    print("\nTickets by Status:\n", df['status'].value_counts())

    if 'created_at' in df.columns and 'updated_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df['resolution_time_hours'] = (df['updated_at'] - df['created_at']).dt.total_seconds() / 3600
        print("\nAverage Resolution Time (hours): ", df['resolution_time_hours'].mean())
    return df