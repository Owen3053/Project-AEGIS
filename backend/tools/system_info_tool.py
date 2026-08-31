import os
import platform

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

            information = {
                "operating_system": system,
                "os_release": release,
                "os_version": version,
                "machine": machine,
                "processor": processor,
                "cpu_cores": cpu_count,
                "python_version": python_version
            }

            return self.success(information)

        except Exception as error:

            return self.failure(
                f"I couldn't retrieve the system information: {error}"
            )