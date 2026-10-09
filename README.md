# 🎓 AI College Placement Assistant

A full-stack AI-powered college placement management system with role-based access for **Admin, Operator, Trainer, Recruiter, and Student** roles.

---

## ✨ Features

- **Student Portal** — Profile, social links, matched jobs, interview prep, off-campus auto-apply agent
- **Admin / Operator** — Full student CRUD, drive management, override enrollment, analytics
- **Trainer** — Create training sessions, upload study materials (PDF, images, notes)
- **Recruiter** — Post jobs, manage drives, review applications
- **LangGraph Auto-Apply Agent** — Autonomous skill-match scoring + cover letter generation (no LLM key required)
- **Live Off-Campus Jobs** — Verified openings at Google, Microsoft, NVIDIA, Stripe, L&T, etc.
- **LaTeX Resume Generator** — ATS-optimized tailored resume per job
- **Multi-Skill Student Search** — AND/OR filter with skill level awareness

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Backend | FastAPI (Python 3.11+) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Agent | LangGraph + LangChain |
| Auth | JWT Bearer tokens |
| File Storage | Local filesystem (`backend/uploads/`) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/AI-College-Placement-Assistant.git
cd AI-College-Placement-Assistant
```

### 2. Backend setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the server
uvicorn app.main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`  
API docs at: `http://localhost:8000/docs`

### 3. Frontend setup
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 👤 Default Roles

Register users at `/register` with these roles:
- `admin` — Full system access
- `operator` — Student & drive management
- `trainer` — Training sessions & materials upload
- `recruiter` — Job & drive management
- `student` — Apply for jobs, access materials

---

## 📁 Project Structure

```
AI-College-Placement-Assistant/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers
│   │   ├── agent/        # LangGraph auto-apply agent
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── schemas.py    # Pydantic schemas
│   │   └── main.py       # App entry point
│   ├── tests/            # pytest test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/        # React page components
│   │   ├── api.js        # API helper
│   │   └── App.jsx       # Router & layout
│   └── package.json
├── data/                 # Sample CSV data for student import
├── .env.example          # Environment variable template
└── README.md
```

---

## 🧪 Running Tests

```bash
cd backend
.venv\Scripts\activate
pytest tests/ -v
```

---

## 📄 License

MIT License — feel free to use and adapt for your institution.
