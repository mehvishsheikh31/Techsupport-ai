import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.database.models import SessionLocal
from app.database.models import Ticket
st.set_page_config(
    page_title="TechSupport AI — Admin",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
        border: 1px solid #2196F3;
    }
    .metric-card {
        background: #1e3a5f;
        border: 1px solid #2196F3;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        color: white;
    }
    .ticket-row {
        background: #1a1a2e;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 TechSupport AI — Admin Dashboard</h1>
    <p>Real-time IT Helpdesk Analytics & Ticket Management</p>
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
    from app.tools.ticket_tool import update_ticket_status
    return update_ticket_status(ticket_id, new_status)

# Fetch data
tickets = get_all_tickets()

# Refresh button
col_refresh, col_empty = st.columns([1, 5])
with col_refresh:
    if st.button("🔄 Refresh Data"):
        st.rerun()

st.divider()

if not tickets:
    st.info("📭 No tickets yet! Start chatting to create tickets.")
else:
    df = pd.DataFrame(tickets)

    # ── TOP METRICS ──
    st.subheader("📈 Overview")
    m1, m2, m3, m4, m5 = st.columns(5)

    total = len(df)
    open_t = len(df[df["status"] == "Open"])
    in_progress = len(df[df["status"] == "In Progress"])
    resolved = len(df[df["status"] == "Resolved"])
    critical = len(df[df["priority"] == "Critical"])

    with m1:
        st.metric("🎫 Total Tickets", total)
    with m2:
        st.metric("🔴 Open", open_t)
    with m3:
        st.metric("🟡 In Progress", in_progress)
    with m4:
        st.metric("🟢 Resolved", resolved)
    with m5:
        st.metric("🚨 Critical", critical)

    st.divider()

    # ── CHARTS ──
    st.subheader("📊 Analytics")
    chart1, chart2, chart3 = st.columns(3)

    # Priority Distribution
    with chart1:
        priority_counts = df["priority"].value_counts().reset_index()
        priority_counts.columns = ["Priority", "Count"]
        colors = {
            "Critical": "#ff4444",
            "High": "#ff8800",
            "Medium": "#ffcc00",
            "Low": "#44ff44"
        }
        fig1 = px.pie(
            priority_counts,
            values="Count",
            names="Priority",
            title="Priority Distribution",
            color="Priority",
            color_discrete_map=colors,
            hole=0.4
        )
        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )
        st.plotly_chart(fig1, use_container_width=True)

    # Issue Type Distribution
    with chart2:
        type_counts = df["issue_type"].value_counts().reset_index()
        type_counts.columns = ["Issue Type", "Count"]
        fig2 = px.bar(
            type_counts,
            x="Issue Type",
            y="Count",
            title="Issue Type Breakdown",
            color="Count",
            color_continuous_scale="Blues"
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Status Distribution
    with chart3:
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        status_colors = {
            "Open": "#ff4444",
            "In Progress": "#ffcc00",
            "Resolved": "#44ff44"
        }
        fig3 = px.pie(
            status_counts,
            values="Count",
            names="Status",
            title="Status Overview",
            color="Status",
            color_discrete_map=status_colors,
            hole=0.4
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── FILTERS ──
    st.subheader("🎫 Ticket Management")

    f1, f2, f3 = st.columns(3)
    with f1:
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "Open", "In Progress", "Resolved"]
        )
    with f2:
        filter_priority = st.selectbox(
            "Filter by Priority",
            ["All", "Critical", "High", "Medium", "Low"]
        )
    with f3:
        filter_type = st.selectbox(
            "Filter by Type",
            ["All"] + list(df["issue_type"].unique())
        )

    # Apply filters
    filtered_df = df.copy()
    if filter_status != "All":
        filtered_df = filtered_df[filtered_df["status"] == filter_status]
    if filter_priority != "All":
        filtered_df = filtered_df[filtered_df["priority"] == filter_priority]
    if filter_type != "All":
        filtered_df = filtered_df[filtered_df["issue_type"] == filter_type]

    st.markdown(f"Showing **{len(filtered_df)}** tickets")
    st.divider()

    # ── TICKET LIST ──
    for _, ticket in filtered_df.iterrows():
        priority_emoji = {
            "Critical": "🚨",
            "High": "⚠️",
            "Medium": "🔔",
            "Low": "✅"
        }.get(ticket["priority"], "🔔")

        status_emoji = {
            "Open": "🔴",
            "In Progress": "🟡",
            "Resolved": "🟢"
        }.get(ticket["status"], "🔴")

        with st.expander(
            f"{priority_emoji} {ticket['ticket_id']} | "
            f"{ticket['issue_type']} | "
            f"{status_emoji} {ticket['status']} | "
            f"{ticket['priority']} Priority"
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

    st.divider()

    # ── EXPORT ──
    st.subheader("📥 Export Data")
    csv = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download All Tickets (CSV)",
        data=csv,
        file_name="techsupport_tickets.csv",
        mime="text/csv"
    )