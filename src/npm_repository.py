"""Work with npm repository metadata."""

import json
from json import JSONDecodeError
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


REQUEST_TIMEOUT = 10


def build_package_url(repository, package_name):
    """Build URL for npm package metadata."""
    encoded_name = quote(
        package_name,
        safe="@",
    )

    return (
        f"{repository.rstrip('/')}/"
        f"{encoded_name}"
    )


def fetch_package_metadata(
    repository,
    package_name,
):
    """Download npm package metadata."""
    url = build_package_url(
        repository,
        package_name,
    )

    request = Request(
        url,
        headers={
            "User-Agent": "dependency-graph-visualizer"
        },
    )

    try:
        with urlopen(
            request,
            timeout=REQUEST_TIMEOUT,
        ) as response:
            text = response.read().decode(
                "utf-8"
            )

    except HTTPError as error:
        raise ValueError(
            f"пакет не найден: {package_name}"
        ) from error

    except URLError as error:
        raise ValueError(
            "не удалось подключиться "
            "к репозиторию"
        ) from error

    try:
        return json.loads(text)

    except JSONDecodeError as error:
        raise ValueError(
            "репозиторий вернул "
            "некорректный JSON"
        ) from error


def get_latest_version(metadata):
    """Return the latest package version."""
    dist_tags = metadata.get(
        "dist-tags",
        {},
    )

    version = dist_tags.get("latest")

    if not version:
        raise ValueError(
            "не найдена latest-версия пакета"
        )

    return version


def get_direct_dependencies(metadata):
    """Return dependencies of latest version."""
    version = get_latest_version(
        metadata
    )

    versions = metadata.get(
        "versions",
        {},
    )

    package_data = versions.get(
        version
    )

    if not isinstance(
        package_data,
        dict,
    ):
        raise ValueError(
            "данные версии пакета не найдены"
        )

    dependencies = package_data.get(
        "dependencies",
        {},
    )

    if not isinstance(
        dependencies,
        dict,
    ):
        return {}

    return dict(
        sorted(dependencies.items())
    )


def load_direct_dependencies(
    repository,
    package_name,
):
    """Download and return direct dependencies."""
    metadata = fetch_package_metadata(
        repository,
        package_name,
    )

    return get_direct_dependencies(
        metadata
    )