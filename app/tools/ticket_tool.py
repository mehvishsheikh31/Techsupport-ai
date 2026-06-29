from sqlalchemy.orm import Session
from app.database.models import Ticket, SessionLocal
from datetime import datetime
import random
import string

def generate_ticket_id():
    """Generate unique ticket ID"""
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"TK-{datetime.now().strftime('%Y%m%d')}-{random_part}"

def create_ticket(description: str, issue_type: str, priority: str, user_name: str = "User") -> dict:
    """Create a new support ticket"""
    db: Session = SessionLocal()
    try:
        ticket_id = generate_ticket_id()
        
        ticket = Ticket(
            ticket_id=ticket_id,
            user_name=user_name,
            issue_type=issue_type,
            priority=priority,
            status="Open",
            description=description,
            created_at=datetime.now()
        )
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "priority": priority,
            "issue_type": issue_type,
            "status": "Open",
            "message": f"Ticket {ticket_id} created successfully!"
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()

def get_ticket_status(ticket_id: str) -> dict:
    """Get status of existing ticket"""
    db: Session = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        
        if not ticket:
            return {
                "success": False,
                "message": f"Ticket {ticket_id} not found!"
            }
        
        return {
            "success": True,
            "ticket_id": ticket.ticket_id,
            "status": ticket.status,
            "priority": ticket.priority,
            "issue_type": ticket.issue_type,
            "description": ticket.description,
            "created_at": str(ticket.created_at),
            "updated_at": str(ticket.updated_at)
        }
    finally:
        db.close()

def update_ticket_status(ticket_id: str, status: str) -> dict:
    """Update ticket status"""
    db: Session = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        
        if not ticket:
            return {"success": False, "message": f"Ticket {ticket_id} not found!"}
        
        ticket.status = status
        ticket.updated_at = datetime.now()
        db.commit()
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "new_status": status,
            "message": f"Ticket {ticket_id} updated to {status}"
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()

def get_all_tickets() -> list:
    """Get all tickets"""
    db: Session = SessionLocal()
    try:
        tickets = db.query(Ticket).all()
        return [
            {
                "ticket_id": t.ticket_id,
                "status": t.status,
                "priority": t.priority,
                "issue_type": t.issue_type,
                "description": t.description[:50] + "...",
                "created_at": str(t.created_at)
            }
            for t in tickets
        ]
    finally:
        db.close()