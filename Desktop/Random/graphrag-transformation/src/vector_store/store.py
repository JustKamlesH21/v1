from typing import List, Dict, Any, Optional
import math

try:
    import faiss  # type: ignore
    _HAS_FAISS = True
except Exception:
    _HAS_FAISS = False


class VectorStore:
    """Simple vector store with FAISS when available, else an in-memory fallback.

    API:
    - add(id: str, vector: List[float], metadata: dict)
    - search(query_vector: List[float], top_k: int) -> List[Dict[str, Any]]
    """

    def __init__(self, dim: int):
        self.dim = dim
        self.ids: List[str] = []
        self.vectors: List[List[float]] = []
        self.metadatas: List[Dict[str, Any]] = []
        if _HAS_FAISS:
            self.index = faiss.IndexFlatIP(dim)  # inner product; we will normalize
        else:
            self.index = None

    @staticmethod
    def _normalize(vec: List[float]) -> List[float]:
        norm = math.sqrt(sum(x * x for x in vec))
        if norm == 0:
            return vec
        return [x / norm for x in vec]

    def add(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None):
        if len(vector) != self.dim:
            raise ValueError("Vector dimensionality mismatch")
        norm = self._normalize(vector)
        self.ids.append(id)
        self.vectors.append(norm)
        self.metadatas.append(metadata or {})
        if _HAS_FAISS:
            import numpy as np

            self.index.add(np.array([norm], dtype="float32"))

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        q = self._normalize(query_vector)
        results: List[Dict[str, Any]] = []
        if _HAS_FAISS and self.index is not None and len(self.ids) > 0:
            import numpy as np

            qn = np.array([q], dtype="float32")
            D, I = self.index.search(qn, min(top_k, len(self.ids)))
            for score, idx in zip(D[0].tolist(), I[0].tolist()):
                results.append({"id": self.ids[idx], "score": float(score), "metadata": self.metadatas[idx]})
            return results

        # Fallback in-memory linear search with cosine similarity
        sims: List[Tuple[int, float]] = []
        for i, v in enumerate(self.vectors):
            sim = sum(a * b for a, b in zip(q, v))
            sims.append((i, sim))
        sims.sort(key=lambda x: x[1], reverse=True)
        for idx, score in sims[:top_k]:
            results.append({"id": self.ids[idx], "score": float(score), "metadata": self.metadatas[idx]})
        return results
