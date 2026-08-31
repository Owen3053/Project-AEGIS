import os

from backend.tools.base_tool import BaseTool


class FileTool(BaseTool):

    name = "files"

    description = (
        "List files and folders, check paths, "
        "and inspect directories on the computer"
    )

    HOME_ALIASES = {
        "home",
        "my home",
        "home directory",
        "my home directory",
        "user directory",
        "my user directory",
        "user folder",
        "my user folder",
    }

    def execute(self, data):

        path = self._resolve_path(data)

        if not os.path.exists(path):

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": f"Path does not exist: {path}"
            }

        if not os.path.isdir(path):

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": f"Path is not a folder: {path}"
            }

        try:

            entries = os.listdir(path)

            files = []
            folders = []

            for entry in entries:

                full_path = os.path.join(
                    path,
                    entry
                )

                try:

                    if os.path.isdir(full_path):
                        folders.append(entry)
                    else:
                        files.append(entry)

                except OSError:
                    continue

            folders.sort(key=str.lower)
            files.sort(key=str.lower)

            return {
                "success": True,
                "tool": self.name,
                "data": {
                    "path": path,
                    "folders": folders,
                    "files": files,
                    "folder_count": len(folders),
                    "file_count": len(files)
                },
                "error": None
            }

        except PermissionError:

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": "Permission denied."
            }

        except OSError as error:

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": str(error)
            }

        except Exception as error:

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": str(error)
            }

    def _resolve_path(self, data):

        home = os.path.expanduser("~")

        if not data:
            return home

        requested = str(data).strip()

        if not requested:
            return home

        normalized = requested.lower()

        # ------------------------------------------
        # HOME DIRECTORY ALIASES
        # ------------------------------------------

        if normalized in self.HOME_ALIASES:
            return home

        # ------------------------------------------
        # WINDOWS ENVIRONMENT VARIABLES
        # ------------------------------------------

        if normalized in {
            "%userprofile%",
            "$home",
            "$userprofile",
        }:
            return home

        # ------------------------------------------
        # EXPAND STANDARD PATHS
        # ------------------------------------------

        requested = os.path.expandvars(requested)
        requested = os.path.expanduser(requested)

        # ------------------------------------------
        # PREVENT COMMON LINUX HOME PATH
        # ------------------------------------------

        if requested in {
            "/home/$USER",
            "/home/${USER}",
            "/home/user",
        }:
            return home

        return requested


if __name__ == "__main__":

    tool = FileTool()

    tests = [
        None,
        "home",
        "my home",
        "home directory",
        "my home directory",
        "~",
        "%USERPROFILE%",
    ]

    for test in tests:

        print(
            f"\nInput: {test}"
        )

        print(
            tool.execute(test)
        )