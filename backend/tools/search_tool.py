import webbrowser

from backend.tools.base_tool import BaseTool


class SearchTool(BaseTool):

    name = "search"

    description = "Search the web using Google"

    def execute(self, data):

        query = data.strip()

        if not query:
            return "What would you like me to search for?"

        url = "https://www.google.com/search?q=" + query.replace(" ", "+")

        webbrowser.open(url)

        return f"Searching Google for: {query}"
