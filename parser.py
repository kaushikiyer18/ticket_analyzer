import xml.etree.ElementTree as ET
import os
import html

def parse_ticket_xml(file_path):
    tickets = []
    tree = ET.parse(file_path)
    root = tree.getroot()

    for ticket_elem in root.findall('.//helpdesk-ticket'):
        display_id = safe_find_text(ticket_elem, 'display-id')
        subject = safe_find_text(ticket_elem, 'subject')
        priority = safe_find_text(ticket_elem, 'priority')
        ticket_type = safe_find_text(ticket_elem, 'ticket-type')
        created_at = safe_find_text(ticket_elem, 'created-at')
        account_tier = safe_find_text(ticket_elem, 'custom-field:account-tier')
        issue_type = safe_find_text(ticket_elem, 'custom-field:issue-type')
        company_name = safe_find_text(ticket_elem, 'company-name')

        ticket = {
            'ticket_id': display_id,
            'subject': subject,
            'priority': priority,
            'ticket_type': ticket_type,
            'created_at': created_at,
            'account_tier': account_tier,
            'issue_type': issue_type,
            'company_name': company_name
        }
        tickets.append(ticket)
    return tickets

def safe_find_text(element, tag_name):
    tag = element.find(tag_name)
    if tag is not None and tag.text:
        return tag.text.strip()
    return ''

def parse_all_xmls(folder_path):
    all_tickets = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            full_path = os.path.join(folder_path, filename)
            tickets = parse_ticket_xml(full_path)
            all_tickets.extend(tickets)
    return all_tickets
