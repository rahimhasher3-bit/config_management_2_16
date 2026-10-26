
"""Dependency graph traversal functions."""


def get_dependency_names(package_name, dependency_loader):
    """Load and sort dependency names."""
    dependencies = dependency_loader(package_name)
    return sorted(dependencies.keys())


def add_unvisited_dependencies(
    dependency_names,
    visited,
    queued,
    next_level,
):
    """Add new dependencies to the next BFS level."""
    for dependency in dependency_names:
        if dependency in visited or dependency in queued:
            continue

        queued.add(dependency)
        next_level.append(dependency)


def process_package(
    package_name,
    graph,
    dependency_loader,
    max_depth,
    depth,
    visited,
    queued,
    next_level,
):
    """Process one package in the current BFS level."""
    if package_name in visited:
        return

    visited.add(package_name)

    if depth >= max_depth:
        graph.setdefault(package_name, [])
        return

    dependency_names = get_dependency_names(
        package_name,
        dependency_loader,
    )
    graph[package_name] = dependency_names

    add_unvisited_dependencies(
        dependency_names,
        visited,
        queued,
        next_level,
    )


def process_level(
    packages,
    graph,
    dependency_loader,
    max_depth,
    depth,
    visited,
):
    """Process one BFS level."""
    next_level = []
    queued = set()

    for package_name in packages:
        process_package(
            package_name,
            graph,
            dependency_loader,
            max_depth,
            depth,
            visited,
            queued,
            next_level,
        )

    return next_level


def bfs_recursive(
    packages,
    graph,
    dependency_loader,
    max_depth,
    depth,
    visited,
):
    """Build graph using recursive BFS."""
    if not packages:
        return graph

    next_level = process_level(
        packages,
        graph,
        dependency_loader,
        max_depth,
        depth,
        visited,
    )

    return bfs_recursive(
        next_level,
        graph,
        dependency_loader,
        max_depth,
        depth + 1,
        visited,
    )


def build_dependency_graph(
    root_package,
    dependency_loader,
    max_depth,
):
    """Build transitive dependency graph."""
    return bfs_recursive(
        [root_package],
        {},
        dependency_loader,
        max_depth,
        0,
        set(),
    )


def reverse_graph(graph):
    """Reverse all dependency edges."""
    reversed_graph = {
        package_name: []
        for package_name in graph
    }

    for package_name, dependencies in graph.items():
        for dependency in dependencies:
            reversed_graph.setdefault(dependency, [])
            reversed_graph[dependency].append(package_name)

    for dependencies in reversed_graph.values():
        dependencies.sort()

    return reversed_graph


def create_reverse_loader(graph):
    """Create loader for reversed graph."""
    reversed_graph = reverse_graph(graph)

    def loader(package_name):
        dependencies = reversed_graph.get(
            package_name,
            [],
        )
        return {
            dependency: "test"
            for dependency in dependencies
        }

    return loader


def graph_contains_package(
    graph,
    package_name,
):
    """Check whether package exists in graph."""
    if package_name in graph:
        return True

    return any(
        package_name in dependencies
        for dependencies in graph.values()
    )


def build_reverse_dependency_graph(
    package_name,
    graph,
    max_depth,
):
    """Build reverse dependency graph."""
    loader = create_reverse_loader(graph)

    return build_dependency_graph(
        package_name,
        loader,
        max_depth,
    )