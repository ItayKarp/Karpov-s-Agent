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
        "mem0": {
            "command": "npx",
            "args": ["-y", "@mem0/mcp-server"],
            "transport": "stdio",
            "env": {"MEM0_API_KEY": settings.mem0_api_key}
        }
    }