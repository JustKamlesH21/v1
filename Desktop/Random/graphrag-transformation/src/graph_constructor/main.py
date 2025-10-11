from src.graph_constructor.graph_populator import GraphPopulator

def run_graph_construction(db_backend: str, ontology: dict, data: list):
    """
    Runs the graph construction process.

    Args:
        db_backend: The graph database backend to use ('neo4j' or 'neptune').
        ontology: A dictionary representing the ontology.
        data: A list of dictionaries representing the data to be inserted.
    """
    graph_populator = GraphPopulator(db_backend)
    graph_populator.populate_graph(ontology, data)
    graph_populator.close()
    print("Graph construction complete.")

if __name__ == "__main__":
    # This is a placeholder for the actual ontology and data
    ONTOLOGY = {
        "classes": [{"name": "Person", "attributes": ["name", "age"]}],
        "properties": [],
    }
    DATA = [{"Person": {"name": "Alice", "age": 30}}, {"Person": {"name": "Bob", "age": 25}}]
    # Replace with your desired backend ('neo4j' or 'neptune')
    DB_BACKEND = "neo4j"
    run_graph_construction(DB_BACKEND, ONTOLOGY, DATA)