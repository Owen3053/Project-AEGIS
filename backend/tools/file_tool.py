import os

from backend.tools.base_tool import BaseTool


class FileTool(BaseTool):

    name = "files"

    description = (
        "List files and folders, check paths, inspect directories, "
        "read text files, and search files on the computer"
    )

    MAX_READ_SIZE = 1 * 1024 * 1024
    MAX_SEARCH_RESULTS = 100
    MAX_CONTENT_SEARCH_FILE_SIZE = 512 * 1024

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
    }

    ENVIRONMENT_HOME_ALIASES = {
        "%userprofile%",
        "$home",
        "$userprofile",
    }

    TEXT_EXTENSIONS = {
        ".txt",
        ".md",
        ".markdown",
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".json",
        ".yaml",
        ".yml",
        ".xml",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
        ".csv",
        ".log",
        ".ini",
        ".cfg",
        ".conf",
        ".toml",
        ".sql",
        ".sh",
        ".bat",
        ".cmd",
        ".ps1",
        ".env",
    }

    def execute(self, data):

        operation = "list"
        target = data

        if isinstance(data, dict):

            operation = str(
                data.get("operation", "list")
            ).strip().lower()

            target = data.get("path")

        if operation == "list":
            return self._list_directory(target)

        if operation == "read":
            return self._read_file(target)

        if operation == "search":
            return self._search_files(data)

        return {
            "success": False,
            "tool": self.name,
            "data": None,
            "error": (
                f"Unsupported file operation: "
                f"{operation}"
            )
        }

    # ==========================================
    # LIST DIRECTORY
    # ==========================================

    def _list_directory(self, data):

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
                    "operation": "list",
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

    # ==========================================
    # READ FILE
    # ==========================================

    def _read_file(self, data):

        path = self._resolve_file_path(data)

        if not os.path.exists(path):

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": f"File does not exist: {path}"
            }

        if not os.path.isfile(path):

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": f"Path is not a file: {path}"
            }

        extension = os.path.splitext(path)[1].lower()

        if extension not in self.TEXT_EXTENSIONS:

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": (
                    f"Refusing to read unsupported file type: "
                    f"{extension or '[no extension]'}"
                )
            }

        try:

            file_size = os.path.getsize(path)

            if file_size > self.MAX_READ_SIZE:

                return {
                    "success": False,
                    "tool": self.name,
                    "data": None,
                    "error": (
                        f"File is too large to read safely. "
                        f"Maximum size is "
                        f"{self.MAX_READ_SIZE // 1024 // 1024} MB."
                    )
                }

            with open(
                path,
                "r",
                encoding="utf-8",
                errors="replace"
            ) as file:

                content = file.read()

            return {
                "success": True,
                "tool": self.name,
                "data": {
                    "operation": "read",
                    "path": path,
                    "size": file_size,
                    "content": content
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

    # ==========================================
    # SEARCH FILES
    # ==========================================

    def _search_files(self, data):

        if not isinstance(data, dict):

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": "Search requires a search dictionary."
            }

        query = str(
            data.get("query", "")
        ).strip()

        root = data.get("path")

        search_content = bool(
            data.get("content", False)
        )

        extension = str(
            data.get("extension", "")
        ).strip().lower()

        if not query:

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": "Search query cannot be empty."
            }

        search_root = self._resolve_path(root)

        if not os.path.exists(search_root):

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": (
                    f"Search path does not exist: "
                    f"{search_root}"
                )
            }

        if not os.path.isdir(search_root):

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": (
                    f"Search path is not a folder: "
                    f"{search_root}"
                )
            }

        query_lower = query.lower()

        if extension and not extension.startswith("."):
            extension = f".{extension}"

        results = []

        try:

            for current_root, directories, files in os.walk(
                search_root,
                topdown=True
            ):

                directories.sort(
                    key=str.lower
                )

                files.sort(
                    key=str.lower
                )

                for filename in files:

                    if len(results) >= self.MAX_SEARCH_RESULTS:
                        break

                    if extension:
                        if not filename.lower().endswith(
                            extension
                        ):
                            continue

                    full_path = os.path.join(
                        current_root,
                        filename
                    )

                    filename_matches = (
                        query_lower in filename.lower()
                    )

                    content_matches = False

                    if search_content and not filename_matches:

                        content_matches = (
                            self._file_contains_text(
                                full_path,
                                query_lower
                            )
                        )

                    if not (
                        filename_matches
                        or content_matches
                    ):
                        continue

                    try:

                        relative_path = os.path.relpath(
                            full_path,
                            search_root
                        )

                    except ValueError:

                        relative_path = filename

                    try:

                        file_size = os.path.getsize(
                            full_path
                        )

                    except OSError:

                        file_size = None

                    results.append(
                        {
                            "name": filename,
                            "path": full_path,
                            "relative_path": relative_path,
                            "size": file_size,
                            "match": (
                                "content"
                                if content_matches
                                else "filename"
                            )
                        }
                    )

                if len(results) >= self.MAX_SEARCH_RESULTS:
                    break

            return {
                "success": True,
                "tool": self.name,
                "data": {
                    "operation": "search",
                    "query": query,
                    "path": search_root,
                    "content_search": search_content,
                    "extension": extension or None,
                    "result_count": len(results),
                    "results": results,
                    "truncated": (
                        len(results)
                        >= self.MAX_SEARCH_RESULTS
                    )
                },
                "error": None
            }

        except PermissionError:

            return {
                "success": False,
                "tool": self.name,
                "data": None,
                "error": "Permission denied during search."
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

    def _file_contains_text(self, path, query_lower):

        extension = os.path.splitext(path)[1].lower()

        if extension not in self.TEXT_EXTENSIONS:
            return False

        try:

            file_size = os.path.getsize(path)

            if file_size > self.MAX_CONTENT_SEARCH_FILE_SIZE:
                return False

            with open(
                path,
                "r",
                encoding="utf-8",
                errors="replace"
            ) as file:

                for line in file:

                    if query_lower in line.lower():
                        return True

        except (
            PermissionError,
            OSError,
            UnicodeError
        ):

            return False

        return False

    # ==========================================
    # PATH RESOLUTION
    # ==========================================

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
        # WINDOWS KNOWN FOLDERS
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
        # COMMON LINUX HOME PATHS
        # ==========================================

        if requested in {
            "/home/$USER",
            "/home/${USER}",
            "/home/user",
        }:
            return home

        normalized_expanded = requested.lower().strip()

        if normalized_expanded in self.FOLDER_ALIASES:

            folder_name = self.FOLDER_ALIASES[
                normalized_expanded
            ]

            return os.path.join(
                home,
                folder_name
            )

        return requested

    def _resolve_file_path(self, data):

        if not data:
            return ""

        requested = str(data).strip()

        if not requested:
            return ""

        expanded = os.path.expandvars(
            os.path.expanduser(requested)
        )

        if os.path.isabs(expanded):
            return expanded

        normalized = expanded.lower()

        if normalized in self.HOME_ALIASES:
            return self._resolve_path(expanded)

        if normalized in self.FOLDER_ALIASES:
            return self._resolve_path(expanded)

        return expanded

    def _resolve_windows_known_folder(self, requested):

        home = os.path.expanduser("~")

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
            requested,
            requested
        )

        # ==========================================
        # ONEDRIVE
        # ==========================================

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

        # ==========================================
        # KNOWN FOLDER
        # ==========================================

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

        # ==========================================
        # ONEDRIVE REDIRECTION
        # ==========================================

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
        {
            "operation": "list",
            "path": "home"
        },
        {
            "operation": "read",
            "path": ".\\README.md"
        },
        {
            "operation": "search",
            "query": "file_tool",
            "path": "home"
        },
        {
            "operation": "search",
            "query": "ToolManager",
            "path": ".",
            "content": True,
            "extension": ".py"
        },
    ]

    for test in tests:

        print(
            f"\nINPUT: {test}"
        )

        print(
            tool.execute(test)
        )