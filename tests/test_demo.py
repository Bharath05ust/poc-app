import anyio
from fastapi.testclient import TestClient
from mcp import Client

from app.domain import create_reading_plan, list_books, place_order
from app.main import app
from app.mcp_server import mcp


def test_domain_browses_books_and_places_orders() -> None:
    assert len(list_books(category="Technology")) == 6
    assert len(list_books()) == 12
    stock_before = list_books(query="API Handbook")[0].stock
    receipt = place_order("b101", 2)
    assert receipt.title == "The API Handbook"
    assert receipt.total == 57.0
    assert list_books(query="API Handbook")[0].stock == stock_before - 2
    assert len(create_reading_plan("learn API development", list_books()).steps) == 3


def test_rest_api_browses_catalog_and_places_order() -> None:
    client = TestClient(app)
    books = client.get("/api/books", params={"category": "Technology"})
    order = client.post("/api/orders", json={"book_id": "b101", "quantity": 2})

    assert books.status_code == 200
    assert len(books.json()) == 6
    assert order.status_code == 200
    assert order.json()["total"] == 57.0


def test_mcp_server_exposes_bookstore_tool_resource_and_prompt() -> None:
    async def inspect_server() -> None:
        async with Client(mcp) as client:
            tools = await client.list_tools()
            resources = await client.list_resources()
            prompts = await client.list_prompts()

        tool_names = {tool.name for tool in tools.tools}
        assert "search_books" in tool_names
        assert "build_reading_plan" in tool_names
        assert any(str(resource.uri) == "bookstore://catalog" for resource in resources.resources)
        assert any(prompt.name == "book_recommendation" for prompt in prompts.prompts)

    anyio.run(inspect_server)


def test_order_rejects_unknown_book() -> None:
    try:
        place_order("missing", 1)
    except ValueError as error:
        assert "No book found" in str(error)
    else:
        raise AssertionError("Expected an unknown book to be rejected")