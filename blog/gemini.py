"""Thin adapter over the Google Gemini API.

Both the RAG chatbot (`blog/utils.py`) and the authoring helpers
(`blog/views.py`) go through these two functions so the provider lives in one
place. The client is built lazily so importing this module never requires a key
(tests patch `embed_text` / `generate_text` and never construct a client).
"""

import os

from google import genai
from google.genai import types

# gemini-embedding-001 defaults to 3072 dims; 1536 is the same value stored in
# blog/df.pkl by the regenerate_embeddings command. Query and stored embeddings
# MUST share this dimensionality or cosine distance is meaningless.
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 1536
GENERATION_MODEL = "gemini-2.5-flash"

_client = None


def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def embed_text(text: str) -> list[float]:
    response = get_client().models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
    )
    return response.embeddings[0].values


def generate_text(prompt: str, max_output_tokens: int, temperature: float = 0.5) -> str:
    """Single-shot text generation with thinking disabled.

    Thinking is off (`thinking_budget=0`) because every caller wants a short,
    deterministic string and the reasoning tokens would otherwise consume the
    tight `max_output_tokens` budget and return empty text.
    """
    response = get_client().models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    text = response.text
    if not text or not text.strip():
        # A null/empty response means the candidate carried no text — safety
        # block, recitation, or MAX_TOKENS with nothing emitted. Fail loud so
        # the caller's logger fires instead of rendering a blank answer.
        candidate = (response.candidates or [None])[0]
        raise RuntimeError(
            "Gemini returned no text "
            f"(finish_reason={getattr(candidate, 'finish_reason', None)}, "
            f"block_reason={getattr(response.prompt_feedback, 'block_reason', None)})"
        )
    return text.strip()
