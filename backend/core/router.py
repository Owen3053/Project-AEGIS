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
        "show me my memories",

        # Automation
        "open calculator",
        "open the calculator",
        "launch calculator",
        "start notepad",
        "can you open calculator",
        "could you open youtube",
        "please launch chrome",

        # Search
        "search Python tutorials",
        "search for Python AI tutorials",
        "look up autonomous drones",
        "google AEGIS AI assistant",
        "can you search for Python AI",
        "could you search for robotics",
        "please look up autonomous drones",
        "find me information about AI",

        # Chat
        "Hello AEGIS"
    ]

    for test in tests:

        print(f"{test} ->")
        print(router.route(test))
        print()
