from backend.tools.search_tool import SearchTool
from backend.tools.calculator_tool import CalculatorTool
from backend.tools.system_info_tool import SystemInfoTool


class ToolManager:

    def __init__(self):

        self.tools = {}

        self.register(SearchTool())
        self.register(CalculatorTool())
        self.register(SystemInfoTool())

    def register(self, tool):

        if not hasattr(tool, "name"):
            raise ValueError(
                "Tool must have a name."
            )

        if not hasattr(tool, "execute"):
            raise ValueError(
                "Tool must have an execute method."
            )

        self.tools[tool.name] = tool

    def unregister(self, name):

        if name in self.tools:
            del self.tools[name]
            return True

        return False

    def list_tools(self):

        return {
            name: tool.description
            for name, tool in self.tools.items()
        }

    def has_tool(self, name):

        return name in self.tools

    def execute(self, name, data):

        if not self.has_tool(name):

            return {
                "success": False,
                "tool": name,
                "data": None,
                "error": (
                    f"I don't have a "
                    f"'{name}' tool yet."
                )
            }

        result = self.tools[name].execute(data)

        # Make sure every tool returns
        # a structured result.

        if isinstance(result, dict):

            return result

        # Backward compatibility for
        # older tools.

        return {
            "success": True,
            "tool": name,
            "data": result,
            "error": None
        }

    def describe_tools(self):

        if not self.tools:
            return (
                "I don't have any tools available."
            )

        lines = []

        for name, tool in self.tools.items():

            lines.append(
                f"• {name} — {tool.description}"
            )

        return (
            f"I have {len(self.tools)} "
            f"tools available:\n\n"
            + "\n".join(lines)
        )