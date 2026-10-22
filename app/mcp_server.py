import json
import os

import httpx
from mcp.server import MCPServer

from app.domain import Book, BookSearchResult, ReadingPlan, create_reading_plan


BOOKSTORE_API_URL = os.getenv("BOOKSTORE_API_URL", "http://127.0.0.1:8000")


mcp = MCPServer(
    "bookstore-mcp-server",
    instructions="Use the bookstore API data to search books, build goal-based reading plans, and provide catalog context.",
)


async def fetch_books(query: str = "", category: str = "") -> list[Book]:
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(
            f"{BOOKSTORE_API_URL}/api/books",
            params={"query": query, "category": category},
        )
    response.raise_for_status()
    return [Book.model_validate(item) for item in response.json()]


@mcp.tool(title="Search the bookstore")
async def search_books(query: str, category: str = "") -> BookSearchResult:
    """Find matching books by asking the bookstore API for title, category, or description matches."""
    books = await fetch_books(query=query, category=category)
    return BookSearchResult(query=query, total=len(books), books=books)


@mcp.tool(title="Build a reading plan")
async def build_reading_plan(goal: str) -> ReadingPlan:
    """Use current bookstore API data to choose books that fit a reader's learning goal."""
    books = await fetch_books()
    return create_reading_plan(goal, books)


@mcp.resource("bookstore://catalog")
async def catalog() -> str:
    """Read the current bookstore catalog, prices, and stock counts."""
    books = await fetch_books()
    return json.dumps([book.model_dump() for book in books], indent=2)


@mcp.prompt(title="Recommend books for a goal")
def book_recommendation(goal: str) -> str:
    """Create a reusable instruction for recommending books for a goal."""
    return f"Recommend a short reading path for this goal: {goal}. Use the bookstore catalog and explain the order."


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8001)