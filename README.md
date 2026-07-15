# 🖥️ TechSupport AI

> **An AI-powered IT Helpdesk Agent** that automates issue triage, semantic knowledge retrieval, troubleshooting, ticket creation, and escalation.

Built for the **Support Chat Bot Track**.

---

## ✨ Features

- 🌐 Detects issue type (Network, Hardware, Software, Access, Communication)
- 🚦 Assigns priority (Critical, High, Medium, Low)
- 🔍 Semantic search using **FAISS + Sentence Transformers**
- 🛠️ Step-by-step troubleshooting guides
- 🎫 Automatic ticket creation for High/Critical or unresolved issues
- 🚨 Automatic escalation for urgent tickets
- 🤖 Groq LLM generates clear responses
- 🛡️ Graceful fallback if the LLM is unavailable
- 📊 Admin dashboard with analytics and ticket management

---

## 🏗 Architecture

```text
User
 │
 ▼
Streamlit UI
 │
 ▼
FastAPI Backend
 │
 ├── Issue Classification
 ├── KB Semantic Search
 ├── Troubleshooting
 ├── Ticket Creation
 ├── Escalation
 └── Groq LLM
 │
 ▼
Response
```

---

## 📂 Project Structure

```text
TechSupportAI/
│
├── app/
│   ├── main.py
│   ├── agent.py
│   ├── database/
│   ├── rag/
│   └── tools/
│
├── frontend/
│   ├── streamlit_app.py
│   └── admin_dashboard.py
│
├── requirements.txt
├── .env
└── README.md
```

---

# 🚀 Getting Started

## Requirements

- Python 3.10+
- Groq API Key

## Clone

```bash
git clone https://github.com/yourusername/TechSupportAI.git
cd TechSupportAI
```

## Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key
```

## Start Backend

```bash
uvicorn app.main:app --reload
```

Runs on:

```
http://localhost:8000
```

## Start Chat UI

```bash
streamlit run frontend/streamlit_app.py
```

Runs on:

```
http://localhost:8501
```

## Start Admin Dashboard

```bash
streamlit run frontend/admin_dashboard.py --server.port 8502
```

Runs on:

```
http://localhost:8502
```

> Run all commands from the project root.

---

# 📡 API

### POST `/chat`

```json
{
  "session_id": "123",
  "message": "Internet is not working",
  "user_name": "Alice"
}
```

Response

```json
{
  "success": true,
  "response": "...",
  "issue_type": "Network",
  "priority": "High",
  "ticket_info": {
    "ticket_id": "TK-20260716-4821",
    "status": "Open"
  },
  "kb_found": true,
  "escalation_msg": "..."
}
```

### POST `/ticket/status`

Returns ticket status.

### GET `/health`

Health check endpoint.

---

# 🧠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite + SQLAlchemy |
| Vector Search | FAISS |
| Embeddings | Sentence Transformers |
| LLM | Groq (gpt-oss-20b) |
| Charts | Plotly |

---

# 🎯 Design Highlights

- Deterministic issue classification and ticket creation
- Semantic search for FAQ retrieval
- LLM used only for response generation
- Automatic escalation for urgent issues
- Graceful degradation when the LLM is unavailable
- Shared SQLite database for chat and admin dashboard

---

# 📸 Screenshots

```
assets/
├── chat.png
├── dashboard.png
└── ticket.png
```

---

# 📜 License

Licensed under the **MIT License**.

---

⭐ If you found this project useful, consider giving it a **Star**!