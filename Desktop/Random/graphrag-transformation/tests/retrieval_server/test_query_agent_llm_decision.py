import unittest
from unittest.mock import patch, MagicMock

from src.retrieval_server.query_agent import QueryAgent


class TestQueryAgentLLMDecision(unittest.TestCase):
    @patch("src.retrieval_server.query_agent.llm_adapter.generate")
    def test_llm_decision_vector(self, mock_generate):
        mock_generate.return_value = "vector_search"
        qa = QueryAgent(MagicMock())
        strategy = qa.decide_retrieval_strategy("Find documents about cats")
        self.assertEqual(strategy, "vector_search")


if __name__ == "__main__":
    unittest.main()
