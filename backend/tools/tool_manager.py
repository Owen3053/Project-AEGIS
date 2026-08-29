from backend.tools.search_tool import SearchTool


class ToolManager:

    def __init__(self):

        self.tools = {
            "search": SearchTool()
        }

    def execute(self, tool_name, data):

        tool = self.tools.get(tool_name)

        if not tool:
            return f"I don't know how to use the '{tool_name}' tool."

        return tool.execute(data)

    def list_tools(self):

        return {
            name: tool.description
            for name, tool in self.tools.items()
        }
