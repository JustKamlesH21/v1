# RelationalDB to GraphRag Transformation

This project is an automated, production-ready system that transforms structured relational data into a semantically enriched knowledge graph to enable relationship-aware, multi-hop, and semantic retrieval.

Quick start (Gemini):

1. Copy `.env.example` to `.env` and fill in credentials (Google API key or ADC, Neo4j/Neptune endpoints).
2. Create and activate a virtualenv, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3. Run unit tests:

```powershell
cd graphrag-transformation
python -m unittest discover -s tests -p "test_*.py"
```

Notes:
- The project uses Google Generative AI (Gemini) for embeddings and LLM calls via `src/retrieval_server/llm_adapter.py`. If the SDK isn't installed or credentials are not provided, the adapter falls back to a deterministic stub for local development and testing.
- Configure Neo4j or Neptune to enable graph persistence.

Local Neo4j with Docker Compose (quick start):

```powershell
docker compose up -d
# wait for Neo4j to start, then set env vars in .env
$env:NEO4J_URI = 'bolt://localhost:7687'
$env:NEO4J_USER = 'neo4j'
$env:NEO4J_PASSWORD = 'secret'
```

Graph node creation now uses MERGE where appropriate to reduce duplicate nodes during ingestion. For robust entity resolution you should enable a unique `id` column or pass a deduplication strategy into `GraphPopulator`.
