from __future__ import annotations

from typing import Any, Literal

from langchain_core.tools import BaseTool, BaseToolkit
from pydantic import ConfigDict, Field, SecretStr

from langchain_context._client import DEFAULT_TIMEOUT_SECONDS, ContextClient
from langchain_context._spec import schema_without_properties
from langchain_context.tools import CONTEXT_TOOL_TYPES_BY_ENDPOINT

WEB_ENDPOINTS = (
    "parse-document",
    "web-search",
    "web-scrape-html",
    "web-scrape-markdown",
    "web-scrape-images",
    "web-scrape-sitemap",
    "web-crawl",
    "web-extract",
    "web-screenshot",
)
BRAND_ENDPOINTS = (
    "brand-retrieve-unified",
    "web-styleguide",
    "web-fonts",
    "web-naics",
    "web-sic",
)
MONITOR_READ_ENDPOINTS = (
    "list-monitors",
    "get-monitor",
    "list-monitor-runs",
    "get-monitor-run",
    "list-monitor-changes",
    "list-account-runs",
    "list-monitor-credit-usage",
    "list-changes",
    "get-change",
)
MONITOR_WRITE_ENDPOINTS = (
    "create-monitor",
    "update-monitor",
    "delete-monitor",
    "run-monitor-now",
)
BATCH_READ_ENDPOINTS = (
    "list-batches",
    "get-batch",
    "get-batch-results",
)
BATCH_WRITE_ENDPOINTS = (
    "submit-batch",
    "cancel-batch",
    "delete-batch",
)
ACTION_ENDPOINTS = {
    "web-scrape-html",
    "web-scrape-markdown",
    "web-scrape-images",
}


class _ContextToolkitBase(BaseToolkit):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    api_key: SecretStr | str | None = Field(default=None, exclude=True, repr=False)
    api_base: str | None = Field(default=None, exclude=True)
    timeout: float = Field(default=DEFAULT_TIMEOUT_SECONDS, gt=0, exclude=True)
    context_client: ContextClient | None = Field(default=None, exclude=True, repr=False)

    def _tool(self, endpoint_name: str, *, allow_browser_actions: bool = True) -> BaseTool:
        tool_type = CONTEXT_TOOL_TYPES_BY_ENDPOINT[endpoint_name]
        kwargs: dict[str, Any] = {
            "api_key": self.api_key,
            "api_base": self.api_base,
            "timeout": self.timeout,
            "context_client": self.context_client,
        }
        if endpoint_name not in ACTION_ENDPOINTS or allow_browser_actions:
            return tool_type(**kwargs)

        args_schema = schema_without_properties(
            tool_type.model_fields["args_schema"].default,
            {"actions"},
        )
        metadata = {**tool_type.model_fields["metadata"].default}
        metadata.update({"read_only": True, "destructive": False, "browser_actions": False})
        return tool_type(
            **kwargs,
            args_schema=args_schema,
            metadata=metadata,
            description=(
                f"{tool_type.model_fields['description'].default} "
                "This toolkit instance does not expose browser actions."
            ),
        )

    def _tools(
        self,
        endpoint_names: tuple[str, ...],
        *,
        allow_browser_actions: bool = True,
    ) -> list[BaseTool]:
        return [
            self._tool(endpoint_name, allow_browser_actions=allow_browser_actions)
            for endpoint_name in endpoint_names
        ]


class ContextWebToolkit(_ContextToolkitBase):
    """LangChain tools for web search, scraping, crawling, extraction, and parsing."""

    allow_browser_actions: bool = False

    def get_tools(self) -> list[BaseTool]:
        """Return Context.dev web tools."""
        return self._tools(WEB_ENDPOINTS, allow_browser_actions=self.allow_browser_actions)


class ContextBrandToolkit(_ContextToolkitBase):
    """LangChain tools for brand intelligence, styles, fonts, and classifications."""

    def get_tools(self) -> list[BaseTool]:
        """Return Context.dev brand tools."""
        return self._tools(BRAND_ENDPOINTS)


class ContextMonitorToolkit(_ContextToolkitBase):
    """LangChain tools for reading and optionally managing website monitors."""

    include_write_tools: bool = False

    def get_tools(self) -> list[BaseTool]:
        """Return monitor tools, with mutating tools included only when requested."""
        endpoint_names: tuple[str, ...] = MONITOR_READ_ENDPOINTS
        if self.include_write_tools:
            endpoint_names += MONITOR_WRITE_ENDPOINTS
        return self._tools(endpoint_names)


class ContextBatchToolkit(_ContextToolkitBase):
    """LangChain tools for reading and optionally managing asynchronous batches."""

    include_write_tools: bool = False

    def get_tools(self) -> list[BaseTool]:
        """Return batch tools, with mutating tools included only when requested."""
        endpoint_names: tuple[str, ...] = BATCH_READ_ENDPOINTS
        if self.include_write_tools:
            endpoint_names += BATCH_WRITE_ENDPOINTS
        return self._tools(endpoint_names)


class ContextToolkit(_ContextToolkitBase):
    """Combined Context.dev toolkit spanning every public API capability."""

    groups: tuple[Literal["web", "brand", "monitors", "batches"], ...] = (
        "web",
        "brand",
        "monitors",
        "batches",
    )
    include_write_tools: bool = False
    allow_browser_actions: bool = False

    def get_tools(self) -> list[BaseTool]:
        """Return the selected Context.dev tool groups."""
        endpoint_names: list[str] = []
        if "web" in self.groups:
            endpoint_names.extend(WEB_ENDPOINTS)
        if "brand" in self.groups:
            endpoint_names.extend(BRAND_ENDPOINTS)
        if "monitors" in self.groups:
            endpoint_names.extend(MONITOR_READ_ENDPOINTS)
            if self.include_write_tools:
                endpoint_names.extend(MONITOR_WRITE_ENDPOINTS)
        if "batches" in self.groups:
            endpoint_names.extend(BATCH_READ_ENDPOINTS)
            if self.include_write_tools:
                endpoint_names.extend(BATCH_WRITE_ENDPOINTS)
        return [
            self._tool(
                endpoint_name,
                allow_browser_actions=self.allow_browser_actions,
            )
            for endpoint_name in dict.fromkeys(endpoint_names)
        ]
