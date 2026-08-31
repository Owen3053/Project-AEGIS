class CommandRouter:

    def route(self, message):

        text = message.lower().strip()

        # ==========================================
        # MEMORY
        # ==========================================

        if text.startswith("remember that "):

            return {
                "type": "memory",
                "action": "remember",
                "data": message[len("remember that "):].strip()
            }

        if text.startswith("remember "):

            return {
                "type": "memory",
                "action": "remember",
                "data": message[len("remember "):].strip()
            }

        if text.startswith("forget "):

            return {
                "type": "memory",
                "action": "forget",
                "data": message[len("forget "):].strip()
            }

        if (
            "what do you remember" in text
            or "what memories do you have" in text
            or "show my memories" in text
            or "show me my memories" in text
        ):

            return {
                "type": "memory",
                "action": "recall",
                "data": None
            }

        # ==========================================
        # TOOL DISCOVERY
        # ==========================================

        tool_discovery_triggers = [
            "what tools do you have",
            "what tools are available",
            "list your tools",
            "show your tools",
            "show me your tools",
            "available tools"
        ]

        if text in tool_discovery_triggers:

            return {
                "type": "tool_discovery",
                "action": None,
                "data": None
            }

        # ==========================================
        # SYSTEM INFORMATION
        # ==========================================

        system_info_triggers = [
            "system info",
            "system information",
            "computer info",
            "computer information",
            "pc info",
            "my system info",
            "my computer info"
        ]

        if text in system_info_triggers:

            return {
                "type": "tool",
                "action": "system_info",
                "data": None
            }

        # ==========================================
        # AUTOMATION
        # ==========================================

        open_targets = [
            "calculator",
            "calc",
            "notepad",
            "chrome",
            "vscode",
            "youtube",
            "google",
            "github",
            "downloads",
            "documents",
            "desktop"
        ]

        open_triggers = [
            "open ",
            "open the ",
            "launch ",
            "launch the ",
            "start ",
            "start the "
        ]

        for trigger in open_triggers:

            if text.startswith(trigger):

                target = text[len(trigger):].strip()

                if target in open_targets:

                    return {
                        "type": "automation",
                        "action": "open",
                        "data": target
                    }

        # Natural-language open requests

        natural_open = [
            "can you open ",
            "could you open ",
            "please open ",
            "can you launch ",
            "could you launch ",
            "please launch ",
            "can you start ",
            "could you start "
        ]

        for trigger in natural_open:

            if text.startswith(trigger):

                target = text[len(trigger):].strip()

                if target.startswith("the "):
                    target = target[4:].strip()

                if target in open_targets:

                    return {
                        "type": "automation",
                        "action": "open",
                        "data": target
                    }

        # ==========================================
        # CALCULATOR
        # ==========================================

        calculate_triggers = [
            "calculate ",
            "what is ",
            "compute "
        ]

        for trigger in calculate_triggers:

            if text.startswith(trigger):

                expression = message[len(trigger):].strip()

                return {
                    "type": "tool",
                    "action": "calculator",
                    "data": expression
                }

        # ==========================================
        # SEARCH
        # ==========================================

        search_triggers = [
            "search for ",
            "search ",
            "look up ",
            "look for ",
            "find information about ",
            "google "
        ]

        for trigger in search_triggers:

            if text.startswith(trigger):

                query = message[len(trigger):].strip()

                return {
                    "type": "tool",
                    "action": "search",
                    "data": query
                }

        natural_search = [
            "can you search for ",
            "could you search for ",
            "please search for ",
            "can you look up ",
            "could you look up ",
            "please look up ",
            "find me information about "
        ]

        for trigger in natural_search:

            if text.startswith(trigger):

                query = message[len(trigger):].strip()

                return {
                    "type": "tool",
                    "action": "search",
                    "data": query
                }

        # ==========================================
        # NORMAL CHAT
        # ==========================================

        return {
            "type": "chat",
            "action": None,
            "data": message
        }


if __name__ == "__main__":

    router = CommandRouter()

    tests = [

        # Memory
        "remember that my name is Owen",
        "forget my name",
        "what do you remember",

        # Tool discovery
        "what tools do you have",

        # System information
        "system info",
        "computer information",
        "pc info",

        # Automation
        "open calculator",
        "launch calculator",
        "start notepad",

        # Calculator
        "calculate 25 * 4",
        "what is 100 + 50",

        # Search
        "search Python tutorials",
        "look up autonomous drones",

        # Chat
        "Hello AEGIS"
    ]

    for test in tests:

        print(f"{test} ->")
        print(router.route(test))
        print()

