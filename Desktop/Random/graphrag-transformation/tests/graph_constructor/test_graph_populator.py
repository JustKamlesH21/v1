import unittest
from unittest.mock import MagicMock, patch
from src.graph_constructor.graph_populator import GraphPopulator

class TestGraphPopulator(unittest.TestCase):
    """
    Unit tests for the GraphPopulator.
    """

    @patch("src.graph_constructor.graph_populator.GraphDatabase.driver")
    def test_populate_neo4j(self, mock_driver):
        """
        Tests that the populate_neo4j method calls the correct Neo4j driver methods.
        """
        mock_session = MagicMock()
        mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
        graph_populator = GraphPopulator("neo4j")
        ontology = {
            "classes": [{"name": "Person", "attributes": ["name", "age"]}],
        }
        data = [{"Person": {"name": "Alice", "age": 30}}]
        graph_populator.populate_graph(ontology, data)
        mock_session.run.assert_called_once_with(
            "CREATE (n:Person $props)",
            props={"name": "Alice", "age": 30},
        )

    @patch("src.graph_constructor.graph_populator.client.Client")
    def test_populate_neptune(self, mock_client):
        """
        Tests that the populate_neptune method calls the correct Gremlin client methods.
        """
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        graph_populator = GraphPopulator("neptune")
        ontology = {
            "classes": [{"name": "Person", "attributes": ["name", "age"]}],
        }
        data = [{"Person": {"name": "Alice", "age": 30}}]
        graph_populator.populate_graph(ontology, data)
        mock_client_instance.submit.assert_called_once_with(
            "g.addV('Person').property('name', 'Alice').property('age', '30')"
        )

if __name__ == "__main__":
    unittest.main()