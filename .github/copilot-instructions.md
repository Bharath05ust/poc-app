# Project Context

- This is a local learning demo using Python 3.11+, FastAPI, and the official MCP Python SDK.
- `app/domain.py` owns bookstore catalog, order, search, and reading-plan operations.
- `app/main.py` serves the browser UI, REST browse/order endpoints, and demonstration MCP host/client routes.
- `app/mcp_server.py` exposes search and reading-plan tools, a catalog resource, and a recommendation prompt over Streamable HTTP on port 8001.
- Run the MCP server on port 8001 and FastAPI on port 8000 as documented in `README.md`.
- Keep the UI dependency-free and preserve its responsive layout and accessible controls.
- Use `py -3.11 -m pytest -q` for the focused test suite.

## References

- Official SDK repository: https://github.com/modelcontextprotocol/python-sdk
- SDK getting started: https://py.sdk.modelcontextprotocol.io/get-started/
- SDK primitives: https://py.sdk.modelcontextprotocol.io/get-started/first-steps/
- SDK transports: https://py.sdk.modelcontextprotocol.io/run/
- SDK client: https://py.sdk.modelcontextprotocol.io/client/
- MCP specification: https://modelcontextprotocol.io/specification/latest