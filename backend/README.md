# CodeGenerator Backend

FastAPI backend for the CodeGenerator app. Provides SSE streaming, session history,
and sandboxed code execution.

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)

## Setup

```sh
uv venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
uv sync
mkdir -p db
python -m app.db.init_db
```

## Run

```sh
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Notes

- Database file lives at `backend/db/codegen.db`.
- Sessions are ordered by `updated_at` and messages persist to history.
