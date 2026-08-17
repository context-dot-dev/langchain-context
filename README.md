# Context.dev for LangChain

Use Context.dev's live web search, scraping, crawling, structured extraction,
document parsing, brand intelligence, monitors, screenshots, and asynchronous
batches as native LangChain tools.

## Installation

```bash
pip install -U langchain-context
```

Set a Context.dev API key:

```bash
export CONTEXT_API_KEY="your-api-key"
```

## Quick start

Choose individual tools when you know exactly what an agent needs:

```python
from langchain_context import ContextScrape, ContextSearch

tools = [ContextSearch(), ContextScrape()]

results = tools[0].invoke(
    {
        "query": "latest official Stripe product announcements",
        "includeDomains": ["stripe.com"],
        "numResults": 10,
    }
)
```

Or load the combined toolkit:

```python
from langchain_context import ContextToolkit

tools = ContextToolkit().get_tools()
```

The combined toolkit includes all public Context.dev capability groups. By
default, it omits monitor and batch mutations and removes browser actions from
the page-scraping tools. Enable those capabilities only for agents that should
be allowed to change Context.dev or third-party state:

```python
tools = ContextToolkit(
    include_write_tools=True,
    allow_browser_actions=True,
).get_tools()
```

## Focused toolkits

Use smaller toolkits to reduce tool-selection noise:

```python
from langchain_context import (
    ContextBatchToolkit,
    ContextBrandToolkit,
    ContextMonitorToolkit,
    ContextWebToolkit,
)

web_tools = ContextWebToolkit().get_tools()
brand_tools = ContextBrandToolkit().get_tools()
monitor_read_tools = ContextMonitorToolkit().get_tools()
batch_read_tools = ContextBatchToolkit().get_tools()

monitor_tools = ContextMonitorToolkit(include_write_tools=True).get_tools()
batch_tools = ContextBatchToolkit(include_write_tools=True).get_tools()
```

The toolkits accept `api_key`, `api_base`, and `timeout`. `api_key` defaults to
`CONTEXT_API_KEY`; `api_base` defaults to `https://api.context.dev/v1` and can
also be set with `CONTEXT_API_BASE`.

## Core tools

The most common tools have concise aliases:

| Alias | Tool | Purpose |
| --- | --- | --- |
| `ContextSearch` | `ContextWebSearch` | Search the live web |
| `ContextScrape` | `ContextWebScrapeMarkdown` | Read one URL as Markdown |
| `ContextCrawl` | `ContextWebCrawl` | Crawl several linked pages |
| `ContextSitemap` | `ContextWebScrapeSitemap` | Discover or search site URLs |
| `ContextExtract` | `ContextWebExtract` | Extract structured JSON |
| `ContextParse` | `ContextParseDocument` | Parse files to Markdown |

Every public endpoint is also available as a dedicated tool class, including
HTML and image scraping, screenshots, style guides, fonts, NAICS and SIC
classification, monitor lifecycle and change history, and batch lifecycle and
results.

The package covers all 33 API-backed tools in the current public Context.dev
MCP catalog. The MCP-only `get-brand` visual card is host UI rather than an API
operation; `ContextBrandRetrieve` exposes the same underlying brand data as
structured output for LangChain applications.

## Parse a document

`ContextParse` accepts base64-encoded file bytes so it remains compatible with
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

## Async use

All tools support LangChain's asynchronous interface:

```python
from langchain_context import ContextSearch

result = await ContextSearch().ainvoke({"query": "Context.dev documentation"})
```

## Tool selection and safety

- Prefer `ContextSearch` when the source URL is unknown.
- Prefer `ContextScrape` for one known page and `ContextCrawl` for a small site section.
- Prefer `ContextSitemap` when an agent needs URL discovery without page content.
- Prefer `ContextExtract` when the output must conform to a JSON schema.
- Prefer batches for large asynchronous jobs.
- Keep `include_write_tools=False` unless an agent should create, update, run,
  cancel, or delete resources.
- Keep `allow_browser_actions=False` unless an agent should interact with
  third-party pages. Browser actions can submit forms or otherwise change
  external state.

## Links

- [Context.dev documentation](https://docs.context.dev)
- [API reference](https://docs.context.dev/api-reference)
- [Context.dev](https://www.context.dev)
