from datetime import datetime

# Priority rules based on keywords
CRITICAL_KEYWORDS = [
    "server down", "data loss", "breach", "hacked", "ransomware",
    "entire network", "production down", "database corrupt", "all users affected",
    "security", "virus", "malware", "data deleted"
]

HIGH_KEYWORDS = [
    "cannot work", "urgent", "important", "deadline", "meeting",
    "vpn not working", "email down", "printer not working", "laptop crashed",
    "blue screen", "not starting", "password locked", "access denied"
]

MEDIUM_KEYWORDS = [
    "slow", "lagging", "software issue", "update", "install",
    "error message", "not responding", "freezing", "wifi issue"
]

def classify_priority(issue_description: str) -> str:
    """Classify issue priority based on keywords"""
    text = issue_description.lower()
    
    for keyword in CRITICAL_KEYWORDS:
        if keyword in text:
            return "Critical"
    
    for keyword in HIGH_KEYWORDS:
        if keyword in text:
            return "High"
    
    for keyword in MEDIUM_KEYWORDS:
        if keyword in text:
            return "Medium"
    
    return "Low"

def classify_issue_type(issue_description: str) -> str:
    """Classify issue type based on keywords"""
    text = issue_description.lower()
    
    if any(word in text for word in ["network", "wifi", "internet", "vpn", "connection", "ethernet"]):
        return "Network"
    elif any(word in text for word in ["laptop", "computer", "hardware", "keyboard", "mouse", "screen", "monitor", "printer"]):
        return "Hardware"
    elif any(word in text for word in ["software", "app", "application", "install", "update", "program", "crash", "error"]):
        return "Software"
    elif any(word in text for word in ["password", "access", "login", "account", "locked", "permission"]):
        return "Access"
    elif any(word in text for word in ["email", "outlook", "teams", "zoom", "office"]):
        return "Communication"
    else:
        return "General"

def should_escalate(priority: str) -> bool:
    """Determine if issue needs human escalation"""
    return priority in ["Critical", "High"]

def get_escalation_message(priority: str, issue_type: str, ticket_id: str) -> str:
    """Generate escalation message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if priority == "Critical":
        return f"""
🚨 CRITICAL ESCALATION ALERT 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ticket ID  : {ticket_id}
Priority   : CRITICAL
Issue Type : {issue_type}
Time       : {timestamp}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ A senior IT engineer has been notified immediately!
Expected response time: Within 15 minutes
"""
    elif priority == "High":
        return f"""
⚠️ HIGH PRIORITY ESCALATION ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ticket ID  : {ticket_id}
Priority   : HIGH
Issue Type : {issue_type}
Time       : {timestamp}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👨‍💻 An IT engineer has been assigned to your ticket!
Expected response time: Within 2 hours
"""
    else:
        return f"""
✅ Ticket Assigned
Ticket ID  : {ticket_id}
Priority   : {priority}
Issue Type : {issue_type}
Time       : {timestamp}
Expected response time: Within 24 hours
"""

def get_troubleshooting_steps(issue_type: str) -> list:
    """Get basic troubleshooting steps based on issue type"""
    steps = {
        "Network": [
            "Check if WiFi/Ethernet cable is properly connected",
            "Try turning WiFi off and on again",
            "Restart your router/modem",
            "Check if other devices can connect to internet",
            "Try forgetting and reconnecting to WiFi network",
            "Flush DNS: Run 'ipconfig /flushdns' in Command Prompt"
        ],
        "Hardware": [
            "Restart your computer completely",
            "Check all cable connections",
            "Check if device is properly powered on",
            "Try using device on another port/slot",
            "Check Device Manager for any error flags",
            "Run hardware diagnostics if available"
        ],
        "Software": [
            "Close and reopen the application",
            "Restart your computer",
            "Check for pending software updates",
            "Clear application cache/temp files",
            "Uninstall and reinstall the application",
            "Check if antivirus is blocking the software"
        ],
        "Access": [
            "Verify you are using correct username",
            "Try resetting your password",
            "Check if Caps Lock is on",
            "Clear browser cookies and cache",
            "Try logging in from a different browser",
            "Contact admin if account may be locked"
        ],
        "Communication": [
            "Check internet connection first",
            "Sign out and sign back into the application",
            "Clear application cache",
            "Check if service is down (visit status page)",
            "Reinstall the communication application",
            "Check firewall settings"
        ],
        "General": [
            "Restart your computer",
            "Check for any pending updates",
            "Run a virus scan",
            "Check available disk space",
            "Contact IT support with detailed description"
        ]
    }
    return steps.get(issue_type, steps["General"])