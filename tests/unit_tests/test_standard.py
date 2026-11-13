from __future__ import annotations

from typing import Any, ClassVar

from langchain_tests.unit_tests import ToolsUnitTests

from langchain_context import ContextSearch


class TestContextSearchStandard(ToolsUnitTests):
    tool_constructor = ContextSearch
    tool_constructor_params: ClassVar[dict[str, Any]] = {"api_key": "test-key"}
    tool_invoke_params_example: ClassVar[dict[str, Any]] = {
        "query": "latest Context.dev announcements"
    }
    init_from_env_params = (
        {"CONTEXT_API_KEY": "environment-key"},
        {},
        {},
    )
