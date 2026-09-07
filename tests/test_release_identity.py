import os
from unittest.mock import patch

from django.test import Client, override_settings

from .base import SetUp


@override_settings(ALLOWED_HOSTS=["www.blogthedata.com", "blogthedata.com"])
class ProductionReleaseIdentityTests(SetUp):
    def test_deployed_build_is_identifiable_on_pages_redirects_and_errors(self):
        commit = "0326f35a191e07e60372ec8f2769e5b3cb3dd0a6"
        with patch.dict(os.environ, {"HEROKU_BUILD_COMMIT": commit}):
            client = Client()
            page = client.get("/", HTTP_HOST="www.blogthedata.com", secure=True)
            redirect = client.get("/", HTTP_HOST="blogthedata.com", secure=True)
            missing = client.get(
                "/missing-release-probe/", HTTP_HOST="www.blogthedata.com", secure=True
            )
        self.assertEqual(page.status_code, 200)
        self.assertEqual(redirect.status_code, 301)
        self.assertEqual(missing.status_code, 404)
        for response in (page, redirect, missing):
            self.assertEqual(response["x-release-id"], commit)

    def test_unconfigured_or_invalid_build_identity_cannot_pass_release_verification(self):
        for commit in (None, "dev", "0326f35-dirty", "release\r\nInjected: header"):
            with self.subTest(commit=commit), patch.dict(os.environ):
                if commit is None:
                    os.environ.pop("HEROKU_BUILD_COMMIT", None)
                else:
                    os.environ["HEROKU_BUILD_COMMIT"] = commit
                response = Client().get("/", HTTP_HOST="www.blogthedata.com", secure=True)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["x-release-id"], "dev")
