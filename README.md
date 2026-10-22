# 🧠 Text-to-SQL Generator

A **FastAPI-powered REST API** that converts plain-English questions into valid SQL `SELECT` queries using a locally hosted LLM (via an OpenAI-compatible endpoint such as Ollama). The system is designed around a **school management database** and features an intelligent multi-stage pipeline with clarification support and SQL validation.

---

## ✨ Features

- 🔍 **Smart Table Selection** — LLM first identifies the relevant tables before generating SQL
- ❓ **Clarification Engine** — Asks the user a follow-up question when the input is ambiguous
- 🛡️ **SQL Validation** — Blocks dangerous keywords (`DROP`, `DELETE`, `INSERT`, etc.) and validates syntax via `sqlglot`
- 🔁 **Retry on Failure** — Automatically retries SQL generation with the validation error as feedback
- 📋 **Session Management** — In-memory sessions track multi-turn clarification conversations
- 📄 **YAML Schema Registry** — Human-readable schema description drives table/column awareness for the LLM
- 📡 **OpenAI-compatible LLM** — Works with any local model served at an OpenAI-compatible endpoint (e.g., Ollama, LM Studio)

---

## 🏗️ Architecture

```
User Question (NL)
        │
        ▼
┌─────────────────────┐
│  POST /api/v1/query │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│              QueryOrchestrator              │
│                                             │
│  1. Table Selection  ──► LLM (prompt)       │
│  2. Clarification Check ──► LLM (prompt)    │
│     └─ If needed ──► return question        │
│  3. SQL Generation ──► LLM (prompt)         │
│  4. SQL Validation ──► sqlglot + blocklist  │
│     └─ If invalid ──► retry with error      │
│  5. Return SQL + Explanation                │
└─────────────────────────────────────────────┘
```

### Multi-Turn Clarification Flow

```
POST /api/v1/query
  └─► status: "needs_clarification"
        └─► returns: session_id + clarification_question
              └─► POST /api/v1/clarify  (session_id + answer)
                    └─► status: "sql_ready"  →  SQL query returned
```

---

## 📁 Project Structure

```
TestToSqlGenerator/
├── app/
│   ├── main.py                   # FastAPI app entry point, lifespan, DI wiring
│   ├── config.py                 # Settings (Pydantic BaseSettings, .env support)
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── router.py         # Combines query & clarify routers
│   │       └── endpoints/
│   │           ├── query.py      # POST /api/v1/query
│   │           └── clarify.py    # POST /api/v1/clarify
│   │
│   ├── core/
│   │   ├── orchestrator.py       # Main pipeline: table selection → clarify → SQL gen → validate
│   │   ├── session.py            # In-memory session store (SessionManager)
│   │   ├── parsers.py            # LLM response parsers (table list, SQL, clarification)
│   │   ├── dependencies.py       # FastAPI dependency injectors
│   │   └── exceptions.py
│   │
│   ├── services/
│   │   ├── llm.py                # LLMService — calls OpenAI-compatible endpoint via httpx
│   │   ├── schema.py             # SchemaService — loads & queries YAML schema registry
│   │   ├── clarification.py      # ClarificationEngine — decides if question needs clarification
│   │   └── validator.py          # SQLValidator — keyword blocklist + sqlglot syntax check
│   │
│   ├── models/
│   │   ├── domain.py             # Pydantic models: QuerrySession, TableMeta, ColumnMeta, ClarificationPair
│   │   ├── request.py            # QueryRequest, ClarifyRequest
│   │   ├── response.py           # QueryResponse, QueryStatus (Enum)
│   │   └── prompt_type.py        # PROMPT_TYPE enum (TABLE_SELECTION, CLARIFICATION, SQL_GENERATION)
│   │
│   └── prompts/
│       ├── table_selection.py    # Prompt: pick relevant tables from the schema
│       ├── clarification.py      # Prompt: decide if clarification is needed
│       └── sql_generation.py     # Prompt: generate the final SQL SELECT query
│
├── database_description.yaml     # Full schema definition (tables, columns, types, FKs, descriptions)
├── migration.py                  # Database migration / seed script
├── table_creation.sql            # Raw SQL DDL for creating the school DB
├── school.db                     # SQLite database file
├── test_question_to_test.txt     # Sample questions for manual testing
├── pyproject.toml                # Project metadata & dependencies (uv/pip)
├── .env                          # Environment variable overrides
└── .python-version               # Python version pin
```

