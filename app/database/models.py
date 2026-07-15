from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True)
    user_name = Column(String, default="User")
    issue_type = Column(String)  # network, hardware, software, access
    priority = Column(String)    # Low, Medium, High, Critical
    status = Column(String, default="Open")  # Open, In Progress, Resolved
    description = Column(Text)
    solution_attempted = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# Database setup
# NOTE: We build an absolute path (based on this file's location) instead of a
# relative one. A relative path like "sqlite:///./app/database/tickets.db"
# resolves against whatever directory the process happens to be launched from.
# That meant the FastAPI server and the Streamlit admin dashboard could end up
# reading/writing two DIFFERENT database files if launched from different
# folders -- tickets created in the chatbot wouldn't show up in the dashboard.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'tickets.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()