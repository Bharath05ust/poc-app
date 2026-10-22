import json
import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from mcp import Client
from pydantic import BaseModel, Field

from app.domain import Book, OrderReceipt, ReadingPlan, list_books, place_order


ROOT = Path(__file__).resolve().parent.parent
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8001/mcp")

app = FastAPI(
    title="API vs MCP Learning Demo",
    description="REST browse/order operations and discoverable MCP bookstore capabilities.",
    version="1.0.0",
)
logger = logging.getLogger(__name__)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class OrderRequest(BaseModel):
    book_id: str = Field(min_length=1, max_length=20)
    quantity: int = Field(ge=1, le=10)


class McpSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=100)
    category: str = Field(default="", max_length=40)


class ReadingPlanRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=200)


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/books", response_model=list[Book], tags=["REST API"])
def browse_books(
    query: str = Query(default="", max_length=100),
    category: str | None = Query(default=None, max_length=40),
) -> list[Book]:
    """Browse or filter the bookstore catalog over a direct REST endpoint."""
    return list_books(query=query, category=category)


@app.post("/api/orders", response_model=OrderReceipt, tags=["REST API"])
def create_order(request: OrderRequest) -> OrderReceipt:
    """Place a bookstore order and return a checkout confirmation."""
    try:
        return place_order(request.book_id, request.quantity)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


async def call_mcp_tool(tool_name: str, arguments: dict[str, str]) -> dict[str, object]:
    try:
        async with Client(MCP_SERVER_URL) as client:
            tools = await client.list_tools()
            if not any(tool.name == tool_name for tool in tools.tools):
                raise HTTPException(status_code=502, detail=f"MCP server does not expose {tool_name!r}.")
            result = await client.call_tool(tool_name, arguments)
            server_name = client.server_info.name if client.server_info else "Unknown MCP server"
        if result.is_error:
            message = next(
                (block.text for block in result.content if hasattr(block, "text")),
                "The MCP tool returned an error.",
            )
            raise HTTPException(status_code=502, detail=message)
        if not result.structured_content:
            raise HTTPException(status_code=502, detail="The MCP tool returned no structured content.")
        return {
            "server": server_name,
            "discovered_tool": tool_name,
            "result": result.structured_content,
        }
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("MCP tool request failed")
        raise HTTPException(
            status_code=503,
            detail=f"Could not reach the MCP server at {MCP_SERVER_URL}. Start it using the README instructions.",
        ) from error


@app.post("/api/demo/mcp/search", tags=["MCP demonstration"])
async def search_via_mcp(request: McpSearchRequest) -> dict[str, object]:
    """Discoverable MCP search action, invoked by the demo host/client."""
    result = await call_mcp_tool(
        "search_books", {"query": request.query, "category": request.category}
    )
    return {"tool": "search_books", "protocol_method": "tools/call", **result}


@app.post("/api/demo/mcp/plan", tags=["MCP demonstration"])
async def plan_via_mcp(request: ReadingPlanRequest) -> dict[str, object]:
    """Ask the MCP server's tool to assemble a reading plan from a goal."""
    result = await call_mcp_tool("build_reading_plan", {"goal": request.goal})
    return {"tool": "build_reading_plan", "protocol_method": "tools/call", **result}


@app.get("/api/demo/mcp/catalog", tags=["MCP demonstration"])
async def inspect_mcp_catalog() -> dict[str, object]:
    """Discover MCP capabilities and read the bookstore catalog resource."""
    try:
        async with Client(MCP_SERVER_URL) as client:
            tools = await client.list_tools()
            resources = await client.list_resources()
            prompts = await client.list_prompts()
            resource_contents = await client.read_resource("bookstore://catalog")

        catalog_data = next(
            (content.text for content in resource_contents.contents if hasattr(content, "text")),
            "[]",
        )
        return {
            "tools": [{"name": tool.name, "description": tool.description} for tool in tools.tools],
            "resources": [str(resource.uri) for resource in resources.resources],
            "resource_data": json.loads(catalog_data),
            "prompts": [{"name": prompt.name, "description": prompt.description} for prompt in prompts.prompts],
        }
    except Exception as error:
        raise HTTPException(status_code=503, detail="Could not inspect the MCP server.") from error


@app.post("/api/demo/mcp/prompt", tags=["MCP demonstration"])
async def render_mcp_prompt(request: ReadingPlanRequest) -> dict[str, str]:
    """Render the reusable book recommendation prompt through MCP."""
    try:
        async with Client(MCP_SERVER_URL) as client:
            result = await client.get_prompt("book_recommendation", {"goal": request.goal})
        message = next(
            (item.content.text for item in result.messages if hasattr(item.content, "text")),
            "The MCP server returned an empty prompt.",
        )
        return {"name": "book_recommendation", "message": message}
    except Exception as error:
        raise HTTPException(status_code=503, detail="Could not render the MCP prompt.") from error