# Architecture

This document outlines the architecture of the RelationalDB to GraphRag Transformation system.

## Components

The system is composed of three main components:

1.  **Schema-to-Ontology Mapping:** This component is responsible for analyzing the relational schema and generating an equivalent ontology.
2.  **Graph Construction and Enrichment:** This component is responsible for converting the relational entities and relationships into graph nodes and edges, and enriching them with semantic information.
3.  **Unified Retrieval Server:** This component provides a unified interface for querying the knowledge graph.

## Technologies

The system will be built using the following technologies:

*   **Programming Language:** Python
*   **Graph Databases:** Neo4j, AWS Neptune
*   **Embeddings:** OpenAI
*   **Embeddings / LLM:** Google Generative AI (Gemini) via `src/retrieval_server/llm_adapter.py`
