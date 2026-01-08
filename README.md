# AI-Powered Python Code Generator

A full-stack application with a chat interface that generates, executes, and validates Python code using LLM agents (OpenAI GPT/Anthropic Claude).

## Features

- 🤖 **LLM-Powered Code Generation** - Uses OpenAI GPT or Anthropic Claude
- 🔄 **Iterative Error Fixing** - Automatically fixes errors until code works (max 5 iterations)
- ✅ **Test Validation** - Runs user-provided tests first, minimal smoke test by default
- 🔒 **Subprocess Sandbox** - OS-level isolation for secure code execution (Directive 06)
- 📊 **Per-Node Token Tracking** - Detailed observability with LangSmith integration
- 🎯 **Streaming UI** - Real-time updates showing agent progress
- 🗂️ **Session History** - Resume past chats, ordered by latest activity
- 🚫 **Anti-Hardcoding Detection** - Prevents LLM from hardcoding solutions

## Architecture

**Backend:**
- Python 3.11+ with FastAPI
- LangGraph for agent orchestration
- SQLite database (file at `backend/db/codegen.db`, code at `backend/app/db/`)
- Subprocess-based code execution (PRIMARY isolation)
- Structured JSON output enforcement (NO markdown cleanup)

**Frontend:**
- React 18 + TypeScript + Vite
- TailwindCSS for styling
- Zustand for state management
- POST + fetch() streaming (NOT EventSource)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) (Python package manager)

### 1. Clone and Setup Environment

```bash
git clone <your-repo>
cd CodeGenerator
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Backend Setup (Directive 11 - uv sync ONLY)

```bash
cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync  # NOT uv pip install -r requirements.txt
mkdir -p db
python -m app.db.init_db
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup (separate terminal)

```bash
cd frontend
npm install
npm run dev  # Starts on port 5173 (Vite default)
```

### 4. Access

- **Frontend**: http://localhost:5173 (Directive 12)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Project Structure

```
CodeGenerator/
├── backend/
│   ├── db/                      # Database FILE location (Directive 19)
│   │   └── codegen.db          # SQLite database file
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── core/               # Config, security
│   │   ├── api/routes/         # API endpoints
│   │   ├── agents/             # LangGraph workflow
│   │   │   └── nodes/          # Agent nodes (planning, code_gen, etc.)
│   │   ├── services/
│   │   │   ├── llm/            # OpenAI/Anthropic services
│   │   │   ├── execution/      # Subprocess sandbox
│   │   │   └── observability/  # Token tracking
│   │   ├── models/             # Pydantic schemas, SQLAlchemy models
│   │   └── db/                 # Database CODE location (Directive 19)
│   └── pyproject.toml          # uv dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── hooks/              # useFetchStream.ts (Directive 02)
│   │   ├── services/           # API client, SSE parser
│   │   └── store/              # Zustand state
│   └── package.json
│
└── claude-tracker/             # Planning documents (20 directives)
    ├── IMPLEMENTATION_READY.md # Source of truth (Directive 15)
    ├── development_plan.md     # Full 8-phase plan
    ├── critical_updates.md     # All 20 directives explained
    └── chat_tracker.md         # Conversation history
```

## Key Architectural Decisions (All 20 Directives Applied)

1. **POST + fetch() Streaming** (Directive 02) 
2. **Structured JSON Output** (Directive 03) 
3. **User Tests First-Class** (Directive 04) - Inference is optional fallback
4. **Anti-Hardcoding Protection** (Directive 05) - Detect patterns + randomized tests
5. **Subprocess Sandbox** (Directive 06) - PRIMARY isolation (OS-level)
6. **Cancellation Support** (Directive 07) - Track PIDs, SIGTERM/SIGKILL
7. **Port 5173** (Directive 08, 20) - Vite default, no alternatives
8. **Per-Node Token Tracking** (Directive 09) - Every LLM call logged
9. **uv sync ONLY** (Directive 11) - uv only
10. **optional_test_inference.py** (Directive 17) - File name matches concept
11. **DB Folder Convention** (Directive 19) - File at backend/db/, code at backend/app/db/


## License

MIT
