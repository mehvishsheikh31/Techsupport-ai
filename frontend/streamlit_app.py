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

def send_message(message: str):
    """Send message to API and store response"""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "session_id": st.session_state.session_id,
                "message": message,
                "user_name": "User"
            }
        )
        if response.status_code == 200:
            data = response.json()

            # Store ticket if created
            if data.get("ticket_info") and data["ticket_info"].get("success"):
                ticket = data["ticket_info"]
                # Avoid duplicate tickets
                existing_ids = [t["ticket_id"] for t in st.session_state.tickets]
                if ticket["ticket_id"] not in existing_ids:
                    st.session_state.tickets.append(ticket)

            return data
    except requests.exceptions.ConnectionError:
        return None

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
            if message.get("ticket_id"):
                st.markdown(f"""
                <div class='ticket-box'>
                🎫 <b>Ticket Created!</b><br>
                ID: <b>{message['ticket_id']}</b><br>
                Priority: {message.get('priority', 'N/A')}<br>
                Status: Open
                </div>
                """, unsafe_allow_html=True)
            if message.get("escalation_msg"):
                st.markdown(f"""
                <div class='escalation-box'>
                {message['escalation_msg']}
                </div>
                """, unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Describe your IT issue here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Analyzing your issue..."):
            data = send_message(prompt)

        if data:
            assistant_msg = {
                "role": "assistant",
                "content": data["response"],
            }
            if data.get("ticket_info") and data["ticket_info"].get("success"):
                assistant_msg["ticket_id"] = data["ticket_info"]["ticket_id"]
                assistant_msg["priority"] = data["ticket_info"]["priority"]
            if data.get("escalation_msg"):
                assistant_msg["escalation_msg"] = data["escalation_msg"]

            st.session_state.messages.append(assistant_msg)
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "❌ Cannot connect to API! Make sure FastAPI server is running."
            })

        st.rerun()

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
                        st.error(data.get("message", "Ticket not found!"))
            except:
                st.error("❌ Cannot connect to API!")

    st.divider()

    # Session tickets
    st.subheader("📋 Your Tickets")
    if st.session_state.tickets:
        for ticket in st.session_state.tickets:
            priority = ticket.get("priority", "Low")
            st.markdown(f"""
            <div class='ticket-box'>
            🎫 <b>{ticket['ticket_id']}</b><br>
            Priority: {priority}<br>
            Status: {ticket.get('status', 'Open')}
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
            st.session_state.messages.append({"role": "user", "content": issue})

            data = send_message(issue)

            if data:
                assistant_msg = {
                    "role": "assistant",
                    "content": data["response"],
                }
                if data.get("ticket_info") and data["ticket_info"].get("success"):
                    assistant_msg["ticket_id"] = data["ticket_info"]["ticket_id"]
                    assistant_msg["priority"] = data["ticket_info"]["priority"]
                if data.get("escalation_msg"):
                    assistant_msg["escalation_msg"] = data["escalation_msg"]
                st.session_state.messages.append(assistant_msg)
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "❌ Cannot connect to API!"
                })
            st.rerun()

    st.divider()

    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.tickets = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()