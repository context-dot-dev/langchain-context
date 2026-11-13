from __future__ import annotations

from typing import Any, ClassVar

from langchain_core.callbacks import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import ConfigDict, Field, SecretStr

from langchain_context._client import DEFAULT_TIMEOUT_SECONDS, ContextClient
from langchain_context._spec import endpoint_spec, tool_input_schema

TOOL_NAME_REPLACEMENTS = {
    "get-batch-results": "context_get_batch_results",
    "web-scrape-markdown": "context_web_scrape_markdown",
    "web-scrape-sitemap": "context_web_scrape_sitemap",
    "brand-retrieve-unified": "context_brand_retrieve_unified",
    "submit-batch": "context_submit_batch",
    "web-screenshot": "context_web_screenshot",
    "web-styleguide": "context_web_styleguide",
    "web-search": "context_web_search",
    "web-crawl": "context_web_crawl",
    "get-batch": "context_get_batch",
}


def _tool_description(endpoint_name: str, description: str) -> str:
    if endpoint_name == "brand-retrieve-unified":
        return (
            "Retrieve machine-readable company and brand intelligence—logos, colors, "
            "descriptions, socials, links, industry, location, and more—from one domain, "
            "company name, work email, stock ticker, ISIN, transaction descriptor, or direct "
            "URL. Returns raw structured data suitable for analysis and application use."
        )
    result = description
    for source_name, tool_name in TOOL_NAME_REPLACEMENTS.items():
        result = result.replace(source_name, tool_name)
    return result


class ContextEndpointTool(BaseTool):
    """Base class for a LangChain tool backed by one Context.dev endpoint."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    endpoint_name: ClassVar[str]
    api_key: SecretStr | str | None = Field(default=None, exclude=True, repr=False)
    api_base: str | None = Field(default=None, exclude=True)
    timeout: float = Field(default=DEFAULT_TIMEOUT_SECONDS, gt=0, exclude=True)
    context_client: ContextClient | None = Field(default=None, exclude=True, repr=False)

    def _context_client(self) -> ContextClient:
        if self.context_client is not None:
            return self.context_client
        return ContextClient.create(
            api_key=self.api_key,
            api_base=self.api_base,
            timeout=self.timeout,
        )

    def _run(
        self,
        *,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs: Any,
    ) -> Any:
        del run_manager
        return self._context_client().request(endpoint_spec(self.endpoint_name), kwargs)

    async def _arun(
        self,
        *,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
        **kwargs: Any,
    ) -> Any:
        del run_manager
        return await self._context_client().arequest(endpoint_spec(self.endpoint_name), kwargs)


def endpoint_tool_fields(endpoint_name: str) -> dict[str, Any]:
    """Return the LangChain-facing fields shared by an endpoint tool."""
    endpoint = endpoint_spec(endpoint_name)
    return {
        "name": f"context_{endpoint_name.replace('-', '_')}",
        "description": _tool_description(endpoint_name, endpoint.description),
        "args_schema": tool_input_schema(endpoint_name),
        "tags": ["context-dev", endpoint_name],
        "metadata": {
            "context_endpoint": endpoint_name,
            "read_only": endpoint.annotations.read_only,
            "destructive": endpoint.annotations.destructive,
            "open_world": endpoint.annotations.open_world,
        },
    }
