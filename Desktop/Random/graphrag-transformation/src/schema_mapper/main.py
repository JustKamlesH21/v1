from src.utils.db_connector import DBConnector
from src.schema_mapper.relational_schema_parser import RelationalSchemaParser

def run_schema_mapping(db_url: str):
    """
    Runs the schema mapping process.

    Args:
        db_url: The database URL to connect to.
    """
    db_connector = DBConnector(db_url)
    schema_parser = RelationalSchemaParser(db_connector)
    schema = schema_parser.get_schema()
    ontology = schema_parser.suggest_ontology(schema)
    print("Suggested Ontology:")
    print(ontology)

if __name__ == "__main__":
    # Replace with your actual database URL
    DB_URL = "sqlite:///:memory:"
    run_schema_mapping(DB_URL)