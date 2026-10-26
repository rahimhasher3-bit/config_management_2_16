"""CLI dependency graph visualizer."""

import argparse
from pathlib import Path
from urllib.parse import urlparse

from dependency_graph import (
    build_dependency_graph,
    build_reverse_dependency_graph,
    graph_contains_package,
)
from npm_repository import load_direct_dependencies
from test_repository import (
    create_test_loader,
    load_test_repository,
    validate_package_name,
)
from visualization import (
    graph_to_ascii_tree,
    graph_to_dot,
    save_graph_png,
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
        parsed_url.scheme not in {"http", "https"}
        or not parsed_url.netloc
    ):
        raise ValueError(
            "неверный URL репозитория"
        )


def validate_arguments(args):
    """Validate command-line parameters."""
    validate_package(args.package)
    validate_output(args.output)

    validate_repository(
        args.repository,
        args.test_mode,
    )


def add_repository_arguments(parser):
    """Add package and repository arguments."""
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


def add_visualization_arguments(parser):
    """Add visualization arguments."""
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
    )

    parser.add_argument(
        "--ascii-tree",
        type=parse_bool,
        required=True,
    )


def add_graph_arguments(parser):
    """Add graph traversal arguments."""
    parser.add_argument(
        "--max-depth",
        type=parse_positive_int,
        default=DEFAULT_MAX_DEPTH,
    )

    parser.add_argument(
        "--reverse",
        type=parse_bool,
        default=False,
    )


def create_parser():
    """Create command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Визуализатор графа зависимостей "
            "для npm-пакетов"
        )
    )

    add_repository_arguments(parser)
    add_visualization_arguments(parser)
    add_graph_arguments(parser)

    return parser


def create_real_loader(repository):
    """Create loader for npm repository."""

    def loader(package_name):
        return load_direct_dependencies(
            repository,
            package_name,
        )

    return loader


def create_dependency_loader(args):
    """Create real or test loader."""
    if not args.test_mode:
        return create_real_loader(
            args.repository
        )

    validate_package_name(args.package)

    graph = load_test_repository(
        args.repository
    )

    if not graph_contains_package(
        graph,
        args.package,
    ):
        raise ValueError(
            "тестовый пакет не найден "
            "в репозитории"
        )

    return create_test_loader(graph)


def build_normal_graph(args):
    """Build normal dependency graph."""
    loader = create_dependency_loader(args)

    return build_dependency_graph(
        args.package,
        loader,
        args.max_depth,
    )


def load_reverse_repository(args):
    """Load repository for reverse mode."""
    validate_package_name(args.package)

    repository_graph = load_test_repository(
        args.repository
    )

    if not graph_contains_package(
        repository_graph,
        args.package,
    ):
        raise ValueError(
            "тестовый пакет не найден "
            "в репозитории"
        )

    return repository_graph


def build_reverse_graph(args):
    """Build reverse dependency graph."""
    if not args.test_mode:
        raise ValueError(
            "режим обратных зависимостей "
            "используется с тестовым "
            "репозиторием"
        )

    repository_graph = load_reverse_repository(args)

    return build_reverse_dependency_graph(
        args.package,
        repository_graph,
        args.max_depth,
    )


def build_requested_graph(args):
    """Build requested graph type."""
    if args.reverse:
        return build_reverse_graph(args)

    return build_normal_graph(args)


def print_graph_line(package_name, dependencies):
    """Print one graph line."""
    if dependencies:
        dependency_text = ", ".join(dependencies)
        print(
            f"{package_name} -> "
            f"{dependency_text}"
        )
    else:
        print(
            f"{package_name} ->"
        )


def print_dependency_graph(
    graph,
    reverse_mode,
):
    """Print dependency graph."""
    if reverse_mode:
        print("Граф обратных зависимостей:")
    else:
        print("Граф зависимостей:")

    for package_name, dependencies in graph.items():
        print_graph_line(
            package_name,
            dependencies,
        )


def print_ascii_tree(args, graph):
    """Print ASCII tree when enabled."""
    if not args.ascii_tree:
        return

    print()
    print("ASCII-дерево:")
    print(
        graph_to_ascii_tree(
            graph,
            args.package,
        )
    )


def print_visualization(
    args,
    graph,
    dot_text,
):
    """Print visualization information."""
    print()
    print("Graphviz DOT:")
    print(dot_text)

    print()
    print(
        f"PNG-файл сохранён: {args.output}"
    )

    print_ascii_tree(
        args,
        graph,
    )


def build_visualization(args):
    """Build graph and visualization."""
    graph = build_requested_graph(args)
    dot_text = graph_to_dot(graph)

    save_graph_png(
        dot_text,
        args.output,
    )

    return graph, dot_text


def main():
    """Run application."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        validate_arguments(args)
        graph, dot_text = build_visualization(args)

    except ValueError as error:
        parser.error(str(error))

    print_dependency_graph(
        graph,
        args.reverse,
    )

    print_visualization(
        args,
        graph,
        dot_text,
    )


if __name__ == "__main__":
    main()