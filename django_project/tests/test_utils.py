from .base import SetUp
from django.utils.deprecation import MiddlewareMixin
from blog.utils import create_context, answer_question, load_pickle_file
import pandas as pd
from unittest.mock import patch
import numpy as np


class TestUtils(SetUp, MiddlewareMixin):
    def test_load_pickle_file(self):
        df = load_pickle_file()
        self.assertIsInstance(df, pd.DataFrame)

    @patch("blog.utils.load_pickle_file")
    @patch("openai.Embedding.create")
    def test_create_context(self, mock_create, mock_load_pickle_file):
        mock_load_pickle_file.return_value = pd.DataFrame(
            {
                "text": ["The capital of the United States is Washington, D.C."],
                "embeddings": [
                    np.random.random(512)
                ],  # Assuming embeddings are 512-dimensional
                "n_tokens": [10],  # Assuming the text has 10 tokens
                "content": ["The capital of the United States is Washington, D.C."],
            }
        )
        mock_create.return_value = {
            "data": [{"embedding": np.random.random(512)}]
        }  # Assuming embeddings are 512-dimensional
        context = create_context(
            "What is the capital of the United States of America?",
            mock_load_pickle_file.return_value,
        )
        self.assertIsInstance(context, str)

    @patch("openai.Embedding.create")
    @patch("openai.Completion.create")
    @patch("blog.utils.load_pickle_file")
    def test_answer_question(
        self, mock_load_pickle_file, mock_create, mock_embedding_create
    ):
        df = pd.DataFrame(
            {
                "text": ["The capital of the United States is Washington, D.C."],
                "embeddings": [
                    [0.0 for _ in range(512)]
                ],  # Assuming embeddings are 512-dimensional
                "n_tokens": [10],  # Assuming the text has 10 tokens
                "content": ["The capital of the United States is Washington, D.C."],
            }
        )
        mock_load_pickle_file.return_value = df
        mock_create.return_value = {"choices": [{"text": "The mocked answer"}]}
        mock_embedding_create.return_value = {
            "data": [{"embedding": [0.0 for _ in range(512)]}]
        }

        answer = answer_question(
            question="What is the capital of the United States of America?", df=df
        )
        self.assertEqual(answer, "The mocked answer")
