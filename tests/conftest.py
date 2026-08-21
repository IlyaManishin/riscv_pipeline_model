import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register CLI options for benchmark filtering."""
    parser.addoption(
        "--max-duration-scale",
        action="store",
        type=int,
        default=5,
        help="Maximum allowed test duration_scale rating (1..5)."
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Filter test items during collection based on the duration_scale threshold."""
    max_scale = config.getoption("--max-duration-scale")
    if max_scale is None:
        return

    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []

    for item in items:
        test_config = item.callspec.params.get("test_config") if hasattr(item, "callspec") else None

        # Verify class name by string to handle any module import path
        is_cpu_config = test_config is not None and type(test_config).__name__ == "CpuTestConfig"

        if is_cpu_config and getattr(test_config, "duration_scale", 1) > max_scale:
            deselected.append(item)
        else:
            selected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected