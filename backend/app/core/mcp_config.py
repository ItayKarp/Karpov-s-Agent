from app.core.config import settings

def get_mcp_config():
    return {
        "fetch": {
            "command": "uvx",
            "args": ["mcp-server-fetch"],
            "transport": "stdio"
        },
        "arxiv": {
            "command": "uv",
            "args": ["tool", "run", "arxiv-mcp-server"],
            "transport": "stdio"
        },
    }