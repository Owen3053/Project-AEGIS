import webbrowser


class SearchTool:

    def search(self, query):

        query = query.strip()

        if not query:
            return "What would you like me to search for?"

        url = "https://www.google.com/search?q=" + query.replace(" ", "+")

        webbrowser.open(url)

        return f"Searching Google for: {query}"
