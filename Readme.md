
# Multilingual RAG Knowledge Assistant

Upload documents and ask questions about them in English, Hindi, Telugu, or
Maithili. Answers are grounded in the uploaded content, cite their source
document and page, and fall back to "I could not find this information in
the uploaded documents" rather than guessing when nothing relevant is found.

Everything runs locally and for free: a local LLM through
[Ollama](https://ollama.com), a local vector store
([ChromaDB](https://www.trychroma.com)), and a local or free-tier MongoDB
instance for metadata and chat history.

---

## Features

- **Document upload** — PDF, TXT, and DOCX, chunked and embedded automatically
- **Multilingual retrieval** — a multilingual sentence-embedding model
  (`paraphrase-multilingual-MiniLM-L12-v2`) so a question in one language can
  match content written in another
- **Grounded answers with hallucination control** — retrieved chunks below a
  similarity threshold are dropped before they ever reach the LLM, so the
  model can't quietly latch onto a weak match and invent an answer
- **Source citations** — every grounded answer lists the document, page, and
  similarity score behind it
- **Chat sessions & history** — conversations are saved and can be reopened
  later
- **Document management** — view, upload, and delete documents from **My
  Documents**
- **Light/dark theme**

---

## Tech stack

| Layer            | Choice                                                          |
| ---------------- | --------------------------------------------------------------- |
| Backend          | FastAPI (Python)                                                |
| LLM              | Ollama, running locally (default model:`qwen2.5:3b-instruct`) |
| Embeddings       | `sentence-transformers` (multilingual MiniLM, CPU-friendly)   |
| Vector store     | ChromaDB (embedded, persists to disk)                           |
| Metadata & chats | MongoDB (local via Docker, or a free Atlas M0 cluster)          |
| Frontend         | React + TypeScript (Vite)                                       |

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) installed locally
- MongoDB — either:
  - `docker compose up mongo` (see `docker-compose.yml`), fully free and local, or
  - a free-forever M0 cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)

---

## Setup

### 1. Pull the local LLM

```bash
ollama pull qwen2.5:3b-instruct
ollama serve   # if it isn't already running
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/` (all values are optional — sensible
defaults are baked into `app/config.py`):

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b-instruct

MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=rag_assistant

CHROMA_PATH=./data/chroma
CHROMA_COLLECTION_NAME=documents

EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

CHUNK_SIZE_WORDS=350
CHUNK_OVERLAP_WORDS=60
TOP_K=3
SIMILARITY_THRESHOLD=0.35

UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE_MB=20
```

Run the API:

```bash
uvicorn app.main:app --reload
```

- API base URL: `http://localhost:8000`
- Interactive docs (Swagger UI): `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

By default the frontend expects the backend at `http://localhost:8000`
(see `API_BASE_URL` in `src/pages/Dashboard/index.tsx`).

---

## Project structure (backend)

```
backend/
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── chat.py          # /chat, /chat/sessions, /chat/sessions/{id}
│   │   ├── documents.py     # /documents, /documents/upload, /documents/{id}
│   │   └── health.py
│   ├── core/
│   │   └── security.py      # auth dependency (get_current_user_id)
│   ├── database/
│   │   ├── chat_sessions.py # MongoDB: chat sessions + messages
│   │   ├── chroma.py        # ChromaDB wrapper (vector store)
│   │   ├── metadata.py      # MongoDB: document metadata
│   │   └── mongodb.py
│   ├── multilingual/
│   │   └── language_detection.py
│   ├── rag/
│   │   ├── chunker.py
│   │   ├── document_loader.py
│   │   ├── embeddings.py    # sentence-transformers wrapper
│   │   ├── generator.py     # Ollama call
│   │   ├── prompt.py
│   │   └── retriever.py     # embed → search → threshold filter
│   ├── config.py
│   └── main.py
└── requirements.txt
```

---

## How retrieval works

1. The question is embedded with the same multilingual model used to embed
   document chunks at upload time.
2. ChromaDB returns the `top_k` nearest chunks by cosine similarity.
3. Any chunk scoring below `SIMILARITY_THRESHOLD` is dropped.
4. If nothing survives the threshold, the API returns the "not found" message
   in the detected question language — **no LLM call is made**, so there's
   nothing for the model to hallucinate from.
5. Otherwise the surviving chunks are stuffed into a prompt, the local LLM
   generates an answer, and the response includes the source chunks with
   their similarity scores.

**Tuning the threshold:** `0.35` is a reasonable starting point for cosine
similarity with the MiniLM model, but the right value depends on your
documents and how specific your questions tend to be. Vague questions
("what is this document about?") naturally score lower than specific ones,
even against genuinely relevant chunks. If you're getting too many "not
found" responses, lower it in small steps (e.g. `0.30`, `0.25`) and re-test;
if irrelevant chunks are leaking through, raise it.

---

## Troubleshooting

**"I could not find this information" on every question**
Check, in order:

1. Did the document actually finish indexing? (`GET /documents` should show
   `status: "ready"`.)
2. Are there chunks in Chroma at all? From a Python shell in `backend/`:
   ```python
   from app.database.chroma import get_collection
   print(get_collection().count())
   ```
3. Is the similarity threshold too high for your documents/questions? See
   "How retrieval works" above.

**`GET /chat/sessions` returns 404**
Make sure `app/api/chat.py` includes the `/chat/sessions` (list),
`/chat/sessions/{session_id}` (detail), and `DELETE /chat/sessions/{session_id}`
routes — these call into functions already implemented in
`app/database/chat_sessions.py`.

**Document size shows as 0 B**
`file_size` must be passed explicitly into `metadata.create_document(...)`
from the upload endpoint (`len(contents)` is already computed there for the
size-limit check) — it isn't inferred automatically. Documents uploaded
before this was wired up will show `0 B` until re-uploaded.

**Dark mode: language dropdown list still shows a white popup**
This is a native `<select>` limitation — the open dropdown list is rendered
by the OS/browser (notably GTK on Linux Chrome), which ignores page CSS and
`color-scheme`. The fix is a custom-built dropdown component
(`CustomSelect.tsx`) instead of a native `<select>`, so the open/closed
states are fully styled by your own CSS.

---

## Supported languages

| Code | Language |
| ---- | -------- |
| en   | English  |
| hi   | Hindi    |
| te   | Telugu   |
| mai  | Maithili |

Maithili isn't explicitly in the embedding model's training languages, but
because it shares subword vocabulary and script with Hindi, retrieval
quality is usually still reasonable. For stronger Maithili support, swap
`EMBEDDING_MODEL` to `intfloat/multilingual-e5-large` (larger, slower, and
note it requires `"query: "` / `"passage: "` prefixes on inputs — the
current `embeddings.py` wrapper does not add these automatically).

---

## License

Add your license of choice here.
