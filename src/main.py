"""CLI prototype for dependency graph visualizer."""

import argparse
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_OUTPUT = "dependency_graph.png"
DEFAULT_MAX_DEPTH = 3

BOOLEAN_VALUES = {
    "true": True,
    "false": False,
}


def parse_bool(value):
    """Convert true/false text to a boolean value."""
    normalized = value.lower()

    if normalized not in BOOLEAN_VALUES:
        raise argparse.ArgumentTypeError(
            "ожидается значение true или false"
        )

    return BOOLEAN_VALUES[normalized]


def parse_positive_int(value):
    """Convert text to a positive integer."""
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
    """Validate the package name."""
    if not package.strip():
        raise ValueError(
            "имя пакета не может быть пустым"
        )


def validate_output(output):
    """Validate the output image filename."""
    path = Path(output)

    if not path.name:
        raise ValueError(
            "не указано имя выходного файла"
        )

    if path.suffix.lower() != ".png":
        raise ValueError(
            "выходной файл должен иметь расширение .png"
        )


def validate_repository(repository, test_mode):
    """Validate repository URL or test repository path."""
    if test_mode:
        path = Path(repository)

        if not path.is_file():
            raise ValueError(
                "файл тестового репозитория не найден"
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
    """Validate all command-line parameters."""
    validate_package(args.package)
    validate_output(args.output)

    validate_repository(
        args.repository,
        args.test_mode,
    )


def create_parser():
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Визуализатор графа зависимостей "
            "для npm-пакетов"
        )
    )

    parser.add_argument(
        "--package",
        required=True,
        help="Имя анализируемого пакета",
    )

    parser.add_argument(
        "--repository",
        required=True,
        help="URL репозитория или путь к тестовому файлу",
    )

    parser.add_argument(
        "--test-mode",
        type=parse_bool,
        required=True,
        help="Режим тестового репозитория: true/false",
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Имя PNG-файла с изображением графа",
    )

    parser.add_argument(
        "--ascii-tree",
        type=parse_bool,
        required=True,
        help="Вывод ASCII-дерева: true/false",
    )

    parser.add_argument(
        "--max-depth",
        type=parse_positive_int,
        default=DEFAULT_MAX_DEPTH,
        help="Максимальная глубина анализа",
    )

    return parser


def print_configuration(args):
    """Print configuration as key-value pairs."""
    print("Параметры конфигурации:")
    print(f"package = {args.package}")
    print(f"repository = {args.repository}")
    print(f"test_mode = {args.test_mode}")
    print(f"output = {args.output}")
    print(f"ascii_tree = {args.ascii_tree}")
    print(f"max_depth = {args.max_depth}")


def main():
    """Run the stage 1 CLI application."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        validate_arguments(args)
    except ValueError as error:
        parser.error(str(error))

    print_configuration(args)


if __name__ == "__main__":
    main()