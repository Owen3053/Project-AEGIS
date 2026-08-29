class CommandRouter:

    def route(self, message):

        text = message.lower().strip()

        # MEMORY COMMANDS

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
            or text == "show my memories"
        ):

            return {
                "type": "memory",
                "action": "recall",
                "data": None
            }

        # AUTOMATION COMMANDS

        if text.startswith("open "):

            return {
                "type": "automation",
                "action": "open",
                "data": message[len("open "):].strip()
            }

        # TOOL COMMANDS

        if text.startswith("search "):

            return {
                "type": "tool",
                "action": "search",
                "data": message[len("search "):].strip()
            }

        # NORMAL CHAT

        return {
            "type": "chat",
            "action": None,
            "data": message
        }


if __name__ == "__main__":

    router = CommandRouter()

    tests = [
        "remember that my name is Owen",
        "forget my name",
        "what do you remember",
        "open calculator",
        "open chrome",
        "open youtube",
        "open downloads",
        "search Python tutorials",
        "Hello AEGIS"
    ]

    for test in tests:
        print(f"{test} ->")
        print(router.route(test))
        print()
