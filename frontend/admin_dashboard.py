import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
from app.database.models import SessionLocal, Ticket
from app.tools.ticket_tool import update_ticket_status

st.set_page_config(
    page_title="TechSupport AI — Admin",
    page_icon="📊",
    layout="wide"
)

# ──────────────────────────────────────────────────────────────────────────
# Same "Command Center" theme as the chat app, so the admin dashboard reads
# as one product rather than two mismatched screens.
# ──────────────────────────────────────────────────────────────────────────
PALETTE = {
    "Critical": "#F87171",
    "High": "#FB923C",
    "Medium": "#FBBF24",
    "Low": "#34D399",
    "Open": "#F87171",
    "In Progress": "#FBBF24",
    "Resolved": "#34D399",
}

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
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--text); }
    .stApp { background: var(--bg); }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }

    .console-header {
        background: linear-gradient(180deg, #0F1729 0%, #0A0E17 100%);
        border: 1px solid var(--panel-border);
        border-radius: 12px;
        padding: 22px 28px;
        margin-bottom: 22px;
    }
    .console-header h1 { margin: 0; font-size: 1.65rem; color: #fff; }
    .console-header p { margin: 4px 0 0 0; color: var(--text-dim); font-size: 0.88rem; }

    .panel-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        color: var(--text-dim);
        text-transform: uppercase;
        margin: 18px 0 10px 0;
        border-bottom: 1px solid var(--panel-border);
        padding-bottom: 8px;
    }

    div[data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--panel-border);
        border-radius: 10px;
        padding: 14px 16px;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #fff !important;
    }
    div[data-testid="stMetricLabel"] { color: var(--text-dim) !important; }

    .ticket-row {
        background: var(--panel);
        border: 1px solid var(--panel-border);
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        color: var(--text);
    }

    .stButton > button {
        background: var(--panel) !important;
        color: var(--text) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 8px !important;
    }
    .stButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="console-header">
    <h1>📊 TechSupport AI — Admin</h1>
    <p>Real-time IT helpdesk analytics & ticket management</p>
</div>
""", unsafe_allow_html=True)


def get_all_tickets():
    """Fetch all tickets from database"""
    db = SessionLocal()
    try:
        tickets = db.query(Ticket).all()
        return [
            {
                "ticket_id": t.ticket_id,
                "user_name": t.user_name,
                "issue_type": t.issue_type,
                "priority": t.priority,
                "status": t.status,
                "description": t.description,
                "created_at": t.created_at,
                "updated_at": t.updated_at
            }
            for t in tickets
        ]
    finally:
        db.close()


def update_ticket(ticket_id: str, new_status: str):
    """Update ticket status"""
    return update_ticket_status(ticket_id, new_status)


tickets = get_all_tickets()

col_refresh, col_empty = st.columns([1, 5])
with col_refresh:
    if st.button("🔄 Refresh Data"):
        st.rerun()

if not tickets:
    st.info("📭 No tickets yet! Start chatting in the main app to create tickets.")
else:
    df = pd.DataFrame(tickets)

    # ── TOP METRICS ──
    st.markdown('<div class="panel-label">📈 OVERVIEW</div>', unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns(5)

    total = len(df)
    open_t = len(df[df["status"] == "Open"])
    in_progress = len(df[df["status"] == "In Progress"])
    resolved = len(df[df["status"] == "Resolved"])
    critical = len(df[df["priority"] == "Critical"])

    with m1: st.metric("🎫 Total Tickets", total)
    with m2: st.metric("🔴 Open", open_t)
    with m3: st.metric("🟡 In Progress", in_progress)
    with m4: st.metric("🟢 Resolved", resolved)
    with m5: st.metric("🚨 Critical", critical)

    # ── CHARTS ──
    st.markdown('<div class="panel-label">📊 ANALYTICS</div>', unsafe_allow_html=True)
    chart1, chart2, chart3 = st.columns(3)

    def style_fig(fig):
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E5E7EB",
            font_family="Inter",
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=50, b=10, l=10, r=10),
        )
        return fig

    with chart1:
        priority_counts = df["priority"].value_counts().reset_index()
        priority_counts.columns = ["Priority", "Count"]
        fig1 = px.pie(
            priority_counts, values="Count", names="Priority",
            title="Priority Distribution", color="Priority",
            color_discrete_map=PALETTE, hole=0.55
        )
        st.plotly_chart(style_fig(fig1), use_container_width=True)

    with chart2:
        type_counts = df["issue_type"].value_counts().reset_index()
        type_counts.columns = ["Issue Type", "Count"]
        fig2 = px.bar(
            type_counts, x="Issue Type", y="Count",
            title="Issue Type Breakdown", color_discrete_sequence=["#22D3EE"]
        )
        fig2.update_traces(marker_line_width=0)
        fig2.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig2), use_container_width=True)

    with chart3:
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig3 = px.pie(
            status_counts, values="Count", names="Status",
            title="Status Overview", color="Status",
            color_discrete_map=PALETTE, hole=0.55
        )
        st.plotly_chart(style_fig(fig3), use_container_width=True)

    # ── FILTERS ──
    st.markdown('<div class="panel-label">🎫 TICKET MANAGEMENT</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        filter_status = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Resolved"])
    with f2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "Critical", "High", "Medium", "Low"])
    with f3:
        filter_type = st.selectbox("Filter by Type", ["All"] + list(df["issue_type"].unique()))

    filtered_df = df.copy()
    if filter_status != "All":
        filtered_df = filtered_df[filtered_df["status"] == filter_status]
    if filter_priority != "All":
        filtered_df = filtered_df[filtered_df["priority"] == filter_priority]
    if filter_type != "All":
        filtered_df = filtered_df[filtered_df["issue_type"] == filter_type]

    st.markdown(f"Showing **{len(filtered_df)}** of **{total}** tickets")

    # ── TICKET LIST ──
    for _, ticket in filtered_df.iterrows():
        priority_emoji = {"Critical": "🚨", "High": "⚠️", "Medium": "🔔", "Low": "✅"}.get(ticket["priority"], "🔔")
        status_emoji = {"Open": "🔴", "In Progress": "🟡", "Resolved": "🟢"}.get(ticket["status"], "🔴")

        with st.expander(
            f"{priority_emoji} {ticket['ticket_id']} | {ticket['issue_type']} | "
            f"{status_emoji} {ticket['status']} | {ticket['priority']} Priority"
        ):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**📝 Description:** {ticket['description']}")
                st.markdown(f"**🕐 Created:** {str(ticket['created_at'])[:19]}")
                st.markdown(f"**🔄 Updated:** {str(ticket['updated_at'])[:19]}")
            with c2:
                new_status = st.selectbox(
                    "Update Status",
                    ["Open", "In Progress", "Resolved"],
                    index=["Open", "In Progress", "Resolved"].index(ticket["status"]),
                    key=f"status_{ticket['ticket_id']}"
                )
                if st.button("💾 Update", key=f"btn_{ticket['ticket_id']}"):
                    result = update_ticket(ticket["ticket_id"], new_status)
                    if result["success"]:
                        st.success(f"Updated to {new_status}!")
                        st.rerun()
                    else:
                        st.error("Update failed!")

    # ── EXPORT ──
    st.markdown('<div class="panel-label">📥 EXPORT DATA</div>', unsafe_allow_html=True)
    csv = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download All Tickets (CSV)",
        data=csv,
        file_name="techsupport_tickets.csv",
        mime="text/csv"
    )