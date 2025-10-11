import unittest
from unittest.mock import MagicMock
from src.schema_mapper.relational_schema_parser import RelationalSchemaParser

class TestRelationalSchemaParser(unittest.TestCase):
    """
    Unit tests for the RelationalSchemaParser.
    """

    def test_get_schema(self):
        """
        Tests that the get_schema method returns the expected schema.
        """
        mock_db_connector = MagicMock()
        mock_db_connector.get_schema.return_value = {
            "users": [
                {"name": "id", "type": "INTEGER", "primary_key": True},
                {"name": "name", "type": "VARCHAR", "primary_key": False},
            ]
        }
        schema_parser = RelationalSchemaParser(mock_db_connector)
        schema = schema_parser.get_schema()
        self.assertEqual(len(schema), 1)
        self.assertIn("users", schema)
        self.assertEqual(len(schema["users"]), 2)

    def test_suggest_ontology(self):
        """
        Tests that the suggest_ontology method returns a valid ontology.
        """
        schema = {
            "users": [
                {"name": "id", "type": "INTEGER"},
                {"name": "name", "type": "VARCHAR"},
            ]
        }
        schema_parser = RelationalSchemaParser(MagicMock())
        ontology = schema_parser.suggest_ontology(schema)
        self.assertIn("classes", ontology)
        self.assertEqual(len(ontology["classes"]), 1)
        self.assertEqual(ontology["classes"][0]["name"], "users")
        self.assertEqual(len(ontology["classes"][0]["attributes"]), 2)

if __name__ == "__main__":
    unittest.main()