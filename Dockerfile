# ============================================================
# Production-Grade RAG System — Optimized Dockerfile
# ============================================================

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Install CPU-optimized PyTorch first to save space, then other requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt


# Stage 2: Final lightweight image
FROM python:3.11-slim AS runner

WORKDIR /app

# Install system utilities needed by python-docx/pdfplumber
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code and files
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY scripts/ ./scripts/
COPY evaluation/ ./evaluation/
COPY data/ ./data/
COPY .streamlit/ ./.streamlit/
COPY Makefile README.md pytest.ini ./

# Create directories for storage
RUN mkdir -p chroma_db logs evaluation/reports

# Environment variables
ENV PYTHONUNBUFFERED=1

EXPOSE 8501
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:${PORT:-8501}/_stcore/health || exit 1

# Command to run Streamlit — uses $PORT for cloud platforms (Render, etc.)
CMD ["sh", "-c", "streamlit run frontend/app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]
