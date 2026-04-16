from langchain_core.tools import BaseTool


_registry: dict[str, BaseTool] = {}

def register_tools(tools: list[BaseTool]) -> None:
    for tool in tools:
        _registry[tool.name] = tool

def get_tools(names: list[str]) -> list[BaseTool]:
    return [_registry[n] for n in names if n in _registry]

def get_all_tools() -> list[BaseTool]:
    return list(_registry.values())

def get_tool_manifest() -> str:
    """Readable list of all tools and descriptions, used in the selector prompt"""
    lines = []
    for name, tool in _registry.items():
        description = (tool.description or "").split("\n")[0][:120]
        lines.append(f"{name}: {description}")
    return "\n".join(lines)
