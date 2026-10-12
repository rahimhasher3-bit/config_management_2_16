"""Tests for npm repository functions."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

import npm_repository


class TestStage2(unittest.TestCase):

    def test_build_package_url(self):
        url = npm_repository.build_package_url(
            "https://registry.npmjs.org",
            "express",
        )

        self.assertEqual(
            url,
            "https://registry.npmjs.org/express",
        )

    def test_scoped_package_url(self):
        url = npm_repository.build_package_url(
            "https://registry.npmjs.org",
            "@babel/core",
        )

        self.assertEqual(
            url,
            "https://registry.npmjs.org/@babel%2Fcore",
        )

    def test_latest_version(self):
        metadata = {
            "dist-tags": {
                "latest": "2.0.0",
            }
        }

        self.assertEqual(
            npm_repository.get_latest_version(
                metadata
            ),
            "2.0.0",
        )

    def test_missing_latest_version(self):
        with self.assertRaises(ValueError):
            npm_repository.get_latest_version(
                {}
            )

    def test_direct_dependencies(self):
        metadata = {
            "dist-tags": {
                "latest": "1.0.0",
            },
            "versions": {
                "1.0.0": {
                    "dependencies": {
                        "beta": "^2.0.0",
                        "alpha": "^1.0.0",
                    }
                }
            },
        }

        result = (
            npm_repository
            .get_direct_dependencies(metadata)
        )

        self.assertEqual(
            result,
            {
                "alpha": "^1.0.0",
                "beta": "^2.0.0",
            },
        )

    def test_package_without_dependencies(self):
        metadata = {
            "dist-tags": {
                "latest": "1.0.0",
            },
            "versions": {
                "1.0.0": {}
            },
        }

        result = (
            npm_repository
            .get_direct_dependencies(metadata)
        )

        self.assertEqual(
            result,
            {},
        )

    @patch("npm_repository.urlopen")
    def test_fetch_metadata(self, mock_urlopen):
        metadata = {
            "name": "test-package"
        }

        response = MagicMock()

        response.read.return_value = (
            json.dumps(metadata)
            .encode("utf-8")
        )

        mock_urlopen.return_value.__enter__.return_value = (
            response
        )

        result = (
            npm_repository
            .fetch_package_metadata(
                "https://registry.npmjs.org",
                "test-package",
            )
        )

        self.assertEqual(
            result,
            metadata,
        )


if __name__ == "__main__":
    unittest.main()