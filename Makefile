.PHONY: setup install run-ui run-api test evaluate clean

# ============================================================
# Production-Grade RAG System — Development Commands
# ============================================================

# --- Setup ---
setup: ## Create virtual environment and install dependencies
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt

install: ## Install dependencies only (assumes venv exists)
	./venv/bin/pip install -r requirements.txt

# --- Run ---
run-ui: ## Launch Streamlit frontend
	./venv/bin/streamlit run frontend/app.py --server.port 8501 --server.headless true


run-api: ## Launch FastAPI backend
	./venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# --- Seed ---
seed: ## Seed sample Indian legal documents
	./venv/bin/python scripts/seed_documents.py

# --- Test ---
test: ## Run all tests
	./venv/bin/pytest tests/ -v

# --- Evaluate ---
evaluate: ## Run RAGAS evaluation pipeline
	./venv/bin/python scripts/run_evaluation.py

# --- Quality ---
lint: ## Run linter
	./venv/bin/ruff check src/ tests/ frontend/

format: ## Format code
	./venv/bin/ruff format src/ tests/ frontend/

# --- Clean ---
clean: ## Remove generated data
	rm -rf chroma_db/
	rm -rf logs/*.log
	rm -rf evaluation/reports/*.json
	rm -rf __pycache__ src/__pycache__ tests/__pycache__

clean-all: clean ## Full clean including venv
	rm -rf venv/

# --- Docker ---
docker-build: ## Build Docker image
	docker build -t rag-system .

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

# --- Help ---
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
