# 🖥️ TechSupport AI

> **An AI-powered IT Helpdesk Agent that automates issue triage, knowledge retrieval, troubleshooting, ticket creation, and escalation.**

Built for the **Support Chat Bot Track**, TechSupport AI reduces manual support workload by intelligently diagnosing user issues, recommending solutions, and creating support tickets automatically whenever required.

---

## 🌟 Features

✅ Intelligent Issue Classification

- Detects issue category:
  - 🌐 Network
  - 💻 Hardware
  - ⚙️ Software
  - 🔐 Access
  - 📧 Communication

- Automatically assigns priority:
  - 🔴 Critical
  - 🟠 High
  - 🟡 Medium
  - 🟢 Low

---

✅ Semantic Knowledge Search

Uses **FAISS + Sentence Transformers** to search an IT knowledge base using semantic similarity rather than simple keyword matching.

Even if users describe problems differently, the system retrieves the most relevant solution.

---

✅ Guided Troubleshooting

Provides clear, step-by-step troubleshooting instructions tailored to the detected issue.

---

✅ Automatic Ticket Creation

Support tickets are generated automatically when:

- Priority is High
- Priority is Critical
- User indicates the issue remains unresolved

No manual intervention required.

---

✅ Smart Escalation

Critical and High priority issues are immediately escalated with response expectations.

---

✅ Fault Tolerant Design

If the LLM becomes unavailable due to:

- API failure
- Invalid key
- Network issue
- Rate limit

the backend still returns:

- Knowledge Base result
- Issue classification
- Troubleshooting guide
- Ticket creation

The chatbot never simply crashes.

---

✅ Admin Dashboard

Support staff can monitor:

- Ticket statistics
- Priority distribution
- Issue type distribution
- Ticket status
- CSV Export

---

# 🏗 System Architecture

```
                 User
                   │
                   ▼
         Streamlit Chat Interface
                   │
                   ▼
           FastAPI Backend API
                   │
     ┌─────────────┼──────────────┐
     ▼             ▼              ▼
Issue        Knowledge Base     Ticket
Classifier      Retrieval      Management
     │             │              │
     └──────┬──────┴───────┬──────┘
            ▼              ▼
      Escalation Logic   Groq LLM
              │
              ▼
        Final Response
```

---

# ⚙ Workflow

```
User Message
      │
      ▼
Issue Classification
      │
      ▼
Semantic KB Search
      │
      ▼
Troubleshooting Guide
      │
      ▼
Ticket Creation (if needed)
      │
      ▼
Escalation (Critical / High)
      │
      ▼
Groq LLM
      │
      ▼
Final Response
```

---

# 📂 Project Structure

```
TechSupportAI/

│
├── app/
│   ├── main.py
│   ├── agent.py
│   │
│   ├── database/
│   │      └── models.py
│   │
│   ├── rag/
│   │      ├── retriever.py
│   │      └── knowledge_base/
│   │              └── it_faqs.txt
│   │
│   └── tools/
│          ├── ticket_tool.py
│          ├── escalate_tool.py
│          └── search_tool.py
│
├── frontend/
│      ├── streamlit_app.py
│      └── admin_dashboard.py
│
├── requirements.txt
├── .env
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

- Python 3.10+
- Groq API Key

---

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/TechSupportAI.git

cd TechSupportAI
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Configure Environment

Create a `.env` file

```env
GROQ_API_KEY=your_api_key
```

---

## 4. Start Backend

```bash
uvicorn app.main:app --reload
```

Runs at

```
http://localhost:8000
```

---

## 5. Launch Chat Interface

```bash
streamlit run frontend/streamlit_app.py
```

Runs at

```
http://localhost:8501
```

---

## 6. Launch Admin Dashboard

```bash
streamlit run frontend/admin_dashboard.py --server.port 8502
```

Runs at

```
http://localhost:8502
```

---

# 📡 API Endpoints

## POST `/chat`

Send a support request.

### Request

```json
{
  "session_id":"123",
  "message":"Internet is not working",
  "user_name":"Alice"
}
```

### Response

```json
{
  "success": true,
  "response": "...",
  "issue_type": "Network",
  "priority": "High",
  "ticket_info": {
      "ticket_id":"TK-20260716-4821",
      "status":"Open"
  },
  "kb_found": true,
  "escalation_msg":"..."
}
```

---

## POST `/ticket/status`

Returns ticket status.

---

## GET `/health`

Backend health check.

---

# 🧠 Tech Stack

| Layer | Technology |
|---------|------------|
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite + SQLAlchemy |
| Vector Search | FAISS |
| Embeddings | Sentence Transformers |
| LLM | Groq (gpt-oss-20b) |
| Visualization | Plotly |

---

# 🎯 Why This Design?

Instead of relying entirely on an LLM, TechSupport AI separates deterministic business logic from natural language generation.

The system first:

- Classifies issues
- Determines priority
- Searches the knowledge base
- Creates tickets
- Handles escalations

Only after these reliable steps does the LLM generate a user-friendly response.

This architecture makes the system:

- More reliable
- Easier to test
- Resistant to hallucinations
- Functional even when the LLM is unavailable

---

# 📊 Dashboard

The Admin Dashboard provides:

- Ticket Management
- Live Analytics
- Issue Distribution
- Priority Breakdown
- Ticket Status Tracking
- CSV Export

---

# 📸 Screenshots

Add screenshots here.

```
assets/

chat.png

dashboard.png

ticket.png
```

---

# 🔮 Future Improvements

- Email notifications
- Slack/MS Teams integration
- Authentication & Role-Based Access
- Multi-language support
- Voice-enabled support assistant
- PDF report generation
- Real-time monitoring dashboard
- Docker deployment
- Kubernetes support

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository

2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

# 📜 License

Licensed under the MIT License.

---

## ⭐ If you found this project useful, please consider giving it a Star!

It helps others discover the project and motivates future improvements.