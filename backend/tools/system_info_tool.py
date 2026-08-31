import platform
import os

from backend.tools.base_tool import BaseTool


class SystemInfoTool(BaseTool):

    name = "system_info"

    description = "Get information about the computer system"

    def execute(self, data):

        try:

            system = platform.system()
            release = platform.release()
            version = platform.version()
            machine = platform.machine()
            processor = platform.processor()
            python_version = platform.python_version()
            cpu_count = os.cpu_count()

            return (
                "System Information:\n\n"
                f"Operating System: {system}\n"
                f"OS Release: {release}\n"
                f"OS Version: {version}\n"
                f"Machine: {machine}\n"
                f"Processor: {processor}\n"
                f"CPU Cores: {cpu_count}\n"
                f"Python Version: {python_version}"
            )

        except Exception as error:

            return f"I couldn't retrieve the system information: {error}"