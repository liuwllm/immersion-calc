import requests, os, pysubs2, time, math, re
from config import JIMAKU_KEY, UPLOAD_FOLDER

def get_anilist_id(title):
    url = "https://graphql.anilist.co"
    query = """
    query ($search: String) {
      Media(search: $search, type: ANIME) {
        id
        title {
          romaji
          english
          native
        }
      }
    }
    """
    variables = {"search": title}

    try:
        response = requests.post(url, json={"query": query, "variables": variables})
        response.raise_for_status()
        data = response.json()

        media = data.get("data", {}).get("Media")
        if media:
            return media['id']
        else:
            print("Anime not found.")
            return None
    except requests.RequestException as e:
        print("Request failed:", e)
        return None

def get_number_of_episodes(anilist_id):
    url = "https://graphql.anilist.co"
    query = """
    query ($id: Int) {
      Media(id: $id, type: ANIME) {
        id
        title {
          romaji
        }
        episodes
      }
    }
    """
    variables = {"id": anilist_id}

    try:
        response = requests.post(url, json={"query": query, "variables": variables})
        response.raise_for_status()
        data = response.json()

        media = data.get("data", {}).get("Media")
        if media:
            print(f"Anime: {media['title']['romaji']}")
            print(f"Number of Episodes: {media['episodes']}")
            return media['episodes']
        else:
            print("Anime not found.")
            return None
    except requests.RequestException as e:
        print("Request failed:", e)
        return None

def get_jimaku_id(showId):
    jimakuKey = JIMAKU_KEY
    searchUrl = "https://jimaku.cc/api/entries/search"
    searchHeaders = { "Authorization": jimakuKey }
    searchParams = { "anilist_id": showId }
    searchResponse = requests.get(searchUrl, headers=searchHeaders, params=searchParams).json()
    jimakuId = searchResponse[0]['id']

    return jimakuId

def get_with_backoff(url, headers, params):
    for i in range(5):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 429:
            retry_after = math.ceil(float(response.headers.get("x-ratelimit-reset-after", 2)))
            time.sleep(retry_after)
        else:
            return response
    raise Exception("Too many retries, still getting 429.")

def clean_text(text):
    japanese_only = re.sub(
      r'[^\u3040-\u309F\u30A0-\u30FF\uFF66-\uFF9F\u4E00-\u9FFF\u3000-\u303F\uFF01-\uFF60「」、。]+', 
      '', 
      text
    )
    return japanese_only

def get_subtitle_text(showId, jimakuId):
    jimakuKey = JIMAKU_KEY
    episodes = get_number_of_episodes(showId)

    res = ""

    for ep in range(episodes):
      epNo = ep + 1
      filesUrl = f"https://jimaku.cc/api/entries/{jimakuId}/files"
      filesHeader = { "Authorization": jimakuKey }
      filesParams = { "episode": epNo }

      try:
        filesResponse = requests.get(filesUrl, headers=filesHeader, params=filesParams)
        print(filesResponse)
        filesResponse.raise_for_status()
      except requests.exceptions.HTTPError as err:
        if filesResponse.status_code == 404:
          print(f"Subtitles for episode {epNo} was not found (404).")
          continue
        elif filesResponse.status_code == 429:
          retry_after = math.ceil(float(filesResponse.headers.get("x-ratelimit-reset-after")))
          print(f"Rate limited. Retry after {retry_after} seconds.")
          time.sleep(retry_after)
          filesResponse = get_with_backoff(filesUrl, filesHeader, filesParams)
        else:
          print(f"HTTP error occurred: {err}")

      subtitles = filesResponse.json()

      found = False
      for entry in subtitles:
        subUrl = entry['url']
        print(subUrl)
        if subUrl.endswith(".ass"):
          subType = ".ass"
          found = True
          break
        elif subUrl.endswith(".srt"):
          subType = ".srt"
          found = True
          break
        else:
          continue
      
      if not found:
        continue
      
      subResponse = requests.get(subUrl).content
      subPath = os.path.join(UPLOAD_FOLDER, f'subtitle{subType}')
      with open(subPath, 'wb') as file:
          file.write(subResponse)
      subs = pysubs2.load(subPath)
      lines = [event.text for event in subs.events]
      combinedText = "".join(lines)
      clean = clean_text(combinedText)
      res += clean
    
    return res