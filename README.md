# Nerdearla MCP Server

An MCP (Model Context Protocol) server that provides information about Nerdearla events, speakers, and sessions. Built with FastMCP and supports streamable HTTP in stateless mode with JSON responses.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. Make sure you have uv installed:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the project dependencies:

```bash
# Clone and navigate to the repository
cd nerdearla-mcp

# Install dependencies with uv
uv sync
```

## Usage

### Running the Server

Start the MCP server:

```bash
# Using uv
uv run nerdearla-mcp

# Or directly with Python
uv run python -m nerdearla_mcp.server
```

The server will start on `http://localhost:8000/mcp` by default.

## Development

### Project Structure

```
nerdearla-mcp/
├── nerdearla_mcp/
│   ├── __init__.py
│   └── server.py          # Main MCP server implementation
├── pyproject.toml         # Project configuration and dependencies
├── README.md              # This file
└── ...
```

### Adding New Tools

To add new tools to the server:

1. Define your tool function in `nerdearla_mcp/server.py`
2. Use the `@mcp.tool()` decorator
3. Add proper type hints and docstrings
4. Implement the tool to retrieve the data from an API, file or database as needed

Example:
```python
@mcp.tool()
def get_sponsors(tier: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get information about event sponsors.
    
    Args:
        tier: Optional filter by sponsor tier (e.g., "Gold", "Silver", "Bronze")
    
    Returns:
        List of sponsor information
    """
    # Implementation here
    pass
```

### Running Tests

```bash
# Run tests with pytest
uv run pytest
```

### Code Formatting

```bash
# Format code with black
uv run black .

# Lint with ruff
uv run ruff check .
```

## Configuration

### Port Configuration

The server runs on port 8000 by default. You can configure the port using environment variables:

**Environment Variable:**
```bash
export PORT=3000
uv run nerdearla-mcp
```

**Using .env file:**
Create a `.env` file in the project root:
```env
PORT=3000
```

**Priority order:**
1. Environment variable `PORT`
2. `.env` file
3. Default: 8000

**Optional: Install dotenv support**
```bash
uv add python-dotenv
```

### Server Configuration

The server uses streamable HTTP transport with the following default settings:
- Host: `0.0.0.0` (accepts connections from any IP)
- Port: as described above
- Path: `/mcp` (API endpoint)
- Transport: `streamable-http`
- Mode: `stateless_http=True`

## Contributing

1. Fork the repository
2. Make your changes
3. Add tests if applicable
4. Run the linter and formatter
5. Submit a pull request

## License

See the LICENSE file for details.
