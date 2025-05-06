import xml.etree.ElementTree as ET

def parse_ticket_xml(file_path):
    tickets = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for ticket in root.findall(".//helpdesk-ticket"):
            t_data = {}
            t_data["ticket_id"] = ticket.findtext("display-id", default="N/A")
            t_data["subject"] = ticket.findtext("subject", default="N/A").strip()
            t_data["created_at"] = ticket.findtext("created-at", default="N/A")
            t_data["priority"] = ticket.findtext("priority", default="N/A")
            t_data["description"] = ticket.findtext("description", default="").strip()

            group_id = ticket.findtext("group-id", default="").strip()
            if not group_id:
                group_id = "unassigned"
            t_data["group_id"] = group_id

            t_data["type"] = ticket.findtext("ticket-type", default="N/A")  # new field for ticket type

            t_data["combined_text"] = f"{t_data['subject']} {t_data['description']}".strip()
            tickets.append(t_data)
    except Exception as e:
        print(f"❌ Failed to parse {file_path}: {e}")
    return tickets
