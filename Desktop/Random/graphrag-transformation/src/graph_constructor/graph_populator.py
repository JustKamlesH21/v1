from typing import Dict, Any, List, Optional
import os

# Optional imports: tests may run without these heavy dependencies installed.
try:
    from neo4j import GraphDatabase  # type: ignore
except Exception:  # pragma: no cover - fallback for test environments
    GraphDatabase = None

try:
    from gremlin_python.driver import client  # type: ignore
except Exception:  # pragma: no cover - fallback for test environments
    client = None

# Provide minimal stubs so tests can patch attributes even when packages
# aren't installed in the environment.
class _Neo4jDriverStub:
    @staticmethod
    def driver(*a, **k):
        """Return None or a real driver; tests will patch this attribute."""
        return None

class _GremlinClientStub:
    class Client:
        def __init__(self, *a, **k):
            pass

if GraphDatabase is None:  # pragma: no cover - tests patch this
    GraphDatabase = _Neo4jDriverStub

if client is None:  # pragma: no cover - tests patch this
    client = _GremlinClientStub

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # pragma: no cover
    pass

from src.retrieval_server import llm_adapter

class GraphPopulator:
    """
    Populates a graph database with data from a relational source.
    """

    def __init__(self, db_backend: str, vector_store: Optional[Any] = None, embedding_model: str = "embed-text-001"):
        """
        Initializes the GraphPopulator.

        Args:
            db_backend: The graph database backend to use ('neo4j' or 'neptune').
        """
        self.db_backend = db_backend
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        if self.db_backend == "neo4j":
            uri = os.getenv("NEO4J_URI")
            user = os.getenv("NEO4J_USER")
            password = os.getenv("NEO4J_PASSWORD")
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        elif self.db_backend == "neptune":
            neptune_endpoint = os.getenv("NEPTUNE_ENDPOINT")
            self.client = client.Client(neptune_endpoint, "g")
        else:
            raise ValueError("Unsupported graph database backend.")

    def populate_graph(self, ontology: Dict[str, Any], data: List[Dict[str, Any]]):
        """
        Populates the graph with data.

        Args:
            ontology: A dictionary representing the ontology.
            data: A list of dictionaries representing the data to be inserted.
        """
        if self.db_backend == "neo4j":
            self._populate_neo4j(ontology, data)
        elif self.db_backend == "neptune":
            self._populate_neptune(ontology, data)

    def _populate_neo4j(self, ontology: Dict[str, Any], data: List[Dict[str, Any]]):
        with self.driver.session() as session:
            for item in data:
                for class_info in ontology["classes"]:
                    if class_info["name"] in item:
                        entity = item[class_info["name"]]
                        # Build properties from nested entity dict if present,
                        # otherwise look at top-level keys.
                        if isinstance(entity, dict):
                            properties = {attr: entity.get(attr) for attr in class_info["attributes"]}
                        else:
                            properties = {attr: item.get(attr) for attr in class_info["attributes"]}
                        # Use MERGE on an 'id' property when available to avoid duplicates
                        if properties.get("id"):
                            session.run(
                                f"MERGE (n:{class_info['name']} {{id: $props.id}}) SET n += $props",
                                props=properties,
                            )
                        else:
                            session.run(f"CREATE (n:{class_info['name']} $props)", props=properties)
                        # Optionally compute embeddings and index into vector store
                        if self.vector_store is not None:
                            try:
                                text_for_embedding = " ".join(str(properties.get(k, "")) for k in properties.keys())
                                emb = llm_adapter.get_embedding(text_for_embedding, model=self.embedding_model)
                                node_id = properties.get("id") or properties.get("name") or f"{class_info['name']}_{len(self.vector_store.ids)}"
                                self.vector_store.add(str(node_id), emb, {"label": class_info["name"], **properties})
                            except Exception:
                                pass

    def _populate_neptune(self, ontology: Dict[str, Any], data: List[Dict[str, Any]]):
        for item in data:
            for class_info in ontology["classes"]:
                if class_info["name"] in item:
                    entity = item[class_info["name"]]
                    if isinstance(entity, dict):
                        properties = {attr: entity.get(attr) for attr in class_info["attributes"]}
                    else:
                        properties = {attr: item.get(attr) for attr in class_info["attributes"]}
                    query = f"g.addV('{class_info['name']}')"
                    for key, value in properties.items():
                        query += f".property('{key}', '{value}')"
                    self.client.submit(query)
                    if self.vector_store is not None:
                        try:
                            text_for_embedding = " ".join(str(properties.get(k, "")) for k in properties.keys())
                            emb = llm_adapter.get_embedding(text_for_embedding, model=self.embedding_model)
                            node_id = properties.get("id") or properties.get("name") or f"{class_info['name']}_{len(self.vector_store.ids)}"
                            self.vector_store.add(str(node_id), emb, {"label": class_info["name"], **properties})
                        except Exception:
                            pass

    def close(self):
        """
        Closes the connection to the graph database.
        """
        if self.db_backend == "neo4j":
            self.driver.close()
        elif self.db_backend == "neptune":
            self.client.close()