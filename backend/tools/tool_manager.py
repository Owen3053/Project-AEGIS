from backend.tools.search_tool import SearchTool
from backend.tools.calculator_tool import CalculatorTool


class ToolManager:

    def __init__(self):

        self.tools = {
            "search": SearchTool(),
            "calculator": CalculatorTool(),
        }

    def list_tools(self):

        return {
            name: tool.description
            for name, tool in self.tools.items()
        }

    def has_tool(self, name):

        return name in self.tools

    def execute(self, name, data):

        if name not in self.tools:
            return f"I don't have a '{name}' tool yet."

        return self.tools[name].execute(data)