import webbrowser

from backend.tools.base_tool import BaseTool


class SearchTool(BaseTool):

    name = "search"

    description = "Search the web using Google"

    def execute(self, data):

        if data is None:
            return self.failure(
                "What would you like me to search for?"
            )

        query = str(data).strip()

        if not query:
            return self.failure(
                "What would you like me to search for?"
            )

        url = (
            "https://www.google.com/search?q="
            + query.replace(" ", "+")
        )

        webbrowser.open(url)

        return self.success({
            "query": query,
            "message": "Google search opened in the browser."
        })