"""Functions for reading a test dependency repository."""

import re
from pathlib import Path


PACKAGE_PATTERN = re.compile(r"^[A-Z]+$")


def validate_package_name(package_name):
    """Validate test package name."""
    if not PACKAGE_PATTERN.fullmatch(package_name):
        raise ValueError(
            "имя тестового пакета должно "
            "состоять из заглавных латинских букв"
        )


def parse_repository_line(line, line_number):
    """Parse one test repository line."""
    if ":" not in line:
        raise ValueError(
            f"строка {line_number}: "
            "отсутствует символ ':'"
        )

    package_name, raw_dependencies = (
        line.split(":", 1)
    )

    package_name = package_name.strip()
    validate_package_name(package_name)

    dependencies = (
        raw_dependencies.strip().split()
    )

    for dependency in dependencies:
        validate_package_name(dependency)

    return package_name, dependencies


def load_test_repository(file_path):
    """Load dependency graph from text file."""
    path = Path(file_path)

    if not path.is_file():
        raise ValueError(
            "файл тестового репозитория "
            "не найден"
        )

    graph = {}

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(
            file,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            package_name, dependencies = (
                parse_repository_line(
                    line,
                    line_number,
                )
            )

            graph[package_name] = dependencies

    return graph


def create_test_loader(graph):
    """Create dependency loader for test graph."""

    def loader(package_name):
        dependencies = graph.get(
            package_name,
            []
        )

        return {
            dependency: "test"
            for dependency in dependencies
        }

    return loader