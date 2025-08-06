import requests
import logging

class YouTubeAPI:
    def __init__(self, api_keys=None):
        """
        Initializes the YouTubeAPI class with a list of API keys.
        Rotates through the keys to distribute quota usage.

        :param api_keys: List of YouTube Data API keys
        """
        if api_keys is None or not api_keys:
            raise ValueError("No YouTube API keys provided. Please run startup.py to configure your API key.")
            
        self.api_keys = api_keys  # List of API keys
        self.current_key_index = 0  # Index to track the current API key

    def _load_api_keys_from_config(self):
        """
        Load YouTube API keys from the config file created during startup
        
        :return: List of API keys or empty list if none found
        """
        try:
            # Navigate to config file from this location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, '../api_credentials.config')  # CHANGE: New path
            
            if not os.path.exists(config_path):
                logging.warning("Config file not found - no YouTube API keys available")
                return []
            
            with open(config_path, 'r') as file:
                for line in file:
                    if "YOUTUBE_API_KEY" in line and "=" in line:
                        api_key = line.split("=", 1)[1].strip()
                        if api_key and api_key != "":
                            logging.info("Successfully loaded YouTube API key from config")
                            return [api_key]  # Return as list for compatibility
            
            logging.warning("YouTube API key not found in config file")
            return []
            
        except Exception as e:
            logging.error(f"Error loading YouTube API key from config: {e}")
            return []

    def get_api_key(self):
        """
        Rotates through the API keys and returns the current key.
        Updates the index to point to the next key for subsequent calls.

        :return: A YouTube Data API key
        """
        if not self.api_keys:
            raise ValueError("No YouTube API keys available")
            
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
        
    def get_video_details(self, video_id):
        """
        Fetch detailed information about a specific YouTube video using its video ID.
        
        @param video_id: The YouTube video ID (e.g., "dQw4w9WgXcQ")
        @return: Dictionary containing video details
        @raises: Exception if video not found or API error occurs
        """
        try:
            # Use the YouTube Data API v3 videos endpoint
            url = f"https://www.googleapis.com/youtube/v3/videos"
            
            params = {
                'part': 'snippet,contentDetails',  # Get both snippet and content details
                'id': video_id,
                'key': self.get_api_key()  # Use your existing API key method
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            data = response.json()
            
            # Check if video was found
            if 'items' not in data or len(data['items']) == 0:
                raise ValueError(f"No video found with ID: {video_id}")
            
            # Extract video details
            video_item = data['items'][0]
            snippet = video_item['snippet']
            content_details = video_item['contentDetails']
            
            # Return structured video details
            return {
                'video_id': video_id,
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'title': snippet.get('title', 'Unknown Title'),
                'artist': snippet.get('channelTitle', 'Unknown Channel'),
                'description': snippet.get('description', ''),
                'duration': content_details.get('duration', 'PT0S'),  # ISO 8601 format (e.g., "PT4M13S")
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                'view_count': video_item.get('statistics', {}).get('viewCount', '0'),
                'channel_id': snippet.get('channelId', ''),
                'tags': snippet.get('tags', [])
            }
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error while fetching video details for {video_id}: {str(e)}")
            raise Exception(f"Failed to fetch video details: Network error")
        
        except ValueError as e:
            logging.error(f"Video not found: {str(e)}")
            raise e
        
        except Exception as e:
            logging.error(f"Unexpected error while fetching video details for {video_id}: {str(e)}")
            raise Exception(f"Failed to fetch video details: {str(e)}")