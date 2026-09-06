import os
import shutil
from datetime import datetime

from backend.tools.base_tool import BaseTool


class FileTool(BaseTool):

    name = "files"

    description = (
        "List files and folders, check paths, inspect directories, "
        "read text files, search files, inspect file details, "
        "and perform safe file operations on the computer"
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
        "desktop": ("USERPROFILE", "Desktop"),
        "documents": ("USERPROFILE", "Documents"),
        "downloads": ("USERPROFILE", "Downloads"),
        "pictures": ("USERPROFILE", "Pictures"),
        "music": ("USERPROFILE", "Music"),
        "videos": ("USERPROFILE", "Videos"),
        "favorites": ("USERPROFILE", "Favorites"),
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

        if operation == "details":
            return self._file_details(target)

        if operation == "create_folder":
            return self._create_folder(data)

        if operation == "create_file":
            return self._create_file(data)

        if operation == "write_file":
            return self._write_file(data)

        if operation == "copy":
            return self._copy_item(data)

        if operation == "move":
            return self._move_item(data)

        if operation == "rename":
            return self._rename_item(data)

        return self._error(
            f"Unsupported file operation: {operation}"
        )

    # ==========================================
    # LIST DIRECTORY
    # ==========================================

    def _list_directory(self, data):

        path = self._resolve_path(data)

        if not os.path.exists(path):
            return self._error(
                f"Path does not exist: {path}"
            )

        if not os.path.isdir(path):
            return self._error(
                f"Path is not a folder: {path}"
            )

        try:
            entries = os.listdir(path)
            files = []
            folders = []

            for entry in entries:
                full_path = os.path.join(path, entry)

                try:
                    if os.path.isdir(full_path):
                        folders.append(entry)
                    else:
                        files.append(entry)
                except OSError:
                    continue

            folders.sort(key=str.lower)
            files.sort(key=str.lower)

            return self._success({
                "operation": "list",
                "path": path,
                "folders": folders,
                "files": files,
                "folder_count": len(folders),
                "file_count": len(files),
            })

        except PermissionError:
            return self._error("Permission denied.")

        except OSError as error:
            return self._error(str(error))

    # ==========================================
    # READ FILE
    # ==========================================

    def _read_file(self, data):

        path = self._resolve_file_path(data)

        if not os.path.exists(path):
            return self._error(
                f"File does not exist: {path}"
            )

        if not os.path.isfile(path):
            return self._error(
                f"Path is not a file: {path}"
            )

        extension = os.path.splitext(path)[1].lower()

        if extension not in self.TEXT_EXTENSIONS:
            return self._error(
                "Refusing to read unsupported file type: "
                f"{extension or '[no extension]'}"
            )

        try:
            file_size = os.path.getsize(path)

            if file_size > self.MAX_READ_SIZE:
                return self._error(
                    "File is too large to read safely. "
                    "Maximum size is "
                    f"{self.MAX_READ_SIZE // 1024 // 1024} MB."
                )

            with open(
                path,
                "r",
                encoding="utf-8",
                errors="replace",
            ) as file:
                content = file.read()

            return self._success({
                "operation": "read",
                "path": path,
                "size": file_size,
                "content": content,
            })

        except PermissionError:
            return self._error("Permission denied.")

        except OSError as error:
            return self._error(str(error))

    # ==========================================
    # SEARCH FILES
    # ==========================================

    def _search_files(self, data):

        if not isinstance(data, dict):
            return self._error(
                "Search requires a search dictionary."
            )

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
            return self._error(
                "Search query cannot be empty."
            )

        search_root = self._resolve_path(root)

        if not os.path.exists(search_root):
            return self._error(
                f"Search path does not exist: {search_root}"
            )

        if not os.path.isdir(search_root):
            return self._error(
                f"Search path is not a folder: {search_root}"
            )

        query_lower = query.lower()

        if extension and not extension.startswith("."):
            extension = f".{extension}"

        results = []

        try:
            for current_root, directories, files in os.walk(
                search_root,
                topdown=True,
            ):
                directories.sort(key=str.lower)
                files.sort(key=str.lower)

                for filename in files:

                    if len(results) >= self.MAX_SEARCH_RESULTS:
                        break

                    if (
                        extension
                        and not filename.lower().endswith(extension)
                    ):
                        continue

                    full_path = os.path.join(
                        current_root,
                        filename,
                    )

                    filename_matches = (
                        query_lower in filename.lower()
                    )

                    content_matches = False

                    if search_content and not filename_matches:
                        content_matches = (
                            self._file_contains_text(
                                full_path,
                                query_lower,
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
                            search_root,
                        )
                    except ValueError:
                        relative_path = filename

                    try:
                        file_size = os.path.getsize(full_path)
                    except OSError:
                        file_size = None

                    results.append({
                        "name": filename,
                        "path": full_path,
                        "relative_path": relative_path,
                        "size": file_size,
                        "match": (
                            "content"
                            if content_matches
                            else "filename"
                        ),
                    })

                if len(results) >= self.MAX_SEARCH_RESULTS:
                    break

            return self._success({
                "operation": "search",
                "query": query,
                "path": search_root,
                "content_search": search_content,
                "extension": extension or None,
                "result_count": len(results),
                "results": results,
                "truncated": (
                    len(results) >= self.MAX_SEARCH_RESULTS
                ),
            })

        except PermissionError:
            return self._error(
                "Permission denied during search."
            )

        except OSError as error:
            return self._error(str(error))

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
                errors="replace",
            ) as file:
                for line in file:
                    if query_lower in line.lower():
                        return True

        except (
            PermissionError,
            OSError,
            UnicodeError,
        ):
            return False

        return False

    # ==========================================
    # FILE DETAILS
    # ==========================================

    def _file_details(self, data):

        path = self._resolve_details_path(data)

        if not path:
            return self._error(
                "File path cannot be empty."
            )

        if not os.path.exists(path):
            return self._error(
                f"Path does not exist: {path}"
            )

        try:
            is_file = os.path.isfile(path)
            is_directory = os.path.isdir(path)
            stats = os.stat(path)
            size = stats.st_size

            extension = (
                os.path.splitext(path)[1].lower()
                if is_file
                else None
            )

            return self._success({
                "operation": "details",
                "name": os.path.basename(
                    os.path.normpath(path)
                ),
                "path": os.path.abspath(path),
                "extension": extension,
                "size": size,
                "size_human": self._format_size(size),
                "created": self._format_timestamp(
                    stats.st_ctime
                ),
                "modified": self._format_timestamp(
                    stats.st_mtime
                ),
                "accessed": self._format_timestamp(
                    stats.st_atime
                ),
                "is_file": is_file,
                "is_directory": is_directory,
            })

        except PermissionError:
            return self._error("Permission denied.")

        except OSError as error:
            return self._error(str(error))

    # ==========================================
    # CREATE FOLDER
    # ==========================================

    def _create_folder(self, data):

        if not isinstance(data, dict):
            return self._error(
                "Create folder requires a dictionary."
            )

        path = self._resolve_operation_path(
            data.get("path")
        )

        if not path:
            return self._error(
                "Folder path cannot be empty."
            )

        if os.path.exists(path):
            return self._error(
                f"Path already exists: {path}"
            )

        try:
            os.makedirs(path)

            return self._success({
                "operation": "create_folder",
                "path": os.path.abspath(path),
                "created": True,
            })

        except PermissionError:
            return self._error(
                "Permission denied."
            )

        except OSError as error:
            return self._error(str(error))

    # ==========================================
    # CREATE FILE
    # ==========================================

    def _create_file(self, data):

        if not isinstance(data, dict):
            return self._error(
                "Create file requires a dictionary."
            )

        path = self._resolve_operation_path(
            data.get("path")
        )

        if not path:
            return self._error(
                "File path cannot be empty."
            )

        content = str(
            data.get("content", "")
        )

        if os.path.exists(path):
            return self._error(
                f"Path already exists: {path}"
            )

        parent = os.path.dirname(path)

        if parent and not os.path.isdir(parent):
            return self._error(
                f"Parent folder does not exist: {parent}"
            )

        try:
            with open(
                path,
                "x",
                encoding="utf-8",
            ) as file:
                file.write(content)

            return self._success({
                "operation": "create_file",
                "path": os.path.abspath(path),
                "size": os.path.getsize(path),
                "created": True,
            })

        except FileExistsError:
            return self._error(
                f"Path already exists: {path}"
            )

        except PermissionError:
            return self._error(
                "Permission denied."
            )

        except OSError as error:
            return self._error(str(error))

    # ==========================================
    # WRITE FILE
    # ==========================================

    def _write_file(self, data):

        if not isinstance(data, dict):
            return self._error(
                "Write file requires a dictionary."
            )

        path = self._resolve_operation_path(
            data.get("path")
        )

        if not path:
            return self._error(
                "File path cannot be empty."
            )

        if os.path.isdir(path):
            return self._error(
                f"Path is a folder: {path}"
            )

        content = str(
            data.get("content", "")
        )

        overwrite = bool(
            data.get("overwrite", False)
        )

        if os.path.exists(path) and not overwrite:
            return self._error(
                "File already exists. "
                "Set 'overwrite' to true to replace it."
            )

        parent = os.path.dirname(path)

        if parent and not os.path.isdir(parent):
            return self._error(
                f"Parent folder does not exist: {parent}"
            )

        try:
            with open(
                path,
                "w",
                encoding="utf-8",
            ) as file:
                file.write(content)

            return self._success({
                "operation": "write_file",
                "path": os.path.abspath(path),
                "size": os.path.getsize(path),
                "overwritten": overwrite,
            })

        except PermissionError:
            return self._error(
                "Permission denied."
            )

        except OSError as error:
            return self._error(str(error))

    # ==========================================
    # COPY
    # ==========================================

    def _copy_item(self, data):

        if not isinstance(data, dict):
            return self._error(
                "Copy requires a dictionary."
            )

        source = self._resolve_operation_path(
            data.get("source")
        )
        destination = self._resolve_operation_path(
            data.get("destination")
        )

        overwrite = bool(
            data.get("overwrite", False)
        )

        if not source:
            return self._error(
                "Copy source cannot be empty."
            )

        if not destination:
            return self._error(
                "Copy destination cannot be empty."
            )

        if not os.path.exists(source):
            return self._error(
                f"Source does not exist: {source}"
            )

        if os.path.exists(destination) and not overwrite:
            return self._error(
                "Destination already exists. "
                "Set 'overwrite' to true to replace it."
            )

        try:
            if os.path.isdir(source):
                if os.path.exists(destination):
                    shutil.rmtree(destination)

                shutil.copytree(
                    source,
                    destination,
                )
            else:
                parent = os.path.dirname(destination)

                if parent and not os.path.isdir(parent):
                    return self._error(
                        f"Destination folder does not exist: {parent}"
                    )

                shutil.copy2(
                    source,
                    destination,
                )

            return self._success({
                "operation": "copy",
                "source": os.path.abspath(source),
                "destination": os.path.abspath(destination),
                "copied": True,
            })

        except PermissionError:
            return self._error(
                "Permission denied."
            )

        except OSError as error:
            return self._error(str(error))

    # ==========================================
    # MOVE
    # ==========================================

    def _move_item(self, data):

        if not isinstance(data, dict):
            return self._error(
                "Move requires a dictionary."
            )

        source = self._resolve_operation_path(
            data.get("source")
        )
        destination = self._resolve_operation_path(
            data.get("destination")
        )

        if not source:
            return self._error(
                "Move source cannot be empty."
            )

        if not destination:
            return self._error(
                "Move destination cannot be empty."
            )

        if not os.path.exists(source):
            return self._error(
                f"Source does not exist: {source}"
            )

        if os.path.exists(destination):
            return self._error(
                "Destination already exists. "
                "Move was cancelled."
            )

        parent = os.path.dirname(destination)

        if parent and not os.path.isdir(parent):
            return self._error(
                f"Destination folder does not exist: {parent}"
            )

        try:
            shutil.move(
                source,
                destination,
            )

            return self._success({
                "operation": "move",
                "source": os.path.abspath(source),
                "destination": os.path.abspath(destination),
                "moved": True,
            })

        except PermissionError:
            return self._error(
                "Permission denied."
            )

        except OSError as error:
            return self._error(str(error))

    # ==========================================
    # RENAME
    # ==========================================

    def _rename_item(self, data):

        if not isinstance(data, dict):
            return self._error(
                "Rename requires a dictionary."
            )

        source = self._resolve_operation_path(
            data.get("source")
        )
        destination = self._resolve_operation_path(
            data.get("destination")
        )

        if not source:
            return self._error(
                "Rename source cannot be empty."
            )

        if not destination:
            return self._error(
                "Rename destination cannot be empty."
            )

        if not os.path.exists(source):
            return self._error(
                f"Source does not exist: {source}"
            )

        if os.path.exists(destination):
            return self._error(
                "Destination already exists. "
                "Rename was cancelled."
            )

        try:
            os.rename(
                source,
                destination,
            )

            return self._success({
                "operation": "rename",
                "source": os.path.abspath(source),
                "destination": os.path.abspath(destination),
                "renamed": True,
            })

        except PermissionError:
            return self._error(
                "Permission denied."
            )

        except OSError as error:
            return self._error(str(error))

    # ==========================================
    # PATH HELPERS
    # ==========================================

    def _resolve_operation_path(self, data):

        if not data:
            return ""

        requested = str(data).strip()

        if not requested:
            return ""

        return self._resolve_file_path(requested)

    def _resolve_details_path(self, data):

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

    def _resolve_path(self, data):

        home = os.path.expanduser("~")

        if not data:
            return home

        requested = str(data).strip()

        if not requested:
            return home

        normalized = requested.lower()

        if normalized in self.HOME_ALIASES:
            return home

        if (
            os.name == "nt"
            and normalized in {
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
            }
        ):
            return self._resolve_windows_known_folder(
                normalized
            )

        if normalized in self.FOLDER_ALIASES:
            return os.path.join(
                home,
                self.FOLDER_ALIASES[normalized],
            )

        if normalized in self.ENVIRONMENT_HOME_ALIASES:
            return home

        requested = os.path.expandvars(requested)
        requested = os.path.expanduser(requested)

        if requested in {
            "/home/$USER",
            "/home/${USER}",
            "/home/user",
        }:
            return home

        normalized_expanded = requested.lower().strip()

        if normalized_expanded in self.FOLDER_ALIASES:
            return os.path.join(
                home,
                self.FOLDER_ALIASES[
                    normalized_expanded
                ],
            )

        return requested

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
            requested,
        )

        if canonical_name == "onedrive":

            onedrive = os.environ.get("OneDrive")

            if onedrive and os.path.isdir(onedrive):
                return onedrive

            return os.path.join(
                home,
                "OneDrive",
            )

        environment_name, default_folder = (
            self.WINDOWS_KNOWN_FOLDERS[
                canonical_name
            ]
        )

        base_path = os.environ.get(
            environment_name,
            home,
        )

        standard_path = os.path.join(
            base_path,
            default_folder,
        )

        if os.path.isdir(standard_path):
            return standard_path

        onedrive = os.environ.get("OneDrive")

        if onedrive:

            onedrive_path = os.path.join(
                onedrive,
                default_folder,
            )

            if os.path.isdir(onedrive_path):
                return onedrive_path

        return standard_path

    # ==========================================
    # RESPONSE HELPERS
    # ==========================================

    def _success(self, data):

        return {
            "success": True,
            "tool": self.name,
            "data": data,
            "error": None,
        }

    def _error(self, message):

        return {
            "success": False,
            "tool": self.name,
            "data": None,
            "error": message,
        }

    @staticmethod
    def _format_size(size):

        if size < 1024:
            return f"{size} B"

        if size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"

        if size < 1024 ** 3:
            return f"{size / (1024 ** 2):.2f} MB"

        return f"{size / (1024 ** 3):.2f} GB"

    @staticmethod
    def _format_timestamp(timestamp):

        return datetime.fromtimestamp(
            timestamp
        ).isoformat(
            sep=" ",
            timespec="seconds",
        )


if __name__ == "__main__":

    tool = FileTool()

    tests = [
        {
            "operation": "create_folder",
            "path": ".\\aegis_file_test",
        },
        {
            "operation": "create_file",
            "path": ".\\aegis_file_test\\notes.txt",
            "content": "AEGIS file operations test.",
        },
        {
            "operation": "write_file",
            "path": ".\\aegis_file_test\\notes.txt",
            "content": "Updated by AEGIS.",
            "overwrite": True,
        },
        {
            "operation": "details",
            "path": ".\\aegis_file_test\\notes.txt",
        },
    ]

    for test in tests:
        print(
            f"\nINPUT: {test}"
        )
        print(
            tool.execute(test)
        )