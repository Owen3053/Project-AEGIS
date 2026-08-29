import os
import subprocess
import webbrowser


class AutomationManager:

    def __init__(self):
        self.apps = {
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "notepad": "notepad.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "vscode": r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe",
        }

    def open(self, target):
        target = target.lower().strip()

        # Open known applications
        if target in self.apps:
            command = os.path.expandvars(self.apps[target])

            try:
                subprocess.Popen(command)
                return f"Opening {target}."
            except FileNotFoundError:
                return f"I couldn't find {target} on this computer."

        # Open common Windows folders
        folders = {
            "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
            "documents": os.path.join(os.path.expanduser("~"), "Documents"),
            "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        }

        if target in folders:
            path = folders[target]

            if os.path.exists(path):
                os.startfile(path)
                return f"Opening {target}."

            return f"I couldn't find your {target} folder."

        # Open websites
        websites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://github.com",
        }

        if target in websites:
            webbrowser.open(websites[target])
            return f"Opening {target}."

        return f"I don't know how to open '{target}' yet."
