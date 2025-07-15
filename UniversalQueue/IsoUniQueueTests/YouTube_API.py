import requests

class YouTubeAPI:
    def __init__(self, api_keys=None):
        """
        Initializes the YouTubeAPI class with a list of API keys.
        Rotates through the keys to distribute quota usage.

        :param api_keys: List of YouTube Data API keys
        """
        if api_keys is None:
            api_keys = [
                "AIzaSyCGJ1UXzFF7QL3X5WHdMhWIGJjhu1BBqh8",
                "AIzaSyC948uX02ZYvomTfRfw9eSwQJDE9bnIId4",
                "AIzaSyCDAeaAOmP3M-TLn59923SGQTr7o1w1F4Y",
                "AIzaSyCxzo4ExRujDH9kv1SysovtSSWTBXKDFec",
                "AIzaSyAvOmpwSH-nePF4zeqEJwD8CfKX6dP4pTg"
            ]
        self.api_keys = api_keys  # List of API keys
        self.current_key_index = 0  # Index to track the current API key

    def get_api_key(self):
        """
        Rotates through the API keys and returns the current key.
        Updates the index to point to the next key for subsequent calls.

        :return: A YouTube Data API key
        """
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key

    def search_videos(self, query, max_results=4):
        """
        Searches for videos on YouTube using the YouTube Data API.

        :param query: The search query string
        :param max_results: The maximum number of results to return
        :return: A list of video metadata dictionaries
        :raises ValueError: If the API request fails
        """
        api_key = self.get_api_key()  # Get the current API key
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults={max_results}&key={api_key}"
        print(f"Making YouTube API request with key: {api_key}")  # Debugging log

        try:
            response = requests.get(url)
            print(f"YouTube API response status: {response.status_code}")  # Debugging log
            print(f"YouTube API response data: {response.text}")  # Debugging log

            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("items", []):
                    results.append({
                        "title": item["snippet"]["title"],
                        "artist": item["snippet"]["channelTitle"],
                        "video_url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
                        "platform": "YouTube"
                    })
                return results
            else:
                raise ValueError(f"Error fetching video search results: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Network error occurred: {str(e)}")