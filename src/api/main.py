"""FastAPI backend for the RAG system."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from src.orchestration.graph import RAGPipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI backend and initializing RAG pipeline...")
    app.state.pipeline = RAGPipeline()
    logger.info("RAG pipeline initialized successfully")
    yield


app = FastAPI(
    title="RAG System API",
    description="FastAPI backend for the Indian Citizen Rights & Government Services Assistant.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    response_mode: Optional[str] = "normal"
    user_id: Optional[int] = 0
    is_admin: bool = False


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/stats")
def stats() -> dict:
    pipeline = getattr(app.state, "pipeline", None)
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline is not initialized")
    return pipeline.get_stats()


@app.post("/query")
def query(request: QueryRequest) -> dict:
    query_text = request.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text must not be empty")

    pipeline = getattr(app.state, "pipeline", None)
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline is not initialized")

    return pipeline.query_with_state(
        {
            "query": query_text,
            "response_mode": request.response_mode,
            "user_id": request.user_id,
            "is_admin": request.is_admin,
        }
    )


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...), uploaded_by_id: int = 0) -> dict:
    if file.content_type not in (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
    ):
        raise HTTPException(status_code=400, detail=f"Unsupported upload type: {file.content_type}")

    raw_dir = Path("data") / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    destination = raw_dir / file.filename

    contents = await file.read()
    destination.write_bytes(contents)

    pipeline = getattr(app.state, "pipeline", None)
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline is not initialized")

    result = pipeline.ingest_file(str(destination), uploaded_by_id=uploaded_by_id)
    return result
