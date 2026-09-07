import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from django.test import override_settings

from app.storage_backends import StaticStorage
from tests.base import SetUp


class CloudStaticStorageTests(SetUp):
    def test_cloud_configuration_discovers_repository_stylesheet(self):
        result = subprocess.run(
            [sys.executable, "-c", "import json; from app import settings; print(json.dumps(settings.STATICFILES_DIRS))"],
            env={**os.environ, "USE_CLOUD": "True", "LOGGING": "False"},
            check=True,
            capture_output=True,
            text=True,
        )
        directories = json.loads(result.stdout)
        self.assertTrue(any((Path(directory) / "css/main.css").is_file() for directory in directories))

    @override_settings(DEBUG=False, USE_CLOUD=True, STATIC_HOST="https://cdn.example.com")
    def test_cloud_static_url_uses_manifest_filename(self):
        with patch.object(StaticStorage, "load_manifest", return_value=({"css/main.css": "css/main.abc123.css"}, "manifest-hash")):
            storage = StaticStorage(bucket_name="example", access_key="test", secret_key="test")
        self.assertEqual(storage.url("css/main.css"), "https://cdn.example.com/static/css/main.abc123.css")
        with self.assertRaisesMessage(ValueError, "Missing staticfiles manifest entry"):
            storage.url("css/missing.css")
