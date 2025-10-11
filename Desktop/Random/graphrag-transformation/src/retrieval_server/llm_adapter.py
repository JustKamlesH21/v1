"""
Lightweight LLM + Embeddings adapter.

This module provides an abstraction layer so the rest of the codebase
doesn't depend directly on a specific provider. It defaults to a
local stub implementation and can be extended to call Google Gemini
or other providers when available.

The adapter exposes:
- get_embedding(text) -> List[float]
- generate(text, **kwargs) -> str

For production, replace the stubbed implementations with calls to
Google's Generative AI SDK (Gemini) or another provider.
"""
from typing import List
import os
import time
import logging
from typing import Optional

# Try to import Google's Generative AI SDK (Gemini). If it's not available
# we fall back to a deterministic stub so the application and tests can run
# without network access or extra packages.
_HAS_GENAI = False
_GENAI = None
_LOGGER = logging.getLogger(__name__)
try:
    import google.generativeai as genai  # type: ignore
    _GENAI = genai
    _HAS_GENAI = True
except Exception:
    _HAS_GENAI = False


def _configure_genai_from_env():
    """Configure the Google Generative AI SDK from environment variables.

    It will try these options (in order):
    - If GOOGLE_API_KEY is set, call genai.configure(api_key=...)
    - Otherwise rely on GOOGLE_APPLICATION_CREDENTIALS or ADC.
    """
    if not _HAS_GENAI:
        return
    api_key = os.getenv("GOOGLE_API_KEY")
    try:
        if api_key:
            # genai.configure is the expected call in many versions of the SDK
            if hasattr(_GENAI, "configure"):
                _GENAI.configure(api_key=api_key)
                _LOGGER.debug("Configured Google Generative AI SDK with API key from env")
            else:
                # Some SDK variants expect a different config method; set env as fallback
                os.environ.setdefault("GOOGLE_API_KEY", api_key)
                _LOGGER.debug("Set GOOGLE_API_KEY in environment as fallback")
        else:
            _LOGGER.debug("No GOOGLE_API_KEY found; relying on ADC if available")
    except Exception as e:
        _LOGGER.warning("Failed to configure Google Generative AI SDK: %s", e)


_configure_genai_from_env()


def get_embedding(text: str, model: str = "embed-text-001") -> List[float]:
    """Return an embedding for the provided text.

    If the Google Generative AI SDK is installed and configured, use it.
    Otherwise return a deterministic stub vector (useful for tests).

    Args:
        text: Input text to embed.
        model: Optional model name (SDK-dependent).

    Returns:
        A list of floats representing the embedding.
    """
    if _HAS_GENAI:
        # small retry/backoff wrapper
        def _try_get_embeddings():
            # Different SDK versions expose embeddings differently. Try common patterns.
            if hasattr(_GENAI, "get_embeddings"):
                return _GENAI.get_embeddings(model=model, input=[text])
            if hasattr(_GENAI, "embeddings"):
                return _GENAI.embeddings.create(model=model, input=text)
            # older variant
            if hasattr(_GENAI, "getEmbedding"):
                return _GENAI.getEmbedding(model=model, input=text)
            raise RuntimeError("No compatible embeddings API found on google.generativeai module")

        retries = 3
        backoff = 0.5
        last_err = None
        for attempt in range(1, retries + 1):
            try:
                resp = _try_get_embeddings()
                # resp may be a dict with 'data' or an object
                if isinstance(resp, dict) and "data" in resp:
                    emb = resp["data"][0].get("embedding") or resp["data"][0]
                    return emb
                if hasattr(resp, "embeddings"):
                    return resp.embeddings[0].embedding
                if isinstance(resp, list):
                    return resp[0].get("embedding")
                # try attribute
                if hasattr(resp, "data"):
                    return resp.data[0].embedding
                # fallback: return resp directly if it's a vector
                return resp
            except Exception as e:
                last_err = e
                _LOGGER.warning("Embedding attempt %d failed: %s", attempt, e)
                time.sleep(backoff * attempt)
        raise RuntimeError("Failed to obtain embedding from Google Generative AI SDK after retries") from last_err

    # Deterministic stub for local runs/tests: map characters into a small vector
    vec = [float((ord(c) % 10) / 10.0) for c in text[:128]]
    size = 153
    if len(vec) >= size:
        return vec[:size]
    return vec + [0.0] * (size - len(vec))


def generate(prompt: str, model: str = "text-bison-001", temperature: float = 0.0) -> str:
    """Generate text using Gemini (or the stub).

    Args:
        prompt: The input prompt.
        model: Model name; SDK-specific.
        temperature: Sampling temperature.

    Returns:
        Generated string.
    """
    if _HAS_GENAI:
        def _try_generate():
            # Try a few common call-signatures across SDK versions
            if hasattr(_GENAI, "generate"):
                return _GENAI.generate(model=model, prompt=prompt, temperature=temperature)
            if hasattr(_GENAI, "responses"):
                return _GENAI.responses.create(model=model, input=prompt)
            if hasattr(_GENAI, "text"):
                return _GENAI.text.generate(model=model, prompt=prompt)
            raise RuntimeError("No compatible generate API found on google.generativeai module")

        retries = 3
        backoff = 0.5
        last_err = None
        for attempt in range(1, retries + 1):
            try:
                resp = _try_generate()
                if isinstance(resp, dict):
                    if "candidates" in resp and len(resp["candidates"]) > 0:
                        return resp["candidates"][0].get("content", str(resp))
                    if "output" in resp and isinstance(resp["output"], dict):
                        # responses.create style
                        candidates = resp["output"].get("candidates") or []
                        if len(candidates) > 0:
                            return candidates[0].get("content", str(resp))
                if hasattr(resp, "text"):
                    return resp.text
                if hasattr(resp, "output") and hasattr(resp.output, "text"):
                    return resp.output.text
                return str(resp)
            except Exception as e:
                last_err = e
                _LOGGER.warning("Generation attempt %d failed: %s", attempt, e)
                time.sleep(backoff * attempt)
        raise RuntimeError("Failed to generate text from Google Generative AI SDK after retries") from last_err

    # Fallback stub
    return f"[stub-generated response] {prompt[:200]}"
