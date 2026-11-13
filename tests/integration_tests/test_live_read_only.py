from __future__ import annotations

import os

import pytest

from langchain_context import (
    ContextListBatches,
    ContextListMonitors,
    ContextScrape,
    ContextSearch,
)

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.getenv("CONTEXT_RUN_LIVE_TESTS") != "1",
        reason="Set CONTEXT_RUN_LIVE_TESTS=1 to run credit-consuming live tests.",
    ),
]


def test_live_search_and_scrape() -> None:
    search = ContextSearch().invoke(
        {
            "query": "Context.dev official documentation",
            "includeDomains": ["docs.context.dev"],
            "numResults": 10,
        }
    )
    scrape = ContextScrape().invoke(
        {
            "url": "https://docs.context.dev/llms.txt",
            "useMainContentOnly": True,
        }
    )

    assert search["results"]
    assert scrape["markdown"]


def test_live_account_reads() -> None:
    monitors = ContextListMonitors().invoke({"limit": 1})
    batches = ContextListBatches().invoke({"limit": 1})

    assert isinstance(monitors["data"], list)
    assert isinstance(batches["data"], list)


@pytest.mark.asyncio
async def test_live_async_search() -> None:
    result = await ContextSearch().ainvoke(
        {
            "query": "Context.dev official documentation",
            "includeDomains": ["docs.context.dev"],
            "numResults": 10,
        }
    )

    assert result["results"]
