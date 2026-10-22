# API vs MCP Field Guide

A small bookstore demo with 12 sample books across four categories that gives REST and MCP different jobs. REST has explicit endpoints to browse/filter the catalog and place an order. MCP exposes discoverable tools to search books by a reader's request and build a reading plan from a learning goal, plus a catalog resource and a recommendation prompt. The MCP path uses the official Python SDK over Streamable HTTP. No LLM is required, so the protocol steps and results stay deterministic.

## Requirements

- Python 3.11 or newer
- Node.js is optional; it is only needed if you want to use MCP Inspector through `mcp dev`

## Run on Windows PowerShell

From this folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start the MCP server in the first terminal:

```powershell
python -m app.mcp_server
```

Start the FastAPI application in a second terminal:

```powershell
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. FastAPI docs are at `http://127.0.0.1:8000/docs`; the standalone MCP server listens at `http://127.0.0.1:8001/mcp`.

## Try it

- Choose **REST API** and browse/filter books or place an order. These call `GET /api/books` and `POST /api/orders`.
- Choose **MCP host** and search for books or build a reading plan. The demo host discovers available tools with `tools/list`, then calls `search_books` or `build_reading_plan` with `tools/call`. The MCP tools fetch the live catalog from the FastAPI API, so order stock changes stay in sync.
- Select **Inspect MCP catalog** to list the server's tools, resource, and prompt, and read its catalog resource.
- Select **Get recommendation prompt** to render the reusable MCP prompt.
- Connect another MCP host to `http://127.0.0.1:8001/mcp` using Streamable HTTP, or run `mcp dev app/mcp_server.py` to inspect it.

## What the comparison means

An API is an interface for software systems to request data or actions. REST often uses resource URLs and HTTP methods. MCP is a standardized protocol between an AI host and MCP servers. It defines capability discovery and primitives such as tools, resources, and prompts. An MCP server may call an API internally; MCP does not replace the API.

In this demo, REST directly addresses a known operation: browse books or submit a checkout request. A successful checkout reduces the in-memory stock count. MCP's host discovers a server's capabilities and can choose a tool based on a goal; it can also read catalog context as a resource or request a reusable prompt. The MCP server calls the REST catalog endpoint, so the resource and tools use the same current stock. An MCP tool is not automatically better than an API endpoint, and MCP does not replace APIs. Here, FastAPI also acts as the demonstration host/client for the MCP server; in an AI product, that role is typically played by the assistant application. The sample catalog and stock reset when the REST server restarts; there is no persistent database.

Example REST checkout request:

```json
{
	"book_id": "b101",
	"quantity": 2
}
```

FastAPI validates the payload, calls `create_order()`, checks stock, subtracts the requested quantity, and returns an order ID, total, and status. For MCP search, the host first calls `tools/list`, then invokes `search_books` with arguments such as `{"query":"Python","category":"Technology"}` and receives matching books as structured content.

## Test

With the virtual environment active:

```powershell
python -m pytest -q
```

## Project map

- `app/domain.py`: bookstore catalog, order, search, and reading-plan operations
- `app/main.py`: FastAPI REST endpoints and demonstration MCP host/client routes
- `app/mcp_server.py`: MCP server tools, catalog resource, and recommendation prompt
- `static/index.html`: interactive comparison and learning UI
- `tests/test_demo.py`: domain, REST, and in-process MCP checks
- `.vscode/mcp.json`: VS Code MCP server configuration

## Official references

- Python SDK repository: https://github.com/modelcontextprotocol/python-sdk
- SDK getting started: https://py.sdk.modelcontextprotocol.io/get-started/
- SDK servers and primitives: https://py.sdk.modelcontextprotocol.io/get-started/first-steps/
- SDK running server transports: https://py.sdk.modelcontextprotocol.io/run/
- SDK client: https://py.sdk.modelcontextprotocol.io/client/
- MCP specification: https://modelcontextprotocol.io/specification/latest