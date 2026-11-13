from __future__ import annotations

from langchain_context import (
    ContextBatchToolkit,
    ContextBrandToolkit,
    ContextMonitorToolkit,
    ContextToolkit,
    ContextWebToolkit,
)
from langchain_context._spec import endpoint_registry


def _endpoint_names(toolkit: object) -> set[str]:
    return {
        tool.endpoint_name
        for tool in toolkit.get_tools()  # type: ignore[attr-defined]
    }


def test_combined_toolkit_defaults_to_every_safe_capability() -> None:
    toolkit = ContextToolkit(api_key="test")
    tools = toolkit.get_tools()

    assert len(tools) == 26
    assert "create-monitor" not in _endpoint_names(toolkit)
    assert "submit-batch" not in _endpoint_names(toolkit)
    for tool in tools:
        if tool.endpoint_name in {
            "web-scrape-html",
            "web-scrape-markdown",
            "web-scrape-images",
        }:
            assert "actions" not in tool.args
            assert tool.metadata["read_only"] is True
            assert tool.metadata["destructive"] is False


def test_combined_toolkit_can_expose_the_complete_public_catalog() -> None:
    toolkit = ContextToolkit(
        api_key="test",
        include_write_tools=True,
        allow_browser_actions=True,
    )
    tools = toolkit.get_tools()

    assert len(tools) == 33
    assert _endpoint_names(toolkit) == set(endpoint_registry().endpoints)
    assert (
        "actions"
        in next(tool for tool in tools if tool.endpoint_name == "web-scrape-markdown").args
    )


def test_focused_toolkit_counts_and_write_opt_in() -> None:
    assert len(ContextWebToolkit(api_key="test").get_tools()) == 9
    assert len(ContextBrandToolkit(api_key="test").get_tools()) == 5
    assert len(ContextMonitorToolkit(api_key="test").get_tools()) == 9
    assert len(ContextMonitorToolkit(api_key="test", include_write_tools=True).get_tools()) == 13
    assert len(ContextBatchToolkit(api_key="test").get_tools()) == 3
    assert len(ContextBatchToolkit(api_key="test", include_write_tools=True).get_tools()) == 6


def test_combined_toolkit_can_select_groups_without_duplicates() -> None:
    toolkit = ContextToolkit(api_key="test", groups=("web", "web", "brand"))

    assert len(toolkit.get_tools()) == 14
    assert len(_endpoint_names(toolkit)) == 14
