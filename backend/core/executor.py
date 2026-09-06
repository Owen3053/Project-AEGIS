from backend.automation.automation_manager import AutomationManager
from backend.core.permission_manager import PermissionManager
from backend.tools.tool_manager import ToolManager


class CommandExecutor:

    def __init__(
        self,
        memory_service
    ):

        self.automation = (
            AutomationManager()
        )

        self.tools = ToolManager()

        self.memory = memory_service

        self.permissions = (
            PermissionManager()
        )

    # ==========================================
    # EXECUTE
    # ==========================================

    def execute(
        self,
        command
    ):

        if not isinstance(
            command,
            dict
        ):

            return (
                "I received an invalid command."
            )

        permission = (
            self.permissions.check(
                command
            )
        )

        if not permission["allowed"]:

            return (
                "AEGIS safety system blocked "
                "this action: "
                + permission["reason"]
            )

        if permission[
            "requires_confirmation"
        ]:

            approved = (
                self.permissions
                .request_confirmation(
                    command
                )
            )

            if not approved:

                return (
                    "AEGIS: Action cancelled."
                )

        command_type = command.get(
            "type"
        )

        action = command.get(
            "action"
        )

        data = command.get(
            "data"
        )

        # ==========================================
        # MEMORY
        # ==========================================

        if command_type == "memory":

            if action == "remember":

                if not data:

                    return (
                        "What would you like me "
                        "to remember?"
                    )

                saved = self.memory.remember(
                    data
                )

                if saved:

                    return (
                        f"I'll remember that: "
                        f"{data}"
                    )

                return (
                    f"I already remember that: "
                    f"{data}"
                )

            if action == "recall":

                memories = (
                    self.memory.get_all()
                )

                if not memories:

                    return (
                        "I don't have any "
                        "saved memories yet."
                    )

                return (
                    "Here's what I remember:\n- "
                    + "\n- ".join(memories)
                )

            if action == "forget":

                if not data:

                    return (
                        "What would you like "
                        "me to forget?"
                    )

                deleted = (
                    self.memory.forget(
                        data
                    )
                )

                if deleted:

                    return (
                        f"I've forgotten "
                        f"{deleted} memory item(s) "
                        f"matching '{data}'."
                    )

                return (
                    f"I couldn't find any memory "
                    f"matching '{data}'."
                )

            return (
                f"I don't know how to perform "
                f"the memory action '{action}'."
            )

        # ==========================================
        # TOOL DISCOVERY
        # ==========================================

        if command_type == "tool_discovery":

            return (
                self.tools.describe_tools()
            )

        # ==========================================
        # AUTOMATION
        # ==========================================

        if command_type == "automation":

            if action != "open":

                return (
                    "I don't know how to perform "
                    f"the automation action '{action}'."
                )

            if not data:

                return (
                    "What would you like "
                    "me to open?"
                )

            return self.automation.open(
                data
            )

        # ==========================================
        # TOOLS
        # ==========================================

        if command_type == "tool":

            if not action:

                return (
                    "Which tool should I use?"
                )

            return self.tools.execute(
                action,
                data
            )

        # ==========================================
        # CHAT
        # ==========================================

        if command_type == "chat":

            return data

        # ==========================================
        # UNKNOWN COMMAND
        # ==========================================

        return (
            "I don't know how to execute "
            "that command."
        )


if __name__ == "__main__":

    from backend.memory.memory_service import MemoryService

    executor = CommandExecutor(
        MemoryService()
    )

    tests = [

        {
            "type": "tool",
            "action": "calculator",
            "data": "25 * 4"
        },

        {
            "type": "tool",
            "action": "search",
            "data": "AEGIS AI assistant"
        },

        {
            "type": "tool",
            "action": "system_info",
            "data": None
        },

        {
            "type": "tool",
            "action": "tool_discovery",
            "data": None
        },

        {
            "type": "automation",
            "action": "open",
            "data": "calculator"
        },

        {
            "type": "tool",
            "action": "files",
            "data": {
                "operation": "details",
                "path": ".\\backend\\core\\executor.py"
            }
        },

        {
            "type": "tool",
            "action": "unknown",
            "data": "test"
        }

    ]

    for test in tests:

        print(test)

        print(
            executor.execute(test)
        )

        print()