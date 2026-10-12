"""CLI dependency graph visualizer."""

import argparse
from pathlib import Path
from urllib.parse import urlparse

from dependency_graph import build_dependency_graph
from npm_repository import load_direct_dependencies
from test_repository import (
    create_test_loader,
    load_test_repository,
    validate_package_name,
)


DEFAULT_OUTPUT = "dependency_graph.png"
DEFAULT_MAX_DEPTH = 3

BOOLEAN_VALUES = {
    "true": True,
    "false": False,
}


def parse_bool(value):
    """Convert true/false text to boolean."""
    normalized = value.lower()

    if normalized not in BOOLEAN_VALUES:
        raise argparse.ArgumentTypeError(
            "ожидается значение true или false"
        )

    return BOOLEAN_VALUES[normalized]


def parse_positive_int(value):
    """Convert text to positive integer."""
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "ожидается целое число"
        ) from error

    if number < 1:
        raise argparse.ArgumentTypeError(
            "значение должно быть больше нуля"
        )

    return number


def validate_package(package):
    """Validate package name."""
    if not package.strip():
        raise ValueError(
            "имя пакета не может быть пустым"
        )


def validate_output(output):
    """Validate output filename."""
    path = Path(output)

    if not path.name:
        raise ValueError(
            "не указано имя выходного файла"
        )

    if path.suffix.lower() != ".png":
        raise ValueError(
            "выходной файл должен "
            "иметь расширение .png"
        )


def validate_repository(
    repository,
    test_mode,
):
    """Validate repository parameter."""
    if test_mode:
        path = Path(repository)

        if not path.is_file():
            raise ValueError(
                "файл тестового "
                "репозитория не найден"
            )

        return

    parsed_url = urlparse(repository)

    if (
        parsed_url.scheme
        not in {"http", "https"}
        or not parsed_url.netloc
    ):
        raise ValueError(
            "неверный URL репозитория"
        )


def validate_arguments(args):
    """Validate command-line parameters."""
    validate_package(
        args.package
    )

    validate_output(
        args.output
    )

    validate_repository(
        args.repository,
        args.test_mode,
    )


def create_parser():
    """Create command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Визуализатор графа зависимостей "
            "для npm-пакетов"
        )
    )

    parser.add_argument(
        "--package",
        required=True,
    )

    parser.add_argument(
        "--repository",
        required=True,
    )

    parser.add_argument(
        "--test-mode",
        type=parse_bool,
        required=True,
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
    )

    parser.add_argument(
        "--ascii-tree",
        type=parse_bool,
        required=True,
    )

    parser.add_argument(
        "--max-depth",
        type=parse_positive_int,
        default=DEFAULT_MAX_DEPTH,
    )

    return parser


def create_real_loader(repository):
    """Create loader for real npm repository."""

    def loader(package_name):
        return load_direct_dependencies(
            repository,
            package_name,
        )

    return loader


def create_dependency_loader(args):
    """Create real or test dependency loader."""
    if not args.test_mode:
        return create_real_loader(
            args.repository
        )

    validate_package_name(
        args.package
    )

    graph = load_test_repository(
        args.repository
    )

    if args.package not in graph:
        raise ValueError(
            "тестовый пакет не найден "
            "в репозитории"
        )

    return create_test_loader(
        graph
    )


def print_dependency_graph(graph):
    """Print dependency graph."""
    print("Граф зависимостей:")

    for package_name, dependencies in graph.items():
        if dependencies:
            dependency_text = ", ".join(
                dependencies
            )

            print(
                f"{package_name} -> "
                f"{dependency_text}"
            )
        else:
            print(
                f"{package_name} ->"
            )


def main():
    """Run application."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        validate_arguments(args)

        loader = create_dependency_loader(
            args
        )

        graph = build_dependency_graph(
            args.package,
            loader,
            args.max_depth,
        )

    except ValueError as error:
        parser.error(str(error))

    print_dependency_graph(
        graph
    )


if __name__ == "__main__":
    main()