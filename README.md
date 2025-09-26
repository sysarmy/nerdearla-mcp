# Nerdearla MCP Server

🚀 **Live Server**: The server is running at https://mcp.nerdear.la/mcp

An MCP (Model Context Protocol) server that provides information about Nerdearla events, speakers, and sessions. Built with FastMCP and supports streamable HTTP in stateless mode with JSON responses.

## Quick Start - Add to VS Code Copilot

To use this MCP server with VS Code Copilot:

1. Open the command palette in VS Code (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Type "MCP: Add Server" and select it
3. Select "HTTP" as the server type
4. Enter the server URL: `https://mcp.nerdear.la/mcp`
5. Give it a name, any name is fine
6. Select if you want to save it in your user or workspace settings

You can now ask Copilot about Nerdearla events, speakers, and sessions!


## Add to Cursor IDE 

To use this MCP server with Cursor:

1. Open the command palette in Cursor (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Type "Open MCP settings" and select it
3. Click on "New MCP Server" + icon.
4. Paste the following configuration
```
{
  "mcpServers": {
    "nerdearla": {
      "name": "nerdearla",
      "version": "1.0",
      "description": "Nerdearla is a tool that helps you find information about the nerdear.la community.",
      "url": "https://mcp.nerdear.la/mcp",
      "command": "npx",
      "env:{},
    }
  }
}
```
You can use cursor chat to ask about Nerdearla events, speakers, and sessions!




## Quick Start - Add to your favourite Agent/IDE

Most Agents/IDEs support MCP servers out of the box. Check your documentation for instructions on how to add a new server.

## Local Developtment Setup

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

#### Pre-commit Hooks (Recommended)

This project uses pre-commit hooks to automatically format and lint code before commits:

**Install pre-commit hooks:**
```bash
# Install dependencies (includes pre-commit)
uv sync

# Install the git hooks
uv run pre-commit install
```

**Usage:**
- Hooks run automatically on `git commit`
- To run manually on all files: `uv run pre-commit run --all-files`
- To skip hooks for a commit: `git commit --no-verify`

The hooks will automatically:
- Format code with Black
- Lint and fix issues with Ruff
- Format code with Ruff formatter

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
