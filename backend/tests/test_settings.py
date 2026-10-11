"""Guards on how configuration is loaded, not on any particular value.

`.env.sample` only works as documentation if it stays complete, and it is the
kind of file that rots quietly: a new field added to `config/env.py` reads its
default from the class, the project still starts, and nobody notices the key is
undocumented until someone goes looking for a knob that was never written down.
The parity test below turns that into a failure at the moment it happens.
"""
import os
import re
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase
from pydantic import ValidationError

from config.env import BASE_DIR, Settings

SAMPLE = BASE_DIR / ".env.sample"
KEY = re.compile(r"^([A-Z][A-Z0-9_]*)=", re.MULTILINE)


def sample_keys() -> set[str]:
    return set(KEY.findall(SAMPLE.read_text(encoding="utf-8")))


class EnvSampleTests(SimpleTestCase):
    def test_sample_documents_every_setting(self):
        """Every field the project reads is named in the committed sample."""
        undocumented = set(Settings.model_fields) - sample_keys()
        self.assertEqual(undocumented, set(),
                         f"add these to .env.sample: {', '.join(sorted(undocumented))}")

    def test_sample_names_no_setting_the_project_ignores(self):
        """A key nothing reads is worse than no key: it looks like it works."""
        unread = sample_keys() - set(Settings.model_fields)
        self.assertEqual(unread, set(),
                         f"no field in config/env.py reads: {', '.join(sorted(unread))}")


class EnvLayeringTests(SimpleTestCase):
    """The precedence `config/env.py` promises: environment > `.env` > `.env.sample`."""

    def test_sample_is_read_as_configuration(self):
        """A checkout with no `.env` still starts with the sample's values."""
        self.assertIn(str(SAMPLE), [str(path) for path in Settings.model_config["env_file"]])
        self.assertTrue(SAMPLE.exists(), "the sample is configuration, so it must be committed")

    def test_local_env_file_outranks_the_sample(self):
        files = [Path(path).name for path in Settings.model_config["env_file"]]
        self.assertLess(files.index(".env.sample"), files.index(".env"),
                        "pydantic-settings lets later files win, so `.env` must come last")

    def test_process_environment_outranks_both_files(self):
        """How the serve pipeline forces a setting for one run without editing a file."""
        with patch.dict(os.environ, {"OTP_BACKEND": "console"}):
            self.assertEqual(Settings().OTP_BACKEND, "console")

    def test_a_bad_value_is_rejected_at_startup(self):
        """Validation is the point of the typed fields: fail here, not mid-request."""
        with patch.dict(os.environ, {"OTP_CODE_LENGTH": "99"}):
            with self.assertRaises(ValidationError):
                Settings()
