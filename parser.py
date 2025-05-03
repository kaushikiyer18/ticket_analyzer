import xml.etree.ElementTree as ET

def parse_ticket_xml(file_path):
    tickets = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for ticket in root.findall(".//helpdesk-ticket"):
            ticket_data = {}

            # Extract relevant fields
            ticket_data["display_id"] = ticket.findtext("display-id", default="").strip()
            ticket_data["subject"] = ticket.findtext("subject", default="").strip()
            ticket_data["created_at"] = ticket.findtext("created-at", default="").strip()
            ticket_data["priority"] = ticket.findtext("priority", default="").strip()
            ticket_data["ticket_type"] = ticket.findtext("ticket-type", default="").strip()
            ticket_data["description"] = ticket.findtext("description", default="").strip()

            # Combine for analysis
            ticket_data["combined_text"] = f"{ticket_data['subject']} {ticket_data['description']}".strip()

            tickets.append(ticket_data)

    except Exception as e:
        print(f"❌ Failed to parse {file_path}: {e}")
    return tickets
