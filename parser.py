
import xml.etree.ElementTree as ET

def parse_ticket_xml(file_path):
    tickets = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for ticket in root.findall(".//helpdesk-ticket"):
            t_data = {}
            t_data["ticket_id"] = ticket.findtext("display-id", default="N/A").strip()
            t_data["subject"] = ticket.findtext("subject", default="N/A").strip()
            t_data["created_at"] = ticket.findtext("created-at", default="N/A").strip()
            t_data["priority"] = ticket.findtext("priority", default="N/A").strip()
            t_data["description"] = ticket.findtext("description", default="").strip()
            t_data["type"] = ticket.findtext("ticket-type", default="Unknown").strip()

            group_id = ticket.findtext("group-id", default="").strip()
            if not group_id:
                group_id = "unassigned"
            t_data["group_id"] = group_id

            # Extract current issue type from <custom_field>
            custom_field = ticket.find("custom_field")
            if custom_field is not None:
                issue_type = custom_field.findtext("cf_issue_type_430969", default="N/A").strip()
            else:
                issue_type = "N/A"
            t_data["current_issue_type"] = issue_type

            t_data["combined_text"] = f"{t_data['subject']} {t_data['description']}".strip()
            tickets.append(t_data)
    except Exception as e:
        print(f"❌ Failed to parse {file_path}: {e}")
    return tickets
