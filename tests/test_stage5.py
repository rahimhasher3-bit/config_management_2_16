"""Tests for stage 5 visualization."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from visualization import (
    escape_dot_text,
    graph_to_ascii_tree,
    graph_to_dot,
    save_graph_png,
)


class TestStage5(unittest.TestCase):

    def test_escape_dot_text(self):
        result = escape_dot_text(
            'package"name'
        )

        self.assertEqual(
            result,
            'package\\"name',
        )

    def test_graph_to_dot(self):
        graph = {
            "A": ["B", "C"],
            "B": [],
            "C": [],
        }

        result = graph_to_dot(
            graph
        )

        self.assertIn(
            '"A" -> "B";',
            result,
        )

        self.assertIn(
            '"A" -> "C";',
            result,
        )

        self.assertTrue(
            result.startswith(
                "digraph dependencies {"
            )
        )

    def test_ascii_tree(self):
        graph = {
            "A": ["B", "C"],
            "B": [],
            "C": [],
        }

        result = graph_to_ascii_tree(
            graph,
            "A",
        )

        self.assertIn(
            "A",
            result,
        )

        self.assertIn(
            "├── B",
            result,
        )

        self.assertIn(
            "└── C",
            result,
        )

    def test_ascii_tree_cycle(self):
        graph = {
            "A": ["B"],
            "B": ["A"],
        }

        result = graph_to_ascii_tree(
            graph,
            "A",
        )

        self.assertIn(
            "A [cycle]",
            result,
        )

    @patch("visualization.subprocess.run")
    @patch("visualization.find_dot")
    def test_save_graph_png(
        self,
        mock_find_dot,
        mock_run,
    ):
        mock_find_dot.return_value = "dot"

        save_graph_png(
            "digraph test {}",
            "test.png",
        )

        mock_run.assert_called_once()

        arguments = (
            mock_run.call_args.args[0]
        )

        self.assertEqual(
            arguments[0],
            "dot",
        )

        self.assertIn(
            "-Tpng",
            arguments,
        )

        self.assertIn(
            "test.png",
            arguments,
        )


if __name__ == "__main__":
    unittest.main()