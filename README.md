# Ticket Analyzer Tool

This tool processes Freshdesk XML ticket exports and generates:
- A ticket metadata CSV file
- A full Customer Support Insights report with auto-clustering of problem types.

## Setup Instructions

1. Clone the repo
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git

2. Install dependencies
pip install -r requirements.txt

3. Place your XML files inside the xml_files/ folder.

4. Run the analyzer
python3 main.py

5. Output Files
ticket_analysis_output_YYYYMMDD.csv
insights_report_YYYYMMDD.txt

Author
Built by Kaushik Iyer 🚀

---
