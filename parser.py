import xml.etree.ElementTree as ET
import os

def parse_ticket_xml(file_path):
    tickets = []
    context = ET.iterparse(file_path, events=("start", "end"))
    _, root = next(context)

    ticket = {}
    for event, elem in context:
        if event == "end":
            if elem.tag == "ticket":
                tickets.append(ticket.copy())
                ticket.clear()
            elif elem.tag in {"id", "subject", "status", "priority", "created_at", "updated_at"}:
                ticket[elem.tag] = elem.text
        elem.clear()
    return tickets

def parse_all_xmls(folder_path):
    all_tickets = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            full_path = os.path.join(folder_path, filename)
            tickets = parse_ticket_xml(full_path)
            all_tickets.extend(tickets)
    return all_tickets