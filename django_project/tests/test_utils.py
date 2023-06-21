from .base import SetUp
from django.utils.deprecation import MiddlewareMixin
from blog.utils import create_context, answer_question, load_pickle_file
import pandas as pd
from unittest.mock import patch


class TestUtils(SetUp, MiddlewareMixin):
    def test_load_pickle_file(self):
        df = load_pickle_file()
        self.assertIsInstance(df, pd.DataFrame)

    def test_create_context(self):
        df = load_pickle_file()
        context = create_context(
            "What is the capital of the United States of America?", df
        )
        self.assertIsInstance(context, str)

    @patch("openai.Completion.create")
    @patch("blog.utils.load_pickle_file")
    def test_answer_question(self, mock_load_pickle_file):
        mock_load_pickle_file.return_value = pd.DataFrame(
            {"text": ["The capital of the United States is Washington, D.C."]}
        )

        answer = answer_question(
            question="What is the capital of the United States of America?"
        )
        self.assertEqual(answer, "Washington, D.C.")
