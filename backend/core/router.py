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

        natural_system_info = [
            "what processor do i have",
            "what cpu do i have",
            "what cpu does this computer have",
            "what processor does this computer have",
            "what operating system am i using",
            "what operating system is this",
            "tell me about my computer",
            "tell me about this computer",
            "show me my computer information",
            "show me my system information"
        ]

        if text in natural_system_info:

            return {
                "type": "tool",
                "action": "system_info",
                "data": None
            }

        # ==========================================
        # FILE SYSTEM
        # ==========================================

        # ------------------------------------------
        # FILE DETAILS
        # ------------------------------------------

        file_details_commands = [
            "details of ",
            "details for ",
            "file details ",
            "file information ",
            "file info ",
            "what is the file info for ",
            "what are the details of ",
            "show details of ",
            "show me the details of ",
            "show information for ",
            "show me information about "
        ]

        for trigger in file_details_commands:

            if text.startswith(trigger):

                path = message[len(trigger):].strip()

                if path.startswith("the file "):
                    path = path[len("the file "):].strip()

                return {
                    "type": "tool",
                    "action": "files",
                    "data": {
                        "operation": "details",
                        "path": path
                    }
                }

        natural_file_details = [
            "how large is ",
            "how big is ",
            "when was modified ",
            "what type of file is "
        ]

        for trigger in natural_file_details:

            if text.startswith(trigger):

                path = message[len(trigger):].strip()

                if path.endswith("?"):
                    path = path[:-1].strip()

                return {
                    "type": "tool",
                    "action": "files",
                    "data": {
                        "operation": "details",
                        "path": path
                    }
                }

        # ------------------------------------------
        # FILE OPERATIONS
        # ------------------------------------------

        if text.startswith("create folder "):

            path = message[len("create folder "):].strip()

            return {
                "type": "tool",
                "action": "files",
                "data": {
                    "operation": "create_folder",
                    "path": path
                }
            }

        if text.startswith("create a folder "):

            path = message[len("create a folder "):].strip()

            return {
                "type": "tool",
                "action": "files",
                "data": {
                    "operation": "create_folder",
                    "path": path
                }
            }

        if text.startswith("make a folder "):

            path = message[len("make a folder "):].strip()

            return {
                "type": "tool",
                "action": "files",
                "data": {
                    "operation": "create_folder",
                    "path": path
                }
            }

        if text.startswith("create file "):

            path = message[len("create file "):].strip()

            return {
                "type": "tool",
                "action": "files",
                "data": {
                    "operation": "create_file",
                    "path": path,
                    "content": ""
                }
            }

        if text.startswith("create a file "):

            path = message[len("create a file "):].strip()

            return {
                "type": "tool",
                "action": "files",
                "data": {
                    "operation": "create_file",
                    "path": path,
                    "content": ""
                }
            }

        if text.startswith("write "):

            remainder = message[len("write "):].strip()
            lower_remainder = remainder.lower()

            write_separators = [
                " to file ",
                " into file ",
                " in file ",
                " to ",
                " into ",
                " in "
            ]

            for separator in write_separators:

                if separator in lower_remainder:

                    index = lower_remainder.index(separator)

                    content = remainder[:index].strip()
                    path = remainder[
                        index + len(separator):
                    ].strip()

                    if (
                        len(content) >= 2
                        and content[0] == '"'
                        and content[-1] == '"'
                    ):
                        content = content[1:-1]

                    return {
                        "type": "tool",
                        "action": "files",
                        "data": {
                            "operation": "write_file",
                            "path": path,
                            "content": content,
                            "overwrite": False
                        }
                    }

        if text.startswith("copy "):

            remainder = message[len("copy "):].strip()
            lower_remainder = remainder.lower()

            for separator in [
                " to ",
                " into "
            ]:

                if separator in lower_remainder:

                    index = lower_remainder.index(separator)

                    source = remainder[:index].strip()
                    destination = remainder[
                        index + len(separator):
                    ].strip()

                    return {
                        "type": "tool",
                        "action": "files",
                        "data": {
                            "operation": "copy",
                            "source": source,
                            "destination": destination
                        }
                    }

        if text.startswith("move "):

            remainder = message[len("move "):].strip()
            lower_remainder = remainder.lower()

            for separator in [
                " to ",
                " into "
            ]:

                if separator in lower_remainder:

                    index = lower_remainder.index(separator)

                    source = remainder[:index].strip()
                    destination = remainder[
                        index + len(separator):
                    ].strip()

                    return {
                        "type": "tool",
                        "action": "files",
                        "data": {
                            "operation": "move",
                            "source": source,
                            "destination": destination
                        }
                    }

        if text.startswith("rename "):

            remainder = message[len("rename "):].strip()
            lower_remainder = remainder.lower()

            for separator in [
                " to ",
                " as "
            ]:

                if separator in lower_remainder:

                    index = lower_remainder.index(separator)

                    source = remainder[:index].strip()
                    destination = remainder[
                        index + len(separator):
                    ].strip()

                    return {
                        "type": "tool",
                        "action": "files",
                        "data": {
                            "operation": "rename",
                            "source": source,
                            "destination": destination
                        }
                    }

        # ------------------------------------------
        # SEARCH FILES
        # ------------------------------------------

        file_search_commands = [
            "find file ",
            "find files ",
            "find ",
            "search files for ",
            "search my files for ",
            "search my project for ",
            "find my files for ",
            "locate "
        ]

        for trigger in file_search_commands:

            if text.startswith(trigger):

                query = message[len(trigger):].strip()

                query_lower = query.lower()

                for phrase in [
                    "files named ",
                    "file named ",
                    "files called ",
                    "file called ",
                    "named ",
                    "called "
                ]:

                    if query_lower.startswith(phrase):

                        query = query[len(phrase):].strip()
                        break

                return {
                    "type": "tool",
                    "action": "files",
                    "data": {
                        "operation": "search",
                        "query": query,
                        "path": "home",
                        "content": False
                    }
                }

        # ------------------------------------------
        # CONTENT SEARCH
        # ------------------------------------------

        content_search_commands = [
            "search file contents for ",
            "search file content for ",
            "search inside files for ",
            "search inside my files for ",
            "find text ",
            "find text in my files "
        ]

        for trigger in content_search_commands:

            if text.startswith(trigger):

                query = message[len(trigger):].strip()

                return {
                    "type": "tool",
                    "action": "files",
                    "data": {
                        "operation": "search",
                        "query": query,
                        "path": "home",
                        "content": True
                    }
                }

        # ------------------------------------------
        # PROJECT SEARCH
        # ------------------------------------------

        project_search_commands = [
            "search project for ",
            "search the project for ",
            "find in project ",
            "find in my project "
        ]

        for trigger in project_search_commands:

            if text.startswith(trigger):

                query = message[len(trigger):].strip()

                return {
                    "type": "tool",
                    "action": "files",
                    "data": {
                        "operation": "search",
                        "query": query,
                        "path": ".",
                        "content": True
                    }
                }

        # ------------------------------------------
        # READ FILE
        # ------------------------------------------

        file_read_triggers = [
            "read file ",
            "read the file ",
            "show contents of ",
            "show the contents of ",
            "show me the contents of ",
            "read contents of ",
            "read the contents of ",
            "open text file ",
            "inspect file ",
            "inspect the file "
        ]

        for trigger in file_read_triggers:

            if text.startswith(trigger):

                path = message[len(trigger):].strip()

                return {
                    "type": "tool",
                    "action": "files",
                    "data": {
                        "operation": "read",
                        "path": path
                    }
                }

        natural_file_read_requests = [
            "can you read ",
            "could you read ",
            "please read ",
            "can you show me the contents of ",
            "could you show me the contents of ",
            "please show me the contents of "
        ]

        for trigger in natural_file_read_requests:

            if text.startswith(trigger):

                path = message[len(trigger):].strip()

                return {
                    "type": "tool",
                    "action": "files",
                    "data": {
                        "operation": "read",
                        "path": path
                    }
                }

        # ------------------------------------------
        # LIST DIRECTORY WITH PATH
        # ------------------------------------------

        file_path_triggers = [
            "list files in ",
            "show files in ",
            "show me the files in ",
            "list folders in ",
            "show folders in ",
            "show me the folders in ",
            "inspect directory ",
            "inspect folder ",
            "show directory ",
            "show folder "
        ]

        for trigger in file_path_triggers:

            if text.startswith(trigger):

                path = message[len(trigger):].strip()

                if path.startswith("in "):
                    path = path[3:].strip()

                if not path:
                    path = "home"

                return {
                    "type": "tool",
                    "action": "files",
                    "data": path
                }

        # ------------------------------------------
        # GENERIC FILE LISTING
        # ------------------------------------------

        home_file_commands = {
            "list files",
            "show files",
            "show me the files",
            "list folders",
            "show folders",
            "show me the folders"
        }

        if text in home_file_commands:

            return {
                "type": "tool",
                "action": "files",
                "data": "home"
            }

        natural_file_requests = [
            "can you list files",
            "could you list files",
            "please list files",
            "can you show files",
            "could you show files",
            "please show files",
            "can you show me the files",
            "could you show me the files",
            "please show me the files",
            "can you list folders",
            "could you list folders",
            "please list folders",
            "can you show folders",
            "could you show folders",
            "please show folders"
        ]

        for trigger in natural_file_requests:

            if text.startswith(trigger):

                path = message[len(trigger):].strip()

                if path.startswith("in "):
                    path = path[3:].strip()

                if not path:
                    path = "home"

                return {
                    "type": "tool",
                    "action": "files",
                    "data": path
                }

        # ==========================================
        # AUTOMATION
        # ==========================================

        open_targets = [
            "calculator",
            "calc",
            "notepad",
            "paint",
            "chrome",
            "edge",
            "firefox",
            "vscode",
            "explorer",
            "file explorer",
            "terminal",
            "command prompt",
            "powershell",
            "youtube",
            "google",
            "github",
            "gmail",
            "chatgpt",
            "downloads",
            "documents",
            "desktop",
            "pictures",
            "photos",
            "music",
            "videos",
            "favorites",
            "onedrive"
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

                target = message[len(trigger):].strip()
                target_lower = target.lower()

                if target_lower.startswith("the "):

                    target = target[4:].strip()
                    target_lower = target.lower()

                if target_lower in open_targets:

                    return {
                        "type": "automation",
                        "action": "open",
                        "data": target
                    }

                if (
                    target_lower.startswith("http://")
                    or target_lower.startswith("https://")
                    or "\\" in target
                    or "/" in target
                    or target.startswith(".")
                    or target.startswith("~")
                    or (
                        len(target) >= 2
                        and target[1] == ":"
                    )
                ):

                    return {
                        "type": "automation",
                        "action": "open",
                        "data": target
                    }

        natural_open = [
            "can you open ",
            "could you open ",
            "please open ",
            "can you launch ",
            "could you launch ",
            "please launch ",
            "can you start ",
            "could you start ",
            "please start "
        ]

        for trigger in natural_open:

            if text.startswith(trigger):

                target = message[
                    len(trigger):
                ].strip()

                target_lower = target.lower()

                if target_lower.startswith("the "):

                    target = target[4:].strip()
                    target_lower = target.lower()

                if target_lower in open_targets:

                    return {
                        "type": "automation",
                        "action": "open",
                        "data": target
                    }

                if (
                    target_lower.startswith("http://")
                    or target_lower.startswith("https://")
                    or "\\" in target
                    or "/" in target
                    or target.startswith(".")
                    or target.startswith("~")
                    or (
                        len(target) >= 2
                        and target[1] == ":"
                    )
                ):

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

        natural_calculator = [
            "how much is ",
            "how many is ",
            "solve ",
            "work out ",
            "what does ",
            "can you calculate ",
            "can you work out ",
            "please calculate ",
            "please solve "
        ]

        for trigger in natural_calculator:

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
            "find me information about ",
            "tell me about the latest ",
            "what is happening with "
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
        "what processor do i have",
        "tell me about my computer",

        # File system - list
        "list files",
        "list files in home",
        "show me the files in documents",
        "inspect folder desktop",
        "list folders in downloads",

        # File system - read
        "read file test.txt",
        "show contents of notes.txt",
        "inspect file config.json",

        # File system - search
        "find file_tool",
        "find file router.py",
        "find files named router.py",
        "search files for calculator",
        "search project for ToolManager",
        "search file contents for Ollama",

        # File system - details
        "details of router.py",
        "file details file_tool.py",
        "file info router.py",
        "how large is router.py",

        # File system - operations
        "create folder .\\aegis_file_test",
        "create file .\\aegis_file_test\\notes.txt",
        "write hello AEGIS to .\\aegis_file_test\\notes.txt",
        "copy .\\aegis_file_test\\notes.txt to .\\aegis_file_test\\backup.txt",
        "move .\\aegis_file_test\\backup.txt to .\\aegis_file_test\\moved.txt",
        "rename .\\aegis_file_test\\moved.txt to .\\aegis_file_test\\renamed.txt",

        # Automation
        "open calculator",
        "open notepad",
        "open desktop",
        "open downloads",
        "open youtube",
        "open github",
        "launch vscode",
        "can you open documents",
        "open https://www.google.com",
        "open C:\\Windows",

        # Calculator
        "calculate 25 * 4",
        "what is 100 + 50",
        "how much is 25 times 40",
        "solve 100 + 200",

        # Search
        "search Python tutorials",
        "look up autonomous drones",
        "can you search for AI news",

        # Chat
        "Hello AEGIS"
    ]

    for test in tests:

        print(f"{test} ->")
        print(router.route(test))
        print()