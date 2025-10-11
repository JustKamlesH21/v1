import os
import unittest

from src.retrieval_server import llm_adapter


@unittest.skipUnless(os.getenv("GOOGLE_API_KEY"), "Integration test requires GOOGLE_API_KEY")
class TestGeminiIntegration(unittest.TestCase):
    def test_get_embedding_integration(self):
        emb = llm_adapter.get_embedding("hello world")
        # Expect a non-empty list of floats
        self.assertIsInstance(emb, list)
        self.assertGreater(len(emb), 0)
        self.assertIsInstance(emb[0], float)


if __name__ == "__main__":
    unittest.main()
