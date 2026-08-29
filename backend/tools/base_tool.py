class BaseTool:

    name = "base"

    description = "Base class for AEGIS tools"

    def execute(self, data):
        raise NotImplementedError
