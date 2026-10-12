"""Tests for stage 4 reverse dependencies."""

import sys
import unittest
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from dependency_graph import (
    build_reverse_dependency_graph,
    graph_contains_package,
    reverse_graph,
)


class TestStage4(unittest.TestCase):

    def test_reverse_graph(self):
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }

        result = reverse_graph(
            graph
        )

        self.assertEqual(
            result,
            {
                "A": [],
                "B": ["A"],
                "C": ["A"],
                "D": ["B", "C"],
            },
        )

    def test_transitive_reverse_dependencies(self):
        graph = {
            "A": ["B"],
            "B": ["D"],
            "D": [],
        }

        result = build_reverse_dependency_graph(
            "D",
            graph,
            3,
        )

        self.assertEqual(
            result,
            {
                "D": ["B"],
                "B": ["A"],
                "A": [],
            },
        )

    def test_reverse_max_depth(self):
        graph = {
            "A": ["B"],
            "B": ["D"],
            "D": [],
        }

        result = build_reverse_dependency_graph(
            "D",
            graph,
            1,
        )

        self.assertEqual(
            result,
            {
                "D": ["B"],
                "B": [],
            },
        )

    def test_reverse_cycle(self):
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }

        result = build_reverse_dependency_graph(
            "A",
            graph,
            3,
        )

        self.assertEqual(
            result,
            {
                "A": ["C"],
                "C": ["B"],
                "B": ["A"],
            },
        )

    def test_package_as_dependency(self):
        graph = {
            "A": ["B"],
        }

        self.assertTrue(
            graph_contains_package(
                graph,
                "B",
            )
        )

        self.assertFalse(
            graph_contains_package(
                graph,
                "C",
            )
        )


if __name__ == "__main__":
    unittest.main()