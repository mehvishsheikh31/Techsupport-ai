import streamlit as st
import requests
import uuid
import os

# Page config
st.set_page_config(
    page_title="TechSupport AI",
    page_icon="🖥️",
    layout="wide"
)

# ──────────────────────────────────────────────────────────────────────────
# Theme: "Command Center" — a dark ops-console look built for an IT helpdesk
# tool. Monospace ticket IDs, status LEDs, and a live-system header replace
# the generic blue-gradient-card look of a typical chatbot UI.
# ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

    :root {
        --bg: #0A0E17;
        --panel: #111827;
        --panel-border: #1F2937;
        --accent: #FBBF24;
        --accent-2: #22D3EE;
        --text: #E5E7EB;
        --text-dim: #8B96A8;
        --critical: #F87171;
        --high: #FB923C;
        --medium: #FBBF24;
        --low: #34D399;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--text);
    }
    .stApp { background: var(--bg); }

    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }

    /* ── Header / system bar ─────────────────────────────────────────── */
    .console-header {
        background: linear-gradient(180deg, #0F1729 0%, #0A0E17 100%);
        border: 1px solid var(--panel-border);
        border-radius: 12px;
        padding: 22px 28px;
        margin-bottom: 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .console-header h1 {
        margin: 0;
        font-size: 1.65rem;
        letter-spacing: 0.02em;
        color: #fff;
    }
    .console-header p {
        margin: 4px 0 0 0;
        color: var(--text-dim);
        font-size: 0.88rem;
    }
    .status-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        color: var(--low);
        background: rgba(52, 211, 153, 0.1);
        border: 1px solid rgba(52, 211, 153, 0.35);
        padding: 6px 14px;
        border-radius: 100px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .led-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: var(--low);
        box-shadow: 0 0 8px var(--low);
        animation: pulse 1.8s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.35; }
    }

    /* ── Section labels ───────────────────────────────────────────────── */
    .panel-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        color: var(--text-dim);
        text-transform: uppercase;
        margin-bottom: 10px;
        border-bottom: 1px solid var(--panel-border);
        padding-bottom: 8px;
    }

    /* ── Ticket / escalation cards ───────────────────────────────────── */
    .ticket-box {
        background: var(--panel);
        border: 1px solid var(--panel-border);
        border-left: 3px solid var(--accent-2);
        border-radius: 8px;
        padding: 14px 16px;
        margin: 10px 0;
        color: var(--text);
        font-size: 0.9rem;
    }
    .ticket-id {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: var(--accent-2);
        letter-spacing: 0.02em;
    }
    .escalation-box {
        background: rgba(248, 113, 113, 0.07);
        border: 1px solid rgba(248, 113, 113, 0.4);
        border-radius: 8px;
        padding: 14px 16px;
        margin: 10px 0;
        color: var(--text);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        white-space: pre-wrap;
    }

    .priority-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        padding: 2px 9px;
        border-radius: 100px;
        display: inline-block;
    }
    .priority-Critical { background: rgba(248,113,113,0.15); color: var(--critical); border: 1px solid rgba(248,113,113,0.4); }
    .priority-High      { background: rgba(251,146,60,0.15); color: var(--high); border: 1px solid rgba(251,146,60,0.4); }
    .priority-Medium    { background: rgba(251,191,36,0.15); color: var(--medium); border: 1px solid rgba(251,191,36,0.4); }
    .priority-Low       { background: rgba(52,211,153,0.15); color: var(--low); border: 1px solid rgba(52,211,153,0.4); }

    /* ── Buttons ──────────────────────────────────────────────────────── */
    .stButton > button {
        background: var(--panel) !important;
        color: var(--text) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }

    div[data-testid="stChatInput"] textarea {
        font-family: 'Inter', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

# API URL — override with `API_URL` env var when the backend runs elsewhere
# (e.g. a separate container/host in production instead of localhost:8000).
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tickets" not in st.session_state:
    st.session_state.tickets = []


def send_message(message: str):
    """Send message to API and store response.
    Returns (data, error_message). error_message is None on success."""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "session_id": st.session_state.session_id,
                "message": message,
                "user_name": "User"
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ticket_info") and data["ticket_info"].get("success"):
                ticket = data["ticket_info"]
                existing_ids = [t["ticket_id"] for t in st.session_state.tickets]
                if ticket["ticket_id"] not in existing_ids:
                    st.session_state.tickets.append(ticket)
            return data, None
        else:
            try:
                detail = response.json().get("detail", "Unknown server error.")
            except Exception:
                detail = f"Server returned status {response.status_code}."
            return None, detail
    except requests.exceptions.ConnectionError:
        return None, "connection"
    except requests.exceptions.Timeout:
        return None, "The request took too long to respond. Please try again."
    except Exception as e:
        return None, f"Unexpected error: {e}"


def append_assistant_reply(data):
    assistant_msg = {"role": "assistant", "content": data["response"]}
    if data.get("ticket_info") and data["ticket_info"].get("success"):
        assistant_msg["ticket_id"] = data["ticket_info"]["ticket_id"]
        assistant_msg["priority"] = data["ticket_info"]["priority"]
    if data.get("escalation_msg"):
        assistant_msg["escalation_msg"] = data["escalation_msg"]
    st.session_state.messages.append(assistant_msg)


def append_error_reply(error_message):
    if error_message == "connection":
        text = f"⚠️ Can't reach the TechSupport AI backend at `{API_URL}`. Make sure the FastAPI server is running (`uvicorn app.main:app`)."
    else:
        text = f"⚠️ {error_message}"
    st.session_state.messages.append({"role": "assistant", "content": text})


# Header
st.markdown("""
<div class="console-header">
    <div>
        <h1>🖥️ TechSupport AI</h1>
        <p>Intelligent IT Helpdesk Agent · Automated triage, troubleshooting & ticketing</p>
    </div>
    <div class="status-pill"><span class="led-dot"></span> SYSTEM ONLINE</div>
</div>
""", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="panel-label">💬 LIVE CHAT</div>', unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("ticket_id"):
                priority = message.get("priority", "Low")
                st.markdown(f"""
                <div class='ticket-box'>
                🎫 <b>Ticket Created</b><br>
                ID: <span class="ticket-id">{message['ticket_id']}</span><br>
                Priority: <span class="priority-badge priority-{priority}">{priority}</span><br>
                Status: Open
                </div>
                """, unsafe_allow_html=True)
            if message.get("escalation_msg"):
                st.markdown(f"""
                <div class='escalation-box'>{message['escalation_msg']}</div>
                """, unsafe_allow_html=True)

    if prompt := st.chat_input("Describe your IT issue here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Analyzing your issue..."):
            data, error = send_message(prompt)

        if data:
            append_assistant_reply(data)
        else:
            append_error_reply(error)

        st.rerun()

with col2:
    st.markdown('<div class="panel-label">🎫 TICKET TRACKER</div>', unsafe_allow_html=True)

    ticket_id_input = st.text_input("Check ticket status", placeholder="TK-20260715-1234", label_visibility="collapsed")

    if st.button("🔍 Check Status", use_container_width=True):
        if ticket_id_input:
            try:
                response = requests.post(
                    f"{API_URL}/ticket/status",
                    json={"ticket_id": ticket_id_input},
                    timeout=15
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        st.markdown(f"""
                        <div class='ticket-box'>
                        🎫 <span class="ticket-id">{data['ticket_id']}</span><br>
                        Status: <b>{data['status']}</b><br>
                        Priority: <span class="priority-badge priority-{data['priority']}">{data['priority']}</span><br>
                        Type: {data['issue_type']}<br>
                        Created: {data['created_at'][:19]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(data.get("message", "Ticket not found!"))
                else:
                    st.error("Server error while checking ticket status.")
            except requests.exceptions.ConnectionError:
                st.error(f"⚠️ Can't reach the backend at `{API_URL}`.")
            except Exception as e:
                st.error(f"⚠️ {e}")
        else:
            st.warning("Enter a ticket ID first.")

    st.divider()

    st.markdown('<div class="panel-label">📋 YOUR TICKETS</div>', unsafe_allow_html=True)
    if st.session_state.tickets:
        for ticket in st.session_state.tickets:
            priority = ticket.get("priority", "Low")
            st.markdown(f"""
            <div class='ticket-box'>
            🎫 <span class="ticket-id">{ticket['ticket_id']}</span><br>
            Priority: <span class="priority-badge priority-{priority}">{priority}</span><br>
            Status: {ticket.get('status', 'Open')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No tickets created yet.")

    st.divider()

    st.markdown('<div class="panel-label">⚡ QUICK ISSUES</div>', unsafe_allow_html=True)
    quick_issues = [
        "My VPN is not connecting",
        "I forgot my password",
        "My computer is very slow",
        "Printer is not working",
        "Email is not working",
        "Blue screen error"
    ]

    for issue in quick_issues:
        if st.button(issue, use_container_width=True, key=f"quick_{issue}"):
            st.session_state.messages.append({"role": "user", "content": issue})

            with st.spinner("Analyzing your issue..."):
                data, error = send_message(issue)

            if data:
                append_assistant_reply(data)
            else:
                append_error_reply(error)

            st.rerun()

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.tickets = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()