import os
from groq import Groq
from dotenv import load_dotenv
from app.tools.ticket_tool import create_ticket, get_ticket_status, update_ticket_status
from app.tools.escalate_tool import (
    classify_priority, classify_issue_type,
    should_escalate, get_escalation_message,
    get_troubleshooting_steps
)
from app.tools.search_tool import search_it_solution

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are TechSupport AI, an intelligent IT helpdesk assistant. 
Your job is to help users solve their IT problems professionally and efficiently.

Your behavior:
1. UNDERSTAND the user's problem clearly
2. SEARCH for solutions in knowledge base
3. PROVIDE step-by-step troubleshooting guidance
4. CREATE tickets when needed
5. ESCALATE critical issues immediately

Response style:
- Be professional but friendly
- Use clear, simple language
- Always number your troubleshooting steps
- Be empathetic when users are frustrated
- Always mention ticket ID when created

You have access to:
- IT Knowledge Base (FAQs and solutions)
- Ticket Management System
- Escalation System

Never make up solutions. Always provide practical, actionable steps."""

def process_message(user_message: str, conversation_history: list) -> dict:
    """Process user message and return response with actions"""
    
    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    # Step 1 - Classify issue
    issue_type = classify_issue_type(user_message)
    priority = classify_priority(user_message)
    
    # Step 2 - Search knowledge base
    kb_result = search_it_solution(user_message)
    
    # Step 3 - Get troubleshooting steps
    troubleshooting = get_troubleshooting_steps(issue_type)
    
    # Step 4 - Check if ticket needed
    ticket_info = None
    escalation_msg = None
    
    # Keywords that trigger ticket creation
    ticket_keywords = [
        "nothing worked", "still not working", "tried everything",
        "please help", "urgent", "create ticket", "raise ticket",
        "not fixed", "same issue", "happening again"
    ]
    
    should_create_ticket = any(
        keyword in user_message.lower() 
        for keyword in ticket_keywords
    ) or priority in ["Critical", "High"]
    
    if should_create_ticket:
        ticket_info = create_ticket(
            description=user_message,
            issue_type=issue_type,
            priority=priority
        )
        
        if should_escalate(priority):
            escalation_msg = get_escalation_message(
                priority=priority,
                issue_type=issue_type,
                ticket_id=ticket_info["ticket_id"]
            )
    
    # Step 5 - Build context for LLM
    context = f"""
User Issue Analysis:
- Issue Type: {issue_type}
- Priority: {priority}

Knowledge Base Result:
{f"Found solution for: {kb_result['issue']}" if kb_result['found'] else "No exact match found"}
{f"Solution: {kb_result['solution']}" if kb_result['found'] else ""}

Suggested Troubleshooting Steps for {issue_type}:
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(troubleshooting)])}

{f"Ticket Created: {ticket_info['ticket_id']} (Priority: {priority})" if ticket_info else "No ticket created yet"}
"""
    
    # Step 6 - Get LLM response
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\nCurrent Context:\n{context}"}
    ] + conversation_history
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=1000,
        temperature=0.7
    )
    
    ai_response = response.choices[0].message.content
    
    # Add AI response to history
    conversation_history.append({
        "role": "assistant",
        "content": ai_response
    })
    
    return {
        "response": ai_response,
        "issue_type": issue_type,
        "priority": priority,
        "ticket_info": ticket_info,
        "escalation_msg": escalation_msg,
        "kb_found": kb_result["found"]
    }

def check_ticket(ticket_id: str) -> dict:
    """Check ticket status"""
    return get_ticket_status(ticket_id)