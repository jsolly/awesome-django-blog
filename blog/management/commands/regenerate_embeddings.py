"""Rebuild blog/df.pkl with Gemini embeddings.

The chatbot's retrieval compares a query embedding against the per-chunk
embeddings stored in blog/df.pkl. Those were originally produced by OpenAI's
text-embedding-ada-002 (1536-dim); after moving to Gemini they must be
re-embedded with gemini-embedding-001 so query and corpus live in one vector
space. This re-embeds the existing `content` column in place, leaving the chunk
text and n_tokens untouched.
"""

import time

from django.core.management.base import BaseCommand

from blog.gemini import embed_text
from blog.utils import load_pickle_file
from pathlib import Path

# gemini-embedding-001 free tier caps at ~100 requests/minute; a small gap
# keeps the ~300-chunk rebuild under that ceiling without special-casing 429s.
_THROTTLE_SECONDS = 0.7


class Command(BaseCommand):
    help = "Re-embed blog/df.pkl chunks with the current Gemini embedding model."

    def handle(self, *args, **kwargs):
        df = load_pickle_file()
        total = len(df)
        self.stdout.write(
            self.style.SUCCESS(f"Re-embedding {total} chunks with Gemini...")
        )

        embeddings = []
        for i, content in enumerate(df["content"], start=1):
            embeddings.append(embed_text(content))
            if i % 25 == 0 or i == total:
                self.stdout.write(f"  {i}/{total}")
            time.sleep(_THROTTLE_SECONDS)

        df["embeddings"] = embeddings

        out_path = Path(__file__).resolve().parents[3] / "blog" / "df.pkl"
        df.to_pickle(out_path)
        self.stdout.write(self.style.SUCCESS(f"Wrote {total} embeddings to {out_path}"))
