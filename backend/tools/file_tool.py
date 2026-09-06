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

    FOLDER_ALIASES = {
        "desktop": "Desktop",
        "my desktop": "Desktop",

        "documents": "Documents",
        "my documents": "Documents",
        "document": "Documents",

        "downloads": "Downloads",
        "my downloads": "Downloads",
        "download": "Downloads",

        "pictures": "Pictures",
        "my pictures": "Pictures",
        "photos": "Pictures",

        "music": "Music",
        "my music": "Music",

        "videos": "Videos",
        "my videos": "Videos",
        "video": "Videos",

        "favorites": "Favorites",
        "my favorites": "Favorites",

        "onedrive": "OneDrive",
        "my onedrive": "OneDrive",
    }

    WINDOWS_KNOWN_FOLDERS = {
        "desktop": (
            "USERPROFILE",
            "Desktop"
        ),
        "documents": (
            "USERPROFILE",
            "Documents"
        ),
        "downloads": (
            "USERPROFILE",
            "Downloads"
        ),
        "pictures": (
            "USERPROFILE",
            "Pictures"
        ),
        "music": (
            "USERPROFILE",
            "Music"
        ),
        "videos": (
            "USERPROFILE",
            "Videos"
        ),
        "favorites": (
            "USERPROFILE",
            "Favorites"
        ),
        "onedrive": (
            "OneDrive",
            ""
        ),
    }

    ENVIRONMENT_HOME_ALIASES = {
        "%userprofile%",
        "$home",
        "$userprofile",
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

        # ==========================================
        # HOME DIRECTORY ALIASES
        # ==========================================

        if normalized in self.HOME_ALIASES:
            return home

        # ==========================================
        # WINDOWS KNOWN FOLDER ALIASES
        # ==========================================

        if os.name == "nt" and normalized in {
            "desktop",
            "my desktop",
            "documents",
            "my documents",
            "document",
            "downloads",
            "my downloads",
            "download",
            "pictures",
            "my pictures",
            "photos",
            "music",
            "my music",
            "videos",
            "my videos",
            "video",
            "favorites",
            "my favorites",
            "onedrive",
            "my onedrive",
        }:

            return self._resolve_windows_known_folder(
                normalized
            )

        # ==========================================
        # STANDARD USER FOLDER ALIASES
        # ==========================================

        if normalized in self.FOLDER_ALIASES:

            folder_name = self.FOLDER_ALIASES[normalized]

            return os.path.join(
                home,
                folder_name
            )

        # ==========================================
        # WINDOWS ENVIRONMENT VARIABLES
        # ==========================================

        if normalized in self.ENVIRONMENT_HOME_ALIASES:
            return home

        # ==========================================
        # EXPAND ENVIRONMENT VARIABLES
        # ==========================================

        requested = os.path.expandvars(requested)
        requested = os.path.expanduser(requested)

        # ==========================================
        # PREVENT COMMON LINUX HOME PATHS
        # ==========================================

        if requested in {
            "/home/$USER",
            "/home/${USER}",
            "/home/user",
        }:
            return home

        # ==========================================
        # HANDLE COMMON USER FOLDER NAMES
        # ==========================================

        normalized_expanded = requested.lower().strip()

        if normalized_expanded in self.FOLDER_ALIASES:

            folder_name = self.FOLDER_ALIASES[
                normalized_expanded
            ]

            return os.path.join(
                home,
                folder_name
            )

        # ==========================================
        # RETURN EXPLICIT PATH
        # ==========================================

        return requested

    def _resolve_windows_known_folder(self, requested):

        home = os.path.expanduser("~")

        canonical_name = requested

        aliases = {
            "my desktop": "desktop",
            "my documents": "documents",
            "document": "documents",
            "my downloads": "downloads",
            "download": "downloads",
            "my pictures": "pictures",
            "photos": "pictures",
            "my music": "music",
            "my videos": "videos",
            "video": "videos",
            "my favorites": "favorites",
            "my onedrive": "onedrive",
        }

        canonical_name = aliases.get(
            canonical_name,
            canonical_name
        )

        # OneDrive is commonly exposed through an
        # environment variable on Windows.
        if canonical_name == "onedrive":

            onedrive = os.environ.get(
                "OneDrive"
            )

            if onedrive and os.path.isdir(onedrive):
                return onedrive

            return os.path.join(
                home,
                "OneDrive"
            )

        environment_name, default_folder = (
            self.WINDOWS_KNOWN_FOLDERS[
                canonical_name
            ]
        )

        base_path = os.environ.get(
            environment_name,
            home
        )

        standard_path = os.path.join(
            base_path,
            default_folder
        )

        if os.path.isdir(standard_path):
            return standard_path

        # Common OneDrive redirections.
        onedrive = os.environ.get(
            "OneDrive"
        )

        if onedrive:

            onedrive_path = os.path.join(
                onedrive,
                default_folder
            )

            if os.path.isdir(onedrive_path):
                return onedrive_path

        return standard_path


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
        "desktop",
        "documents",
        "downloads",
        "pictures",
        "music",
        "videos",
        "onedrive",
    ]

    for test in tests:

        print(
            f"\nInput: {test}"
        )

        print(
            tool.execute(test)
        )