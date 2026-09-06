import os
import shutil
import subprocess
import webbrowser


class AutomationManager:

    def __init__(self):

        self.apps = {
            "calculator": [
                "calc.exe",
            ],
            "calc": [
                "calc.exe",
            ],
            "notepad": [
                "notepad.exe",
            ],
            "paint": [
                "mspaint.exe",
            ],
            "explorer": [
                "explorer.exe",
            ],
            "file explorer": [
                "explorer.exe",
            ],
            "terminal": [
                "wt.exe",
                "cmd.exe",
            ],
            "command prompt": [
                "cmd.exe",
            ],
            "powershell": [
                "powershell.exe",
            ],
            "vscode": [
                r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe",
                r"C:\Program Files\Microsoft VS Code\Code.exe",
            ],
            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],
            "edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ],
            "firefox": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            ],
        }

        self.websites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://github.com",
            "gmail": "https://mail.google.com",
            "chatgpt": "https://chatgpt.com",
        }

        self.folder_aliases = {
            "desktop": "Desktop",
            "documents": "Documents",
            "downloads": "Downloads",
            "pictures": "Pictures",
            "photos": "Pictures",
            "music": "Music",
            "videos": "Videos",
            "favorites": "Favorites",
            "onedrive": "OneDrive",
        }

    # ==========================================
    # PUBLIC OPEN METHOD
    # ==========================================

    def open(self, target):

        if target is None:
            return "What would you like me to open?"

        target = str(target).strip()

        if not target:
            return "What would you like me to open?"

        normalized = target.lower()

        # ==========================================
        # KNOWN APPLICATIONS
        # ==========================================

        if normalized in self.apps:

            return self._open_application(
                normalized
            )

        # ==========================================
        # KNOWN FOLDERS
        # ==========================================

        if normalized in self.folder_aliases:

            return self._open_folder_alias(
                normalized
            )

        # ==========================================
        # KNOWN WEBSITES
        # ==========================================

        if normalized in self.websites:

            return self._open_url(
                self.websites[normalized],
                normalized,
            )

        # ==========================================
        # DIRECT URL
        # ==========================================

        if (
            normalized.startswith("http://")
            or normalized.startswith("https://")
        ):

            return self._open_url(
                target,
                target,
            )

        # ==========================================
        # EXISTING FILE OR FOLDER PATH
        # ==========================================

        expanded = os.path.expandvars(
            os.path.expanduser(target)
        )

        if os.path.exists(expanded):

            return self._open_path(
                expanded
            )

        # ==========================================
        # PATH-LIKE TARGET THAT DOES NOT EXIST
        # ==========================================

        if self._looks_like_path(target):

            return (
                f"I couldn't find the file or folder: "
                f"{target}"
            )

        return (
            f"I don't know how to open "
            f"'{target}' yet."
        )

    # ==========================================
    # APPLICATIONS
    # ==========================================

    def _open_application(self, target):

        candidates = self.apps[target]

        for candidate in candidates:

            expanded = os.path.expandvars(
                os.path.expanduser(candidate)
            )

            executable = (
                shutil.which(expanded)
                if not os.path.isabs(expanded)
                else expanded
            )

            if executable and os.path.isfile(executable):

                try:
                    subprocess.Popen(
                        [executable],
                        shell=False
                    )

                    return f"Opening {target}."

                except OSError as error:
                    return (
                        f"I found {target}, "
                        f"but couldn't open it: "
                        f"{error}"
                    )

        return (
            f"I couldn't find {target} "
            f"on this computer."
        )

    # ==========================================
    # FOLDERS
    # ==========================================

    def _open_folder_alias(self, target):

        home = os.path.expanduser("~")

        if target == "onedrive":

            onedrive = os.environ.get(
                "OneDrive"
            )

            if onedrive and os.path.isdir(
                onedrive
            ):

                return self._open_path(
                    onedrive
                )

            fallback = os.path.join(
                home,
                "OneDrive"
            )

            if os.path.isdir(fallback):

                return self._open_path(
                    fallback
                )

            return (
                "I couldn't find your "
                "OneDrive folder."
            )

        folder_name = self.folder_aliases[
            target
        ]

        standard_path = os.path.join(
            home,
            folder_name
        )

        if os.path.isdir(standard_path):

            return self._open_path(
                standard_path
            )

        onedrive = os.environ.get(
            "OneDrive"
        )

        if onedrive:

            onedrive_path = os.path.join(
                onedrive,
                folder_name
            )

            if os.path.isdir(onedrive_path):

                return self._open_path(
                    onedrive_path
                )

        return (
            f"I couldn't find your "
            f"{target} folder."
        )

    # ==========================================
    # PATH OPENING
    # ==========================================

    def _open_path(self, path):

        path = os.path.abspath(
            os.path.expandvars(
                os.path.expanduser(path)
            )
        )

        if not os.path.exists(path):

            return (
                f"I couldn't find: {path}"
            )

        if os.name == "nt":

            try:
                os.startfile(path)

                if os.path.isdir(path):
                    return (
                        f"Opening folder: {path}"
                    )

                return f"Opening file: {path}"

            except OSError as error:
                return (
                    f"I couldn't open '{path}': "
                    f"{error}"
                )

        return (
            "Opening files and folders this way "
            "is currently supported on Windows only."
        )

    # ==========================================
    # WEBSITES
    # ==========================================

    def _open_url(self, url, display_name):

        try:

            opened = webbrowser.open(
                url,
                new=2
            )

            if opened:
                return (
                    f"Opening {display_name}."
                )

            return (
                f"I couldn't open {display_name}."
            )

        except Exception as error:

            return (
                f"I couldn't open {display_name}: "
                f"{error}"
            )

    # ==========================================
    # HELPERS
    # ==========================================

    @staticmethod
    def _looks_like_path(target):

        return (
            "\\" in target
            or "/" in target
            or target.startswith(".")
            or target.startswith("~")
            or (
                len(target) >= 2
                and target[1] == ":"
            )
        )


if __name__ == "__main__":

    automation = AutomationManager()

    tests = [
        "calculator",
        "notepad",
        "desktop",
        "documents",
        "youtube",
        "github",
        "C:\\Windows",
        "https://www.google.com",
        "unknown_application",
    ]

    for test in tests:

        print(
            f"\nINPUT: {test}"
        )

        print(
            automation.open(test)
        )