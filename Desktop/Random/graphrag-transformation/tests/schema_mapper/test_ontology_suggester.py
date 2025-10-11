import unittest
from unittest.mock import patch

from src.schema_mapper.ontology_suggester import suggest_ontology_from_schema


class TestOntologySuggester(unittest.TestCase):
    @patch("src.schema_mapper.ontology_suggester.llm_adapter.generate")
    def test_suggest_ontology_parses_json(self, mock_generate):
        mock_generate.return_value = '{"classes": [{"name": "users", "attributes": ["id", "name"]}], "relationships": []}'
        schema = {"users": [{"name": "id"}, {"name": "name"}]}
        ont = suggest_ontology_from_schema(schema)
        self.assertIn("classes", ont)
        self.assertEqual(ont["classes"][0]["name"], "users")


if __name__ == "__main__":
    unittest.main()
