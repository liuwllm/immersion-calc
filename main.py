from prompt_toolkit import prompt
from anilistcomplete import AniListCompleter
from api_utils import get_anilist_id, get_jimaku_id, get_subtitle_text
from jpreadability import calc_readability

def main():
    try:
        while True:
            try:
                title = prompt("Search anime (Ctrl+C to exit): ", completer=AniListCompleter())
                print(f"You selected: {title}")
                anilist_id = get_anilist_id(title)
                jimaku_id = get_jimaku_id(anilist_id)
                text = get_subtitle_text(anilist_id, jimaku_id)
                level = calc_readability(text)

                with open('output.txt', 'w', encoding='utf-8') as file:
                    file.write(text)

                print(f"The difficulty level of this anime series is \033[1m{level}\033[0m.")


            except KeyboardInterrupt:
                print("\n[Interrupted — press Ctrl+C to exit]")
                break
            except EOFError:
                print("\nGoodbye!")
                break
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
