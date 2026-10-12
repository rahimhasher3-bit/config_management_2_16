"""Graph visualization functions."""

import shutil
import subprocess
from pathlib import Path


WINDOWS_DOT_PATH = (
    r"C:\Program Files\Graphviz\bin\dot.exe"
)


def find_dot():
    """Find Graphviz dot executable."""
    dot_path = shutil.which("dot")

    if dot_path:
        return dot_path

    windows_path = Path(
        WINDOWS_DOT_PATH
    )

    if windows_path.is_file():
        return str(windows_path)

    raise ValueError(
        "Graphviz dot не найден"
    )


def escape_dot_text(text):
    """Escape text for Graphviz DOT."""
    return (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
    )


def graph_to_dot(graph):
    """Convert dependency graph to DOT."""
    nodes = set(graph)

    for dependencies in graph.values():
        nodes.update(dependencies)

    lines = [
        "digraph dependencies {",
        "    rankdir=LR;",
    ]

    for node in sorted(nodes):
        escaped_node = escape_dot_text(
            node
        )

        lines.append(
            f'    "{escaped_node}";'
        )

    for source in sorted(graph):
        for target in graph[source]:
            escaped_source = escape_dot_text(
                source
            )

            escaped_target = escape_dot_text(
                target
            )

            lines.append(
                f'    "{escaped_source}" -> '
                f'"{escaped_target}";'
            )

    lines.append("}")

    return "\n".join(lines)


def save_graph_png(
    dot_text,
    output_file,
):
    """Render DOT graph to PNG."""
    dot_executable = find_dot()

    try:
        subprocess.run(
            [
                dot_executable,
                "-Tpng",
                "-o",
                output_file,
            ],
            input=dot_text,
            text=True,
            check=True,
            capture_output=True,
        )

    except subprocess.CalledProcessError as error:
        message = error.stderr.strip()

        raise ValueError(
            f"ошибка Graphviz: {message}"
        ) from error


def append_ascii_children(
    graph,
    package_name,
    prefix,
    path,
    lines,
):
    """Append children to ASCII tree."""
    dependencies = graph.get(
        package_name,
        [],
    )

    for index, dependency in enumerate(
        dependencies
    ):
        is_last = (
            index
            == len(dependencies) - 1
        )

        connector = (
            "└── "
            if is_last
            else "├── "
        )

        cycle = dependency in path

        suffix = (
            " [cycle]"
            if cycle
            else ""
        )

        lines.append(
            prefix
            + connector
            + dependency
            + suffix
        )

        if cycle:
            continue

        child_prefix = (
            prefix
            + (
                "    "
                if is_last
                else "│   "
            )
        )

        append_ascii_children(
            graph,
            dependency,
            child_prefix,
            path | {dependency},
            lines,
        )


def graph_to_ascii_tree(
    graph,
    root_package,
):
    """Convert graph to ASCII tree."""
    lines = [
        root_package
    ]

    append_ascii_children(
        graph,
        root_package,
        "",
        {root_package},
        lines,
    )

    return "\n".join(lines)