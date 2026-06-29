import streamlit as st
import requests
import uuid

# Page config
st.set_page_config(
    page_title="TechSupport AI",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f, #2196F3);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .ticket-box {
        background: #1e3a5f;
        border: 1px solid #2196F3;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: white;
    }
    .priority-critical { color: #ff4444; font-weight: bold; }
    .priority-high { color: #ff8800; font-weight: bold; }
    .priority-medium { color: #ffcc00; font-weight: bold; }
    .priority-low { color: #44ff44; font-weight: bold; }
    .escalation-box {
        background: #3a1e1e;
        border: 2px solid #ff4444;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: white;
    }
    .stChatMessage { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# API URL
API_URL = "http://localhost:8000"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tickets" not in st.session_state:
    st.session_state.tickets = []

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 TechSupport AI</h1>
    <p>Intelligent IT Helpdesk Agent | Available 24/7</p>
</div>
""", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Chat with TechSupport AI")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Describe your IT issue here..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your issue..."):
                try:
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "session_id": st.session_state.session_id,
                            "message": prompt,
                            "user_name": "User"
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Show AI response
                        st.markdown(data["response"])
                        
                        # Show issue metadata
                        priority = data.get("priority", "Low")
                        issue_type = data.get("issue_type", "General")
                        
                        priority_class = f"priority-{priority.lower()}"
                        st.markdown(f"""
                        <small>
                        🏷️ Type: <b>{issue_type}</b> | 
                        ⚡ Priority: <span class='{priority_class}'>{priority}</span> |
                        📚 KB Match: {'✅' if data.get('kb_found') else '❌'}
                        </small>
                        """, unsafe_allow_html=True)
                        
                        # Show ticket info
                        if data.get("ticket_info"):
                            ticket = data["ticket_info"]
                            st.session_state.tickets.append(ticket)
                            st.markdown(f"""
                            <div class='ticket-box'>
                            🎫 <b>Ticket Created!</b><br>
                            ID: <b>{ticket['ticket_id']}</b><br>
                            Priority: {ticket['priority']}<br>
                            Status: {ticket['status']}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Show escalation
                        if data.get("escalation_msg"):
                            st.markdown(f"""
                            <div class='escalation-box'>
                            {data['escalation_msg']}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Add to message history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": data["response"]
                        })
                    
                    else:
                        st.error("API Error! Make sure FastAPI server is running.")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API! Run: uvicorn app.main:app --reload")

with col2:
    st.subheader("🎫 Ticket Tracker")
    
    # Ticket status checker
    ticket_id_input = st.text_input("Check Ticket Status:", placeholder="TK-20260630-1234")
    
    if st.button("🔍 Check Status"):
        if ticket_id_input:
            try:
                response = requests.post(
                    f"{API_URL}/ticket/status",
                    json={"ticket_id": ticket_id_input}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        st.markdown(f"""
                        <div class='ticket-box'>
                        🎫 <b>{data['ticket_id']}</b><br>
                        Status: <b>{data['status']}</b><br>
                        Priority: {data['priority']}<br>
                        Type: {data['issue_type']}<br>
                        Created: {data['created_at'][:19]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(data.get("message"))
            except:
                st.error("Cannot connect to API!")
    
    st.divider()
    
    # Session tickets
    st.subheader("📋 Your Tickets")
    if st.session_state.tickets:
        for ticket in st.session_state.tickets:
            st.markdown(f"""
            <div class='ticket-box'>
            🎫 <b>{ticket['ticket_id']}</b><br>
            Priority: {ticket['priority']}<br>
            Status: {ticket['status']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No tickets created yet.")
    
    st.divider()
    
    # Quick issue buttons
    st.subheader("⚡ Quick Issues")
    quick_issues = [
        "My VPN is not connecting",
        "I forgot my password",
        "My computer is very slow",
        "Printer is not working",
        "Email is not working",
        "Blue screen error"
    ]
    
    for issue in quick_issues:
        if st.button(issue, use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": issue
            })
            st.rerun()
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):