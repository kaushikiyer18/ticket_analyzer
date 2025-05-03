import xml.etree.ElementTree as ET

def parse_ticket_xml(file_path):
    tickets = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for ticket in root.findall(".//helpdesk-ticket"):
            ticket_data = {}

            ticket_data["ticket_id"] = ticket.findtext("display-id", default="N/A")
            ticket_data["created_at"] = ticket.findtext("created-at", default="N/A")
            ticket_data["priority"] = ticket.findtext("priority", default="N/A")
            ticket_data["subject"] = ticket.findtext("subject", default="N/A")

            # Extract only the customer complaint
            desc_elem = ticket.find("description")
            ticket_data["description"] = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

            ticket_data["combined_text"] = f"{ticket_data['subject']} {ticket_data['description']}".strip()

            tickets.append(ticket_data)

    except Exception as e:
        print(f"❌ Failed to parse {file_path}: {e}")

    return tickets
