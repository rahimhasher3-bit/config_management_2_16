"""Tests for stage 3 dependency graph operations."""

import sys
import tempfile
import unittest
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from dependency_graph import build_dependency_graph
from test_repository import (
    create_test_loader,
    load_test_repository,
    parse_repository_line,
    validate_package_name,
)


class TestStage3(unittest.TestCase):

    def test_simple_graph(self):
        source_graph = {
            "A": ["B"],
            "B": ["C"],
            "C": [],
        }

        loader = create_test_loader(
            source_graph
        )

        result = build_dependency_graph(
            "A",
            loader,
            3,
        )

        self.assertEqual(
            result,
            {
                "A": ["B"],
                "B": ["C"],
                "C": [],
            },
        )

    def test_max_depth(self):
        source_graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["E"],
            "D": [],
            "E": [],
        }

        loader = create_test_loader(
            source_graph
        )

        result = build_dependency_graph(
            "A",
            loader,
            1,
        )

        self.assertEqual(
            result,
            {
                "A": ["B", "C"],
                "B": [],
                "C": [],
            },
        )

    def test_cycle(self):
        source_graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }

        loader = create_test_loader(
            source_graph
        )

        result = build_dependency_graph(
            "A",
            loader,
            5,
        )

        self.assertEqual(
            result,
            {
                "A": ["B"],
                "B": ["C"],
                "C": ["A"],
            },
        )

    def test_parse_repository_line(self):
        package, dependencies = (
            parse_repository_line(
                "A: B C",
                1,
            )
        )

        self.assertEqual(
            package,
            "A",
        )

        self.assertEqual(
            dependencies,
            ["B", "C"],
        )

    def test_invalid_package_name(self):
        with self.assertRaises(ValueError):
            validate_package_name(
                "package"
            )

    def test_missing_colon(self):
        with self.assertRaises(ValueError):
            parse_repository_line(
                "A B C",
                1,
            )

    def test_load_repository_file(self):
        content = (
            "A: B C\n"
            "B:\n"
            "C:\n"
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
        ) as file:
            file.write(content)
            file_path = file.name

        try:
            graph = load_test_repository(
                file_path
            )
        finally:
            Path(file_path).unlink()

        self.assertEqual(
            graph,
            {
                "A": ["B", "C"],
                "B": [],
                "C": [],
            },
        )


if __name__ == "__main__":
    unittest.main()