---

## ⚙️ Configuration

Settings are managed via **Pydantic `BaseSettings`** and loaded from the `.env` file.

| Variable                         | Default                                      | Description                                 |
|----------------------------------|----------------------------------------------|---------------------------------------------|
| `APP_NAME`                       | `Text-to-SQL`                                | Application display name                   |
| `DEBUG`                          | `false`                                      | Enable debug mode                           |
| `OLLAMA_URL`                     | `http://127.0.0.1:9931/v1/chat/completions`  | OpenAI-compatible LLM endpoint URL          |
| `MODEL_NAME`                     | `local-model`                                | Model identifier sent in LLM requests       |
| `DB_URL`                         | `sqlite:///./school.db`                      | Database connection URL                     |
| `SCHEMA_PATH`                    | `database_description.yaml`                  | Path to the YAML schema description file    |
| `MAX_RETRIES`                    | `1`                                          | SQL generation retries on validation failure|
| `CLARIFICATION_SIGNAL_THRESHOLD` | `2`                                          | Threshold for triggering clarification      |

**`.env` example:**
```env
OLLAMA_URL=http://localhost:11434/v1/chat/completions
MODEL_NAME=codellama
DB_URL=sqlite:///./school.db
DEBUG=false
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.12+**
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`
- A running **OpenAI-compatible LLM server** (e.g., [Ollama](https://ollama.com/), LM Studio)

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd TestToSqlGenerator

# 2. Install dependencies using uv
uv sync

# or using pip
pip install -e .
```

### Running the Server

```bash
# Using uv + fastapi dev server
uv run fastapi dev app/main.py

# or using uvicorn directly
uvicorn app.main:app --reload
```

The API will be available at **`http://localhost:8000`**.

Interactive Swagger docs: **`http://localhost:8000/docs`**

---

## 📡 API Reference

### `POST /api/v1/query`

Submit a natural language question. Returns either a ready SQL query or a clarification question.

**Request Body:**
```json
{
  "question": "List all female students in Grade 10 Section B"
}
```

**Response — SQL Ready (`status: sql_ready`):**
```json
{
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "sql_ready",
  "sql": "SELECT s.first_name, s.last_name FROM students s JOIN sections sec ON s.section_id = sec.id WHERE s.gender = 'Female' AND sec.name = 'Section B'",
  "explanation": "Returns all female students enrolled in Section B.",
  "tables_used": ["students", "sections"],
  "clarification_question": null,
  "error_message": null
}
```

**Response — Needs Clarification (`status: needs_clarification`):**
```json
{
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "needs_clarification",
  "sql": null,
  "explanation": null,
  "tables_used": [],
  "clarification_question": "Which specific academic year or date range are you referring to?",
  "error_message": null
}
```

---

### `POST /api/v1/clarify`

Answer a clarification question to resume SQL generation from a previous session.

**Request Body:**
```json
{
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "answer": "I mean the current academic year 2026-2027"
}
```

**Response:** Same structure as `/query` with `status: sql_ready`.

> Returns `404` if the `session_id` is not found or has expired.

---

## 🗄️ Database Schema

The system is pre-configured for a **School Management System** SQLite database. The schema is defined in `database_description.yaml` and includes:

| Table             | Description                                                        |
|-------------------|--------------------------------------------------------------------|
| `academic_years`  | Academic session years (e.g., 2026-2027)                          |
| `classes`         | Grade levels (e.g., Grade 10)                                     |
| `sections`        | Class subdivisions (e.g., Section A, Section B)                   |
| `roles`           | System user roles (Super Admin, Teacher, Student, Parent)         |
| `users`           | Central authentication table for all system users                 |
| `staff`           | Employee profiles (teachers, principal, admin staff)              |
| `students`        | Student profiles, linked to sections and parents                  |
| `parents`         | Parent/guardian contact information                               |
| `subjects`        | Academic subject catalog                                          |
| `class_subjects`  | Mapping of subjects to classes with assigned teachers             |
| `attendance`      | Daily student attendance logs (Present, Absent, Late, Excused)    |
| `exams`           | Examination definitions (Mid-Terms, Finals)                       |
| `exam_marks`      | Student scores per subject per exam with letter grades            |
| `fee_structures`  | Standard fee definitions per class and fee type                   |
| `fee_payments`    | Fee payment ledger (Paid, Pending, Overdue)                       |
| `timetables`      | Weekly class schedule (teacher, section, subject, time, room)     |

---

## 🧪 Sample Test Questions

The file `test_question_to_test.txt` contains categorized example questions:

**Vague (likely triggers clarification):**
- *"Who hasn't paid?"*
- *"Are there any bad students?"*
- *"Get me the principal's phone number."*

**Daily Use:**
- *"List all female students in Grade 10 Section B"*
- *"What is the average salary of teachers in the Academics department?"*
- *"Which students were absent yesterday?"*

**Complex Multi-Table:**
- *"List the top 5 students in the 'Mid-Term Examination 2026' based on total marks obtained across all subjects."*
- *"Show me the names of parents whose children have an overdue fee payment for the 'Tuition' fee type."*
- *"Find all teachers who have a class scheduled on Monday morning between 09:00 and 11:00."*
- *"Which class has the highest overall attendance rate this academic year?"*

---

## 🧩 Core Components

### `QueryOrchestrator` (`app/core/orchestrator.py`)
The central pipeline coordinator:
1. Creates an in-memory session for each new query
2. Calls the LLM to identify relevant tables from the schema
3. Invokes `ClarificationEngine` to detect ambiguity — returns early if clarification is needed
4. Generates SQL with retry logic; feeds validation errors back to the LLM for correction
5. Returns a structured `QueryResponse`

### `LLMService` (`app/services/llm.py`)
Wraps async HTTP calls to an OpenAI-compatible `/v1/chat/completions` endpoint using `httpx`. Routes each call to the correct prompt builder based on `PROMPT_TYPE`.

### `SchemaService` (`app/services/schema.py`)
Parses `database_description.yaml` into a registry of `TableMeta` + `ColumnMeta` objects at startup. Provides `get_schema_text()` to format schema context for LLM prompts.

### `ClarificationEngine` (`app/services/clarification.py`)
Uses the LLM to evaluate whether a question is ambiguous given the schema context. Parses the structured `NEEDS_CLARIFICATION: yes/no` + `QUESTION:` response.

### `SQLValidator` (`app/services/validator.py`)
- Blocks DDL/DML keywords: `DROP`, `DELETE`, `INSERT`, `UPDATE`, `CREATE`, `ALTER`, `TRUNCATE`
- Validates SQL syntax using `sqlglot`
- Checks that all referenced tables exist in the schema registry

### `SessionManager` (`app/core/session.py`)
In-memory `dict` store (keyed by UUID `session_id`) tracking full conversation state: original question, selected tables, clarification pairs, generated SQL, and validation errors.

### Prompt Builders (`app/prompts/`)
Three prompt builder functions with strict structured output formats:
- **`build_table_selection_prompt`** → expects `TABLES: table1, table2`
- **`build_clarification_prompt`** → expects `NEEDS_CLARIFICATION: yes/no` + `QUESTION: ...`
- **`build_sql_generation_prompt`** → expects `SQL: ...` + `EXPLANATION: ...`

---

## 🛡️ Security

- Only **`SELECT`** queries are permitted — all write and schema-modifying keywords are blocked at the validator level
- SQL is parsed and validated before being returned — it is **never executed** by the API itself
- Prompt injection is partially mitigated by strict response format parsing

---

## 📦 Dependencies

| Package              | Purpose                                      |
|----------------------|----------------------------------------------|
| `fastapi[standard]`  | Web framework & ASGI server                  |
| `httpx`              | Async HTTP client for LLM calls              |
| `pydantic-settings`  | Settings management with `.env` support      |
| `pyyaml`             | Loading the YAML schema description          |
| `sqlglot`            | SQL parsing and syntax validation            |
| `loguru`             | Structured, coloured logging                 |

**Dev dependencies:**
| Package  | Purpose                         |
|----------|---------------------------------|
| `faker`  | Generating realistic seed data  |

---

## 📝 License

This project is currently unlicensed. Add a `LICENSE` file to define terms of use.
