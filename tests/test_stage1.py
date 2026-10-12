"""Tests for stage 1 CLI configuration."""

import argparse
import sys
import tempfile
import unittest
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

import main


class TestStage1(unittest.TestCase):

    def test_parse_bool_true(self):
        self.assertTrue(
            main.parse_bool("true")
        )

    def test_parse_bool_false(self):
        self.assertFalse(
            main.parse_bool("false")
        )

    def test_invalid_bool(self):
        with self.assertRaises(
            argparse.ArgumentTypeError
        ):
            main.parse_bool("maybe")

    def test_positive_depth(self):
        self.assertEqual(
            main.parse_positive_int("3"),
            3
        )

    def test_invalid_depth(self):
        with self.assertRaises(
            argparse.ArgumentTypeError
        ):
            main.parse_positive_int("0")

    def test_empty_package(self):
        with self.assertRaises(ValueError):
            main.validate_package("")

    def test_invalid_output(self):
        with self.assertRaises(ValueError):
            main.validate_output(
                "graph.jpg"
            )

    def test_invalid_repository_url(self):
        with self.assertRaises(ValueError):
            main.validate_repository(
                "abc",
                False
            )

    def test_valid_repository_url(self):
        main.validate_repository(
            "https://registry.npmjs.org",
            False
        )

    def test_test_repository_exists(self):
        with tempfile.NamedTemporaryFile() as file:
            main.validate_repository(
                file.name,
                True
            )

    def test_test_repository_missing(self):
        with self.assertRaises(ValueError):
            main.validate_repository(
                "missing_repository.txt",
                True
            )


if __name__ == "__main__":
    unittest.main()