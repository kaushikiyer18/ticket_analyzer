import os
import xml.etree.ElementTree as ET

def parse_ticket_xml(file_path):
    tickets = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for ticket in root.findall(".//helpdesk-ticket"):
            ticket_data = {}

            # Ticket ID
            ticket_id_elem = ticket.find("id")
            ticket_data["ticket_id"] = ticket_id_elem.text if ticket_id_elem is not None else None

            # Only extract the customer complaint from <description>
            desc_elem = ticket.find("description")
            ticket_data["description"] = desc_elem.text.strip() if desc_elem is not None else ""

            # Optional: include subject for additional signal
            subject_elem = ticket.find("subject")
            ticket_data["subject"] = subject_elem.text.strip() if subject_elem is not None else ""

            # Combine for analysis
            combined_text = f"{ticket_data['subject']} {ticket_data['description']}".strip()
            ticket_data["combined_text"] = combined_text

            tickets.append(ticket_data)

    except Exception as e:
        print(f"❌ Failed to parse {file_path}: {e}")

    return tickets
