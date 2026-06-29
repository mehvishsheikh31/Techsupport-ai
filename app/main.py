from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agent import process_message, check_ticket
from app.database.models import init_db
import uvicorn

# Initialize FastAPI
app = FastAPI(
    title="TechSupport AI",
    description="Intelligent IT Helpdesk Agent",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation storage
conversations = {}

# Request models
class ChatRequest(BaseModel):
    session_id: str
    message: str
    user_name: str = "User"

class TicketRequest(BaseModel):
    ticket_id: str

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized!")

@app.get("/")
async def root():
    return {
        "message": "TechSupport AI is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Get or create conversation history
        if request.session_id not in conversations:
            conversations[request.session_id] = []
        
        history = conversations[request.session_id]
        
        # Process message
        result = process_message(
            user_message=request.message,
            conversation_history=history
        )
        
        # Update conversation history
        conversations[request.session_id] = history
        
        return {
            "success": True,
            "session_id": request.session_id,
            "response": result["response"],
            "issue_type": result["issue_type"],
            "priority": result["priority"],
            "ticket_info": result["ticket_info"],
            "escalation_msg": result["escalation_msg"],
            "kb_found": result["kb_found"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ticket/status")
async def ticket_status(request: TicketRequest):
    try:
        result = check_ticket(request.ticket_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "TechSupport AI is running!"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)