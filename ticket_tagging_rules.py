# ticket_tagging_rules.py

TICKET_TYPE_RULES = {
    "CEE - API issue": ["api error", "authentication failed", "invalid api key", "missing parameter"],
    "CEE - Campaign issue": ["campaign failed", "campaign not sent", "campaign paused"],
    "CEE - Customer queries": ["customer asked", "customer query", "confused", "clarification"],
    "CEE - Database uploading issue": ["upload failed", "file upload", "csv not uploading", "upload stuck"],
    "CEE - Event not reflecting": ["event not received", "event missing", "event delay"],
    "CEE - Journey issue": ["journey not triggered", "flow stuck", "journey failed"],
    "CEE - Reports issue": ["report missing", "report incorrect", "analytics not loading"],
    "CEE - Segment issue": ["segment not updating", "segment issue", "segment missing"],
    "CEE - UI Functional issues/bugs": ["button not working", "screen blank", "ui not responsive", "not clickable"],
    "CEE - Webhooks issue": ["webhook failed", "webhook not received", "webhook error"],
    "CEE - SFTP issue": ["sftp failed", "sftp connection", "sftp access", "sftp upload"],
    "CEE - Spam issues": ["marked spam", "spam folder", "email flagged"],
    "CEE - Task": ["to be done", "create task", "task pending"],
    "CEE - Template issue": ["template broken", "template not loading", "template issue"],
    "CEE - Non Relevant": ["test ticket", "demo", "trial", "sample"],
}

ISSUE_TYPE_RULES = {
    "Configuration": ["misconfigured", "wrong setting", "incorrect setup"],
    "Enhancement": ["feature request", "suggestion", "enhancement"],
    "Global incident": ["outage", "major issue", "downtime", "widespread"],
    "Integration": ["integration failed", "api error", "webhook failed", "sftp"],
    "Knowledge": ["documentation missing", "not aware", "did not know", "unaware"],
    "Monitoring": ["alert not received", "monitoring issue", "threshold breach"],
    "No Concern": ["no issue found", "everything okay", "working fine"],
    "Query": ["how to", "can i", "query", "clarification"],
    "One-time incident": ["happened once", "isolated issue", "rare occurrence"],
    "Task": ["pending item", "to-do", "next step", "internal task"],
    "Tech": ["bug", "error", "code fix", "backend issue", "deployment"],
}
