# langchain-context

[![CI](https://github.com/context-dot-dev/langchain-context/actions/workflows/test.yml/badge.svg)](https://github.com/context-dot-dev/langchain-context/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/python-3.10--3.14-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/licenses/MIT)

This package contains the LangChain integration for [Context.dev](https://www.context.dev),
an API for turning the live web into reliable data for AI applications. It gives agents
native tools for web search, scraping, crawling, structured extraction, document parsing,
brand intelligence, website monitoring, screenshots, and asynchronous batch jobs.

## Quick install

```bash
pip install -U langchain-context
```

Get an API key from [context.dev](https://www.context.dev) and set it as the
`CONTEXT_API_KEY` environment variable, or pass `api_key=...` to any tool or toolkit.

```bash
export CONTEXT_API_KEY="your-api-key"
```

## Tools

Each Context.dev capability is available as a LangChain `BaseTool`:

```python
from langchain_context import ContextScrape, ContextSearch

search = ContextSearch()
results = search.invoke(
    {
        "query": "latest official Stripe product announcements",
        "includeDomains": ["stripe.com"],
        "numResults": 10,
    }
)

scrape = ContextScrape()
page = scrape.invoke({"url": "https://stripe.com/newsroom"})
```

The most common tools have short aliases:

| Tool | Purpose |
| --- | --- |
| `ContextSearch` | Search the live web |
| `ContextScrape` | Scrape one URL as clean Markdown |
| `ContextCrawl` | Crawl linked pages from a website |
| `ContextSitemap` | Discover or search a site's URLs |
| `ContextExtract` | Extract structured data using a JSON schema |
| `ContextParse` | Parse PDFs and other documents into Markdown |

Dedicated classes are also available for HTML, images, screenshots, style guides,
fonts, company classifications, brand profiles, monitors, and batch jobs.

## Toolkit

Give an agent the complete safe-by-default Context.dev toolkit:

```python
from langchain_context import ContextToolkit

tools = ContextToolkit().get_tools()
```

Or keep the tool list focused:

```python
from langchain_context import (
    ContextBatchToolkit,
    ContextBrandToolkit,
    ContextMonitorToolkit,
    ContextWebToolkit,
)

web_tools = ContextWebToolkit().get_tools()
brand_tools = ContextBrandToolkit().get_tools()
monitor_tools = ContextMonitorToolkit().get_tools()
batch_tools = ContextBatchToolkit().get_tools()
```

Write operations and browser actions are opt-in. Enable them only for agents that
should be allowed to create or modify Context.dev resources or interact with forms
on third-party websites:

```python
tools = ContextToolkit(
    include_write_tools=True,
    allow_browser_actions=True,
).get_tools()
```

All toolkits accept `api_key`, `api_base`, and `timeout`. `api_base` defaults to
`https://api.context.dev/v1` and can also be set with `CONTEXT_API_BASE`.

## Parse documents

`ContextParse` accepts base64-encoded bytes so files remain compatible with
LangChain's JSON tool-call interface:

```python
import base64
from pathlib import Path

from langchain_context import ContextParse

file_bytes = Path("report.pdf").read_bytes()
result = ContextParse().invoke(
    {
        "fileBase64": base64.b64encode(file_bytes).decode("ascii"),
        "fileName": "report.pdf",
    }
)
```

## Async

Every tool supports LangChain's asynchronous interface:

```python
from langchain_context import ContextSearch

result = await ContextSearch().ainvoke(
    {"query": "latest Context.dev product announcements"}
)
```

## Coverage

The package exposes all 33 API-backed tools in Context.dev's public MCP catalog.
The MCP-only `get-brand` visual card is host UI; `ContextBrandRetrieve` returns the
same underlying brand data as structured output for LangChain applications.

## Documentation

- [LangChain integration source](https://github.com/context-dot-dev/langchain-context)
- [Context.dev documentation](https://docs.context.dev)
- [Context.dev API reference](https://docs.context.dev/api-reference)
- [Context.dev homepage](https://www.context.dev)
