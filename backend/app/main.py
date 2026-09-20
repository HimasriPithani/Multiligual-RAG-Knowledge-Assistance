"""
Application entrypoint.

Run locally with:
    uvicorn app.main:app --reload

Then open http://localhost:8000/docs for interactive API documentation
(Swagger UI, generated automatically by FastAPI).
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, documents, health
from app.api.auth import router as auth_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Multilingual RAG Knowledge Assistant",
    description=(
        "Upload documents and ask questions about them in English, Hindi, "
        "Telugu, or Maithili. Answers are grounded in the uploaded content "
        "and cite their source document and page."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend's actual domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(auth_router)



@app.get("/")
async def root():
    return {
        "message": "Multilingual RAG Knowledge Assistant API",
        "docs": "/docs",
    }
