# Multilingual RAG Knowledge Assistant — Backend

A FastAPI backend that lets users upload PDF/TXT/DOCX documents and ask
questions about them in **English, Hindi, Telugu, or Maithili** — with
answers grounded in the documents and cited by page.

Every component below is **free**, so this costs ₹0 to build or run:

| Component | Tool | Cost |
|---|---|---|
| Embeddings | `sentence-transformers` (local, Hugging Face) | Free, runs on your machine |
| Vector database | ChromaDB (local, embedded) | Free, no server needed |
| LLM | Google Gemini API (`gemini-1.5-flash`) | Free tier, no credit card |
| Metadata database | MongoDB (local Docker container, or free Atlas M0) | Free |
| Backend framework | FastAPI | Free, open-source |

---

## 1. Project structure — what each file does

```
app/
├── main.py                        # Creates the FastAPI app, wires up all routes
├── config.py                      # Reads every setting from .env — nothing hard-coded
│
├── api/                            # HTTP layer — thin, just request/response handling
│   ├── documents.py                #   POST /documents/upload, GET /documents, DELETE /documents/{id}
│   ├── chat.py                     #   POST /chat — the main RAG endpoint
│   └── health.py                   #   GET /health — checks all 3 dependencies are up
│
├── rag/                            # The actual RAG pipeline logic
│   ├── document_loader.py          #   Extracts text from PDF / TXT / DOCX
│   ├── chunker.py                  #   Splits text into overlapping chunks (sentence-aware)
│   ├── embeddings.py               #   Loads the multilingual embedding model, encodes text
│   ├── retriever.py                #   Vector search + similarity threshold filtering
│   ├── prompt.py                   #   Builds the "answer only from context" prompt
│   └── generator.py                #   Calls Gemini to generate the final answer
│
├── multilingual/
│   └── language_detection.py       # Detects the language of each question (offline)
│
├── database/
│   ├── chroma.py                   # Vector store wrapper (embeddings + similarity search)
│   └── metadata.py                 # MongoDB wrapper (document names, status, chunk counts)
│
└── models/
    └── schemas.py                  # Every request/response shape (Pydantic)

tests/                               # Pytest unit + API tests (no paid services needed to run them)
data/
├── uploads/                         # Original uploaded files land here
└── chroma/                          # ChromaDB's on-disk vector index
```

**How a question flows through the code**, end to end:

```
POST /chat  →  app/api/chat.py
                 │
                 ├─ 1. multilingual/language_detection.py   → detects "hi"/"te"/"en"/...
                 ├─ 2. rag/retriever.py                      → embeds question, searches Chroma
                 ├─ 3. rag/prompt.py                          → builds grounded prompt
                 ├─ 4. rag/generator.py                       → calls Gemini
                 └─ 5. returns ChatResponse (answer + sources)
```

**How a document upload flows**, end to end:

```
POST /documents/upload  →  app/api/documents.py
                              │
                              ├─ 1. rag/document_loader.py   → extract text per page
                              ├─ 2. multilingual/language_detection.py → detect doc language
                              ├─ 3. rag/chunker.py            → split into overlapping chunks
                              ├─ 4. rag/embeddings.py         → embed every chunk
                              ├─ 5. database/chroma.py        → store vectors + text
                              └─ 6. database/metadata.py      → store filename/status/chunk_count
```

---

## 2. Setup (one-time)

### Step 1 — Get a free Gemini API key
Go to **https://aistudio.google.com/app/apikey**, sign in with any Google
account, and click "Create API key." No credit card needed.

### Step 2 — Clone dependencies
```bash
cd multilingual-rag-backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
The first run will download the embedding model (~470MB) from Hugging
Face automatically — this is a one-time download, cached locally after that.

### Step 3 — Configure environment variables
```bash
cp .env.example .env
```
Open `.env` and paste your Gemini key into `GEMINI_API_KEY`.

### Step 4 — Start MongoDB (pick ONE option)
- **Option A (recommended, fully local, free):**
  ```bash
  docker run -d -p 27017:27017 --name rag-mongo mongo:7
  ```
- **Option B (free Atlas cloud cluster):** create an M0 cluster at
  https://www.mongodb.com/cloud/atlas/register and paste the connection
  string into `MONGODB_URI` in `.env`.

### Step 5 — Run the backend
```bash
uvicorn app.main:app --reload
```
Open **http://localhost:8000/docs** — this is an interactive page
(Swagger UI) where you can try every endpoint directly in the browser.

---

## 3. Running everything with Docker instead (optional)

If you'd rather not install Python locally:
```bash
export GEMINI_API_KEY=your_key_here
docker compose up --build
```
This starts both the backend **and** a local MongoDB container together.

---

## 4. Trying it out

**Upload a document:**
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@/path/to/university_rules.pdf"
```

**Ask a question (any supported language):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the exam eligibility requirements?"}'
```

**List documents:**
```bash
curl http://localhost:8000/documents
```

---

## 5. Running the tests
```bash
pytest -v
```
These tests mock out Gemini/Mongo/Chroma where needed, so they run
without any external service or API key — good for quick iteration and
for a CI pipeline later.

---

## 6. Connecting a React frontend

CORS is already open (`app/main.py`) so a React app on
`http://localhost:3000` (or any origin) can call this API directly.
Point your frontend at `http://localhost:8000` and use the endpoints
documented at `/docs`.

---

## 7. Notes on the free-tier limits you'll actually hit

- **Gemini free tier**: rate-limited (requests/minute), which is fine
  for demoing but will throttle under rapid testing — space out calls
  if you see 429 errors.
- **Local embeddings**: run on CPU by default; a large PDF (100+ pages)
  may take ~10-20 seconds to embed on a laptop. That's expected and
  free — the tradeoff for not paying for an embeddings API.
- **MongoDB Atlas M0**: 512MB storage — more than enough for metadata
  only (vectors live in Chroma, not Mongo).

---

## 8. Extending it later

- Swap `EMBEDDING_MODEL` in `.env` to `intfloat/multilingual-e5-large`
  for stronger Maithili/low-resource-language retrieval (slower).
- Swap the LLM in `app/rag/generator.py` for another provider — it's
  the only file that needs to change.
- Add streaming responses by switching `generate_content` to
  `generate_content(..., stream=True)` in `generator.py` and using
  FastAPI's `StreamingResponse`.
