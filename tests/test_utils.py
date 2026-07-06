from django.utils.deprecation import MiddlewareMixin
from blog.utils import (
    create_context,
    answer_question,
    load_pickle_file,
    preprocess_text,
)
import pandas as pd
from unittest.mock import patch
import numpy as np
from unittest import TestCase


class TestUtils(TestCase, MiddlewareMixin):
    def test_load_pickle_file(self):
        df = load_pickle_file()
        self.assertIsInstance(df, pd.DataFrame)

    def test_preprocess_text_lowercases_strips_noise_and_drops_stopwords(self):
        # A realistic blog sentence with mixed case, a digit, punctuation, and stopwords.
        result = preprocess_text(
            "Django 5 is a popular Python framework for building blogs, and it's fast!"
        )
        tokens = result.split()
        # Lowercased, with digits and punctuation stripped entirely.
        self.assertEqual(result, result.lower())
        self.assertFalse(any(ch.isdigit() for ch in result))
        for punct in (",", "!", "'"):
            self.assertNotIn(punct, result)
        # English stopwords are removed...
        for stopword in ("is", "a", "for", "and"):
            self.assertNotIn(stopword, tokens)
        # ...while content words survive.
        for keyword in ("django", "popular", "python", "framework", "blogs", "fast"):
            self.assertIn(keyword, tokens)

    @patch("blog.utils.load_pickle_file")
    @patch("blog.utils.embed_text")
    def test_create_context(self, mock_embed_text, mock_load_pickle_file):
        mock_load_pickle_file.return_value = pd.DataFrame(
            {
                "text": ["The capital of the United States is Washington, D.C."],
                "embeddings": [np.random.random(1536)],
                "n_tokens": [10],
                "content": ["The capital of the United States is Washington, D.C."],
            }
        )
        mock_embed_text.return_value = np.random.random(1536)
        context = create_context(
            "What is the capital of the United States of America?",
            mock_load_pickle_file.return_value,
        )
        self.assertIsInstance(context, str)
        # The selected context must actually carry the source row's content,
        # not just be some string — otherwise the retrieval logic is untested.
        self.assertIn("Washington, D.C.", context)

    @patch("blog.utils.load_pickle_file")
    @patch("blog.utils.embed_text")
    def test_create_context_exceed_max_len(
        self, mock_embed_text, mock_load_pickle_file
    ):
        mock_load_pickle_file.return_value = pd.DataFrame(
            {
                "text": ["The capital of the United States is Washington, D.C."]
                * 200,  # Multiply by 200 to exceed max_len
                "embeddings": [np.random.random(1536)] * 200,
                "n_tokens": [10] * 200,
                "content": ["The capital of the United States is Washington, D.C."]
                * 200,
            }
        )
        mock_embed_text.return_value = np.random.random(1536)
        context = create_context(
            "What is the capital of the United States of America?",
            mock_load_pickle_file.return_value,
        )
        self.assertIsInstance(context, str)
        self.assertTrue(len(context.split(" ")) <= 1800)

    @patch("blog.utils.embed_text")
    @patch("blog.utils.generate_text")
    @patch("blog.utils.load_pickle_file")
    def test_answer_question(
        self, mock_load_pickle_file, mock_generate_text, mock_embed_text
    ):
        df = pd.DataFrame(
            {
                "text": ["The capital of the United States is Washington, D.C."],
                "embeddings": [
                    np.random.random(1536)
                ],  # gemini-embedding-001 is 1536-dimensional
                "n_tokens": [10],  # Assuming the text has 10 tokens
                "content": ["The capital of the United States is Washington, D.C."],
            }
        )
        mock_load_pickle_file.return_value = df
        mock_generate_text.return_value = "The mocked answer"
        mock_embed_text.return_value = list(np.random.random(1536))

        answer = answer_question(
            question="What is the capital of the United States of America?", df=df
        )
        self.assertEqual(answer, "The mocked answer")
