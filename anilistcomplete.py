from prompt_toolkit.completion import Completer, Completion
import requests

class AniListCompleter(Completer):
    def get_completions(self, document, complete_event):
        query = document.text.strip()
        if not query:
            return

        # GraphQL query to AniList
        graphql_query = {
            "query": """
            query ($search: String) {
              Page(perPage: 10) {
                media(search: $search, type: ANIME) {
                  title {
                    romaji
                  }
                }
              }
            }
            """,
            "variables": {"search": query}
        }

        try:
            response = requests.post("https://graphql.anilist.co", json=graphql_query, timeout=3)
            response.raise_for_status()
            data = response.json()

            titles = data["data"]["Page"]["media"]
            for anime in titles:
                title = anime["title"]["romaji"]
                yield Completion(title, start_position=-len(query))
        except Exception as e:
            # You can print(e) or log errors if desired
            return
