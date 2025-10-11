from typing import Dict, Any, List
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # pragma: no cover - optional dev dependency
    load_dotenv = lambda *a, **k: None

from src.retrieval_server import llm_adapter

class QueryAgent:
    """
    An agent that dynamically determines the optimal retrieval strategy.
    """

    def __init__(self, graph_populator, vector_store=None, embedding_model: str = "embed-text-001"):
        """
        Initializes the QueryAgent.

        Args:
            graph_populator: An instance of GraphPopulator.
        """
        self.graph_populator = graph_populator
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def get_embedding(self, text: str, model="text-embedding-ada-002"):
        """
        Gets the embedding for a given text.
        """
        # Delegate to the provider-agnostic adapter. Tests patch the adapter.
        return llm_adapter.get_embedding(text, model=model)

    def decide_retrieval_strategy(self, query: str) -> str:
        """
        Decides the retrieval strategy based on the query.
        """
        # Heuristic first
        ql = query.lower()
        if "similar to" in ql or "similar" in ql:
            return "vector_search"
        if "connected to" in ql or "relationship between" in ql or "path" in ql:
            return "graph_traversal"

        # If ambiguous, ask the LLM to decide
        try:
            prompt = f"Decide the best retrieval strategy for this user query. Options: vector_search, graph_traversal, logical_filtering. Query: {query}\nReturn only one word."
            resp = llm_adapter.generate(prompt, model="text-bison-001")
            r = resp.strip().lower()
            if "vector" in r:
                return "vector_search"
            if "graph" in r:
                return "graph_traversal"
            return "logical_filtering"
        except Exception:
            return "logical_filtering"

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieves information based on the query.
        """
        strategy = self.decide_retrieval_strategy(query)
        if strategy == "vector_search":
            return self._perform_vector_search(query)
        elif strategy == "graph_traversal":
            return self._perform_graph_traversal(query)
        else:
            return self._perform_logical_filtering(query)

    def _perform_vector_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Performs a vector similarity search.
        """
        if self.vector_store is None:
            print("No vector store configured; returning empty results")
            return []
        # get embedding for query
        emb = self.get_embedding(query, model=self.embedding_model)
        results = self.vector_store.search(emb, top_k=5)
        return results

    def _perform_graph_traversal(self, query: str) -> List[Dict[str, Any]]:
        """
        Performs a graph traversal.
        """
        # This is a placeholder for the actual graph traversal implementation.
        print(f"Performing graph traversal for: {query}")
        return []

    def _perform_logical_filtering(self, query: str) -> List[Dict[str, Any]]:
        """
        Performs logical filtering.
        """
        # This is a placeholder for the actual logical filtering implementation.
        print(f"Performing logical filtering for: {query}")
        return []