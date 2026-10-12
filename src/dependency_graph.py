"""Dependency graph traversal functions."""


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
        if package_name in visited:
            continue

        visited.add(package_name)

        if depth >= max_depth:
            graph.setdefault(
                package_name,
                [],
            )
            continue

        dependencies = dependency_loader(
            package_name
        )

        dependency_names = sorted(
            dependencies.keys()
        )

        graph[package_name] = dependency_names

        for dependency in dependency_names:
            if dependency in visited:
                continue

            if dependency in queued:
                continue

            queued.add(dependency)
            next_level.append(dependency)

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