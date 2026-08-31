from backend.tools.search_tool import SearchTool
from backend.tools.calculator_tool import CalculatorTool


class ToolManager:

    def __init__(self):
        self.tools = {}

        self.register(SearchTool())
        self.register(CalculatorTool())

    def register(self, tool):

        if not hasattr(tool, "name"):
            raise ValueError("Tool must have a name.")

        if not hasattr(tool, "execute"):
            raise ValueError("Tool must have an execute method.")

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
            return f"I don't have a '{name}' tool yet."

        return self.tools[name].execute(data)