from backend.automation.automation_manager import AutomationManager


class CommandExecutor:

    def __init__(self, memory_service=None):

        self.automation = AutomationManager()
        self.memory = memory_service

    def execute(self, command):

        command_type = command.get("type")
        action = command.get("action")
        data = command.get("data")

        # ==========================================
        # MEMORY
        # ==========================================

        if command_type == "memory":

            if self.memory is None:
                return "Memory service is not available."

            if action == "remember":

                if not data:
                    return "What would you like me to remember?"

                saved = self.memory.remember(data)

                if saved:
                    return f"I'll remember that: {data}"

                return f"I already remember that: {data}"

            if action == "recall":

                memories = self.memory.get_all()

                if not memories:
                    return "I don't have any saved memories yet."

                return (
                    "Here's what I remember:\n- "
                    + "\n- ".join(memories)
                )

            if action == "forget":

                if not data:
                    return "What would you like me to forget?"

                deleted = self.memory.forget(data)

                if deleted:
                    return (
                        f"I've forgotten {deleted} "
                        f"memory item(s) matching '{data}'."
                    )

                return (
                    f"I couldn't find any memory "
                    f"matching '{data}'."
                )

        # ==========================================
        # AUTOMATION
        # ==========================================

        if command_type == "automation":

            if action == "open":

                if not data:
                    return "What would you like me to open?"

                return self.automation.open(data)

        # ==========================================
        # TOOLS
        # ==========================================

        if command_type == "tool":

            if action == "search":

                return (
                    f"Search tool is not implemented yet: "
                    f"{data}"
                )

        return "I don't know how to execute that command."
