class BaseTool:

    name = "base"

    description = "Base class for AEGIS tools"

    def execute(self, data):
        raise NotImplementedError

    def success(self, data):
        return {
            "success": True,
            "tool": self.name,
            "data": data,
            "error": None
        }

    def failure(self, error):
        return {
            "success": False,
            "tool": self.name,
            "data": None,
            "error": error
        }