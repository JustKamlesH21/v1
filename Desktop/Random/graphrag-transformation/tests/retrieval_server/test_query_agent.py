import unittest
from unittest.mock import MagicMock, patch
from src.retrieval_server.query_agent import QueryAgent

class TestQueryAgent(unittest.TestCase):
    """
    Unit tests for the QueryAgent.
    """

    def test_decide_retrieval_strategy(self):
        """
        Tests that the decide_retrieval_strategy method returns the correct strategy.
        """
        query_agent = QueryAgent(MagicMock())
        self.assertEqual(
            query_agent.decide_retrieval_strategy("Find articles similar to 'dogs'"),
            "vector_search",
        )
        self.assertEqual(
            query_agent.decide_retrieval_strategy("What is the relationship between 'Alice' and 'Bob'"),
            "graph_traversal",
        )
        self.assertEqual(
            query_agent.decide_retrieval_strategy("Find all users with the name 'Alice'"),
            "logical_filtering",
        )

    @patch("src.retrieval_server.query_agent.llm_adapter.get_embedding")
    def test_get_embedding(self, mock_get_embedding):
        """
        Tests that the get_embedding method calls the LLM adapter correctly.
        """
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]
        query_agent = QueryAgent(MagicMock())
        embedding = query_agent.get_embedding("test")
        self.assertEqual(embedding, [0.1, 0.2, 0.3])

if __name__ == "__main__":
    unittest.main()