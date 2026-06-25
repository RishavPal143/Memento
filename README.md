# Memento - AI-Powered Personal Internet Memory

Memento is an AI-powered "Internet Memory" application that automatically captures the webpages you visit, extracts and cleans their content, generates vector embeddings, and stores them in a local PostgreSQL database using pgvector. It features semantic search, an interactive AI chat agent that cites its sources, an automatic webpage ingestion processor, and a background intelligence layer that learns user interests.

---

## Project Structure

```
Memento/
├── backend/
│   ├── main.py                 # FastAPI application entry point and modular router mounts
│   ├── database.py             # SQLAlchemy configuration and database helpers
│   ├── models.py               # Database schemas (SQLAlchemy models)
│   ├── schemas.py              # API validation and serialization models (Pydantic schemas)
│   ├── crud.py                 # Ingestion pipeline, metadata enhancement, and CRUD database logic
│   ├── embeddings.py           # Text cleaning, page truncation, and embedding generation
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm.py              # LLM client logic (OpenAI / Gemini / Mock)
│   │   ├── vector_search.py    # Vector similarity pgvector database queries
│   │   └── memory_processor.py # Background intelligence loop (periodic user profile analyzer)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── memory.py           # Ingestion and basic CRUD routes (/memory)
│   │   ├── search.py           # Semantic Search API (/search)
│   │   ├── chat.py             # AI Chat Memory Agent (/chat)
│   │   └── insights.py         # Intelligence profiling endpoint (/insights)
│   ├── requirements.txt        # Backend python dependencies
│   ├── .env                    # Active local environment variables
│   └── .env.example            # Environment variables template
├── extension/
│   ├── manifest.json           # Manifest V3 configuration with storage permission
│   ├── popup.html              # Settings control and manual capture UI
│   ├── popup.js                # Controls toggles (Auto-save, Save Only Important) and triggers manual saves
│   ├── content.js              # Extracts clean page text and handles tab save triggers
│   └── background.js           # Ephemeral service worker checking scores and handling api fetch requests
└── README.md                   # Setup and execution guide (this file)
```

---

## Part 1: PostgreSQL & pgvector Setup

### 1. Install pgvector Extension
`pgvector` must be installed on your PostgreSQL server.

#### macOS (Homebrew PostgreSQL)
If using Homebrew PostgreSQL:
```bash
brew install pgvector
```

#### Manual Compilation (EnterpriseDB / System PostgreSQL)
If using the EDB installer (e.g. at `/Library/PostgreSQL/18`):
1. Clone the repository:
   ```bash
   git clone --branch v0.8.3 https://github.com/pgvector/pgvector.git
   cd pgvector
   ```
2. Compile and install (requires Xcode Command Line Tools):
   ```bash
   make PG_CONFIG=/Library/PostgreSQL/18/bin/pg_config CPPFLAGS="-isysroot $(xcrun --sdk macosx --show-sdk-path)" LDFLAGS="-isysroot $(xcrun --sdk macosx --show-sdk-path)"
   sudo make install PG_CONFIG=/Library/PostgreSQL/18/bin/pg_config CPPFLAGS="-isysroot $(xcrun --sdk macosx --show-sdk-path)" LDFLAGS="-isysroot $(xcrun --sdk macosx --show-sdk-path)"
   ```

### 2. Enable pgvector
Connect to your database:
```bash
psql -U postgres -d postgres
```
Inside the interactive prompt, run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Part 2: Backend Setup

### 1. Configure Environment Variables
Create a `.env` file in the `backend/` directory by copying `.env.example`:
```bash
cp backend/.env.example backend/.env
```
Update the settings in `backend/.env` to configure your database connection and AI providers:
*   `EMBEDDING_PROVIDER`: `"openai"`, `"gemini"`, or `"mock"` (for offline testing without keys).
*   `LLM_PROVIDER`: `"openai"`, `"gemini"`, or `"mock"`.
*   Provide `OPENAI_API_KEY` or `GEMINI_API_KEY` depending on the provider chosen.

### 2. Install Dependencies & Run Server
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Activate your virtual environment:
   ```bash
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   On startup, database connections are established, the `vector` extension is verified, and the `insights` table as well as the new metadata columns (`summary`, `tags`, `importance_score`) are automatically created/migrated.

---

## Part 3: Chrome Extension Installation

1. Open **Google Chrome** and navigate to `chrome://extensions/`.
2. Enable **Developer mode** using the toggle switch in the top-right corner.
3. Click the **Load unpacked** button in the top-left corner.
4. Select the `extension/` folder located in the project workspace.
5. Click on the extension icon in your toolbar to configure settings:
   *   **Auto-save Pages**: Toggle whether pages you browse should be automatically captured on load.
   *   **Save Only Important**: Toggle whether to discard pages with low AI importance scores (< 60). Discarded pages show a yellow `"Low"` badge.
   *   **Save Current Page**: Force-save the current page manually (bypasses the importance filter).

---

## Part 4: API Endpoint Specifications

### Ingestion & Basic CRUD (`routes/memory.py`)
*   `POST /memory`: Ingests page data, cleans + truncates, runs the AI metadata enhancement analyzer (extracting summary, tags, importance score), generates a 1536-dimensional vector embedding, and commits both to the database in a single atomic transaction.
*   `GET /memory`: Retrieves all saved memories.
*   `GET /memory/{id}`: Retrieves a specific memory.
*   `DELETE /memory/{id}`: Deletes a memory and cascadingly removes its vector embedding.

### Semantic Search (`routes/search.py`)
*   `GET /search?q={query}&limit={5-20}`: Converts the query into an embedding, performs a pgvector cosine similarity search, generates query-centered snippets matching search terms, and returns search result objects containing `title`, `url`, `snippet`, and `similarity_score`.

### AI Chat Memory Agent (`routes/chat.py`)
*   `POST /chat`: Receives `{ "query": "your question" }`, retrieves the top 5 relevant memories, feeds them as context to the LLM, and returns a natural language response alongside resource citations/sources.

### Intelligence Profiler (`routes/insights.py`)
*   `GET /insights`: Returns the latest user profile summary and active research interests.
*   *Note: A background loop runs periodically (configurable via `INTELLIGENCE_INTERVAL_SECONDS`) to query all memories, detect user themes and topics, and save them to the database.*
