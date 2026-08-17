from __future__ import annotations

from typing import Any, ClassVar

from langchain_context._tool import ContextEndpointTool, endpoint_tool_fields


class ContextParseDocument(ContextEndpointTool):
    """Parse a PDF, Office document, image, or other supported file to Markdown."""

    endpoint_name: ClassVar[str] = "parse-document"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebScrapeHtml(ContextEndpointTool):
    """Scrape raw HTML from a web page."""

    endpoint_name: ClassVar[str] = "web-scrape-html"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebScrapeMarkdown(ContextEndpointTool):
    """Scrape a web page into clean Markdown."""

    endpoint_name: ClassVar[str] = "web-scrape-markdown"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebScrapeImages(ContextEndpointTool):
    """Find useful images on a web page."""

    endpoint_name: ClassVar[str] = "web-scrape-images"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebScrapeSitemap(ContextEndpointTool):
    """Discover and optionally search URLs from a website sitemap."""

    endpoint_name: ClassVar[str] = "web-scrape-sitemap"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebCrawl(ContextEndpointTool):
    """Crawl several linked pages from a website."""

    endpoint_name: ClassVar[str] = "web-crawl"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebExtract(ContextEndpointTool):
    """Extract structured data from one or more web pages."""

    endpoint_name: ClassVar[str] = "web-extract"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebSearch(ContextEndpointTool):
    """Search the live web with optional structured extraction."""

    endpoint_name: ClassVar[str] = "web-search"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextBrandRetrieve(ContextEndpointTool):
    """Retrieve a company's brand identity and intelligence."""

    endpoint_name: ClassVar[str] = "brand-retrieve-unified"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebStyleguide(ContextEndpointTool):
    """Extract a website's visual style guide."""

    endpoint_name: ClassVar[str] = "web-styleguide"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebFonts(ContextEndpointTool):
    """Inspect fonts used by a website."""

    endpoint_name: ClassVar[str] = "web-fonts"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebScreenshot(ContextEndpointTool):
    """Capture a website screenshot."""

    endpoint_name: ClassVar[str] = "web-screenshot"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebNaics(ContextEndpointTool):
    """Classify a company using NAICS codes."""

    endpoint_name: ClassVar[str] = "web-naics"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextWebSic(ContextEndpointTool):
    """Classify a company using SIC codes."""

    endpoint_name: ClassVar[str] = "web-sic"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextListMonitors(ContextEndpointTool):
    """List monitors in the Context.dev account."""

    endpoint_name: ClassVar[str] = "list-monitors"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextCreateMonitor(ContextEndpointTool):
    """Create a recurring website monitor."""

    endpoint_name: ClassVar[str] = "create-monitor"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextGetMonitor(ContextEndpointTool):
    """Get a monitor's configuration."""

    endpoint_name: ClassVar[str] = "get-monitor"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextUpdateMonitor(ContextEndpointTool):
    """Update a monitor's configuration."""

    endpoint_name: ClassVar[str] = "update-monitor"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextDeleteMonitor(ContextEndpointTool):
    """Delete a monitor."""

    endpoint_name: ClassVar[str] = "delete-monitor"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextListMonitorRuns(ContextEndpointTool):
    """List runs for a monitor."""

    endpoint_name: ClassVar[str] = "list-monitor-runs"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextListMonitorChanges(ContextEndpointTool):
    """List detected changes for a monitor."""

    endpoint_name: ClassVar[str] = "list-monitor-changes"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextListAccountRuns(ContextEndpointTool):
    """List monitor runs across an account."""

    endpoint_name: ClassVar[str] = "list-account-runs"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextListMonitorCreditUsage(ContextEndpointTool):
    """Get monitor credit usage for an account."""

    endpoint_name: ClassVar[str] = "list-monitor-credit-usage"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextListChanges(ContextEndpointTool):
    """List detected monitor changes across an account."""

    endpoint_name: ClassVar[str] = "list-changes"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextGetChange(ContextEndpointTool):
    """Get one detected monitor change."""

    endpoint_name: ClassVar[str] = "get-change"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextRunMonitorNow(ContextEndpointTool):
    """Run a monitor immediately."""

    endpoint_name: ClassVar[str] = "run-monitor-now"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextSubmitBatch(ContextEndpointTool):
    """Submit a large asynchronous scraping batch."""

    endpoint_name: ClassVar[str] = "submit-batch"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextListBatches(ContextEndpointTool):
    """List asynchronous scraping batches."""

    endpoint_name: ClassVar[str] = "list-batches"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextGetBatch(ContextEndpointTool):
    """Get the status of an asynchronous scraping batch."""

    endpoint_name: ClassVar[str] = "get-batch"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextDeleteBatch(ContextEndpointTool):
    """Delete an asynchronous scraping batch."""

    endpoint_name: ClassVar[str] = "delete-batch"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextGetBatchResults(ContextEndpointTool):
    """Get result pages from a completed scraping batch."""

    endpoint_name: ClassVar[str] = "get-batch-results"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextCancelBatch(ContextEndpointTool):
    """Cancel an asynchronous scraping batch."""

    endpoint_name: ClassVar[str] = "cancel-batch"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


class ContextGetMonitorRun(ContextEndpointTool):
    """Get one monitor run."""

    endpoint_name: ClassVar[str] = "get-monitor-run"
    name: str = endpoint_tool_fields(endpoint_name)["name"]
    description: str = endpoint_tool_fields(endpoint_name)["description"]
    args_schema: dict[str, Any] = endpoint_tool_fields(endpoint_name)["args_schema"]
    tags: list[str] = endpoint_tool_fields(endpoint_name)["tags"]
    metadata: dict[str, Any] = endpoint_tool_fields(endpoint_name)["metadata"]


ContextSearch = ContextWebSearch
ContextScrape = ContextWebScrapeMarkdown
ContextCrawl = ContextWebCrawl
ContextSitemap = ContextWebScrapeSitemap
ContextExtract = ContextWebExtract
ContextParse = ContextParseDocument

ALL_CONTEXT_TOOL_TYPES: tuple[type[ContextEndpointTool], ...] = (
    ContextParseDocument,
    ContextWebScrapeHtml,
    ContextWebScrapeMarkdown,
    ContextWebScrapeImages,
    ContextWebScrapeSitemap,
    ContextWebCrawl,
    ContextWebExtract,
    ContextWebSearch,
    ContextBrandRetrieve,
    ContextWebStyleguide,
    ContextWebFonts,
    ContextWebScreenshot,
    ContextWebNaics,
    ContextWebSic,
    ContextListMonitors,
    ContextCreateMonitor,
    ContextGetMonitor,
    ContextUpdateMonitor,
    ContextDeleteMonitor,
    ContextListMonitorRuns,
    ContextListMonitorChanges,
    ContextListAccountRuns,
    ContextListMonitorCreditUsage,
    ContextListChanges,
    ContextGetChange,
    ContextRunMonitorNow,
    ContextSubmitBatch,
    ContextListBatches,
    ContextGetBatch,
    ContextDeleteBatch,
    ContextGetBatchResults,
    ContextCancelBatch,
    ContextGetMonitorRun,
)

CONTEXT_TOOL_TYPES_BY_ENDPOINT = {
    tool_type.endpoint_name: tool_type for tool_type in ALL_CONTEXT_TOOL_TYPES
}
