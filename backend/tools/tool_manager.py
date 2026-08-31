import importlib
import inspect
import pkgutil

from backend.tools.base_tool import BaseTool


class ToolManager:

    def __init__(self):

        self.tools = {}

        self.discover_tools()

    # ==========================================
    # DYNAMIC TOOL DISCOVERY
    # ==========================================

    def discover_tools(self):

        package_name = "backend.tools"

        package = importlib.import_module(package_name)

        for module_info in pkgutil.iter_modules(
            package.__path__
        ):

            module_name = module_info.name

            # Ignore internal/base modules
            if module_name.startswith("_"):
                continue

            if module_name == "base_tool":
                continue

            try:

                module = importlib.import_module(
                    f"{package_name}.{module_name}"
                )

            except Exception as error:

                print(
                    f"AEGIS: Could not load tool module "
                    f"{module_name}: {error}"
                )

                continue

            self._discover_classes(module)

    # ==========================================
    # DISCOVER TOOL CLASSES
    # ==========================================

    def _discover_classes(self, module):

        for _, obj in inspect.getmembers(
            module,
            inspect.isclass
        ):

            if obj is BaseTool:
                continue

            if not issubclass(obj, BaseTool):
                continue

            # Avoid registering imported BaseTool subclasses
            if obj.__module__ != module.__name__:
                continue

            try:

                tool = obj()

                self.register(tool)

            except Exception as error:

                print(
                    f"AEGIS: Could not register "
                    f"{obj.__name__}: {error}"
                )

    # ==========================================
    # REGISTER
    # ==========================================

    def register(self, tool):

        if not hasattr(tool, "name"):
            raise ValueError(
                "Tool must have a name."
            )

        if not hasattr(tool, "description"):
            raise ValueError(
                "Tool must have a description."
            )

        if not callable(
            getattr(tool, "execute", None)
        ):
            raise ValueError(
                "Tool must have an execute method."
            )

        if tool.name in self.tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered."
            )

        self.tools[tool.name] = tool

    # ==========================================
    # UNREGISTER
    # ==========================================

    def unregister(self, name):

        if name in self.tools:

            del self.tools[name]

            return True

        return False

    # ==========================================
    # LIST TOOLS
    # ==========================================

    def list_tools(self):

        return {
            name: tool.description
            for name, tool in self.tools.items()
        }

    # ==========================================
    # CHECK TOOL
    # ==========================================

    def has_tool(self, name):

        return name in self.tools

    # ==========================================
    # EXECUTE TOOL
    # ==========================================

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

        try:

            return self.tools[name].execute(data)

        except Exception as error:

            return {
                "success": False,
                "tool": name,
                "data": None,
                "error": str(error)
            }

    # ==========================================
    # DESCRIBE TOOLS
    # ==========================================

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


if __name__ == "__main__":

    manager = ToolManager()

    print("Discovered tools:")
    print()

    print(manager.describe_tools())