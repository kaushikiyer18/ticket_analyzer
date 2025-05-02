# trend_categories.py

TREND_CATEGORIES = {
    # DLT / SMS issues
    "dlt|sender id|sms failure|template rejection|netcore certified": "DLT Configuration Issues",

    # Email delivery issues
    "email error|smtp|not received|bounce|email failure|blocked|email delivery": "Email Delivery Failures",

    # Login & authentication
    "login|authentication|access denied|not able to login|session expired|2fa": "Access & Authentication Issues",

    # Approvals
    "approval pending|submitted for approval|approval delay|awaiting approval": "Approval Delays",

    # Escalations / urgency
    "escalation|urgent|pending since|follow up|still waiting": "High Escalation Volume",

    # Order or billing
    "invoice|billing|order not received|payment failed": "Order/Billing Problems",

    # WhatsApp-related
    "whatsapp|bot|template not triggering|waba": "WhatsApp Channel Issues",

    # Campaigns
    "campaign|schedule|delay in execution|not triggering": "Campaign Execution Issues",

    # Generic tech issues
    "not working|error|fail|crash|issue|bug|unable to|does not work": "Generic System Errors"
}
