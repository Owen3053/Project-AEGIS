import os


class PermissionManager:

    # ==========================================
    # ACTION CATEGORIES
    # ==========================================

    SAFE_FILE_OPERATIONS = {
        "list",
        "read",
        "search",
        "details",
    }

    CONFIRM_FILE_OPERATIONS = {
        "create_folder",
        "create_file",
        "write_file",
        "copy",
        "move",
        "rename",
    }

    PROTECTED_PATHS = {
        os.path.abspath(
            os.environ.get(
                "WINDIR",
                r"C:\Windows"
            )
        ).lower(),
        os.path.abspath(
            os.environ.get(
                "ProgramFiles",
                r"C:\Program Files"
            )
        ).lower(),
        os.path.abspath(
            os.environ.get(
                "ProgramFiles(x86)",
                r"C:\Program Files (x86)"
            )
        ).lower(),
    }

    # ==========================================
    # PUBLIC CHECK
    # ==========================================

    def check(self, command):

        if not isinstance(
            command,
            dict
        ):

            return {
                "allowed": False,
                "requires_confirmation": False,
                "reason": "Invalid command."
            }

        command_type = command.get(
            "type"
        )

        action = command.get(
            "action"
        )

        data = command.get(
            "data"
        )

        # --------------------------------------
        # Chat / discovery / memory
        # --------------------------------------

        if command_type in {
            "chat",
            "tool_discovery",
            "memory",
        }:

            return {
                "allowed": True,
                "requires_confirmation": False,
                "reason": None
            }

        # --------------------------------------
        # Automation
        # --------------------------------------

        if command_type == "automation":

            if action == "open":

                return {
                    "allowed": True,
                    "requires_confirmation": False,
                    "reason": None
                }

            return {
                "allowed": False,
                "requires_confirmation": False,
                "reason": (
                    f"Automation action '{action}' "
                    "is not permitted."
                )
            }

        # --------------------------------------
        # Tools
        # --------------------------------------

        if command_type != "tool":

            return {
                "allowed": False,
                "requires_confirmation": False,
                "reason": "Unknown command type."
            }

        if action != "files":

            return {
                "allowed": True,
                "requires_confirmation": False,
                "reason": None
            }

        if not isinstance(
            data,
            dict
        ):

            return {
                "allowed": False,
                "requires_confirmation": False,
                "reason": (
                    "Invalid file operation data."
                )
            }

        operation = str(
            data.get(
                "operation",
                ""
            )
        ).strip().lower()

        # --------------------------------------
        # Safe operations
        # --------------------------------------

        if operation in self.SAFE_FILE_OPERATIONS:

            return {
                "allowed": True,
                "requires_confirmation": False,
                "reason": None
            }

        # --------------------------------------
        # Protected destructive paths
        # --------------------------------------

        if operation in self.CONFIRM_FILE_OPERATIONS:

            paths = self._extract_paths(
                operation,
                data
            )

            protected_path = (
                self._find_protected_path(
                    paths
                )
            )

            if protected_path:

                return {
                    "allowed": False,
                    "requires_confirmation": False,
                    "reason": (
                        "This operation targets a "
                        f"protected system location: "
                        f"{protected_path}"
                    )
                }

            return {
                "allowed": True,
                "requires_confirmation": True,
                "reason": (
                    f"File operation '{operation}' "
                    "changes data on the computer."
                )
            }

        # --------------------------------------
        # Unknown file operation
        # --------------------------------------

        return {
            "allowed": False,
            "requires_confirmation": False,
            "reason": (
                f"File operation '{operation}' "
                "is not permitted."
            )
        }

    # ==========================================
    # CONFIRMATION
    # ==========================================

    def request_confirmation(
        self,
        command
    ):

        action_text = self.describe(
            command
        )

        print()
        print(
            "AEGIS SAFETY CHECK"
        )
        print(
            action_text
        )

        try:

            answer = input(
                "Allow this action? (yes/no): "
            ).strip().lower()

        except (
            EOFError,
            KeyboardInterrupt
        ):

            return False

        return answer in {
            "yes",
            "y"
        }

    # ==========================================
    # DESCRIPTION
    # ==========================================

    def describe(
        self,
        command
    ):

        command_type = command.get(
            "type"
        )

        action = command.get(
            "action"
        )

        data = command.get(
            "data"
        )

        if (
            command_type == "tool"
            and action == "files"
            and isinstance(data, dict)
        ):

            operation = data.get(
                "operation",
                "unknown"
            )

            if operation == "write_file":

                return (
                    f"AEGIS wants to write to "
                    f"'{data.get('path', '')}'."
                )

            if operation == "create_file":

                return (
                    f"AEGIS wants to create "
                    f"'{data.get('path', '')}'."
                )

            if operation == "create_folder":

                return (
                    f"AEGIS wants to create the "
                    f"folder '{data.get('path', '')}'."
                )

            if operation == "copy":

                return (
                    "AEGIS wants to copy "
                    f"'{data.get('source', '')}' "
                    "to "
                    f"'{data.get('destination', '')}'."
                )

            if operation == "move":

                return (
                    "AEGIS wants to move "
                    f"'{data.get('source', '')}' "
                    "to "
                    f"'{data.get('destination', '')}'."
                )

            if operation == "rename":

                return (
                    "AEGIS wants to rename "
                    f"'{data.get('source', '')}' "
                    "to "
                    f"'{data.get('destination', '')}'."
                )

        return (
            f"AEGIS wants to perform "
            f"'{command_type}:{action}'."
        )

    # ==========================================
    # PATH EXTRACTION
    # ==========================================

    @staticmethod
    def _extract_paths(
        operation,
        data
    ):

        if operation in {
            "create_folder",
            "create_file",
            "write_file",
        }:

            path = data.get(
                "path"
            )

            return (
                [str(path)]
                if path
                else []
            )

        if operation in {
            "copy",
            "move",
            "rename",
        }:

            return [
                str(path)
                for path in [
                    data.get("source"),
                    data.get("destination"),
                ]
                if path
            ]

        return []

    # ==========================================
    # PROTECTED PATH CHECK
    # ==========================================

    def _find_protected_path(
        self,
        paths
    ):

        for raw_path in paths:

            expanded = os.path.abspath(
                os.path.expandvars(
                    os.path.expanduser(
                        str(raw_path)
                    )
                )
            )

            normalized = (
                expanded.rstrip(
                    "\\/"
                ).lower()
            )

            for protected in self.PROTECTED_PATHS:

                protected_normalized = (
                    protected.rstrip(
                        "\\/"
                    )
                )

                if (
                    normalized == protected_normalized
                    or normalized.startswith(
                        protected_normalized + os.sep
                    )
                ):

                    return expanded

        return None