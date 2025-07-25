import json

class Song:
    def __init__(self, json_data, recover=False):
        """
        Creates a song object.

        @param json_data: JSON string or dictionary containing song attributes.
        @param recover: Boolean flag for recovery mode.
        """
        # Loading JSON data into a Python dictionary
        if isinstance(json_data, str):
            try:
                dict = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {e}")
        elif isinstance(json_data, dict):
            dict = json_data  # Already a dictionary
        else:
            raise ValueError(f"json_data must be string or dict, got {type(json_data)}")

        if recover == False:
            status = dict.get('status')

            if status == 200:
                self.platform = dict.get('platform', 'Spotify')  # Default to Spotify if platform is not provided

                if self.platform == "YouTube":
                    # Handle YouTube-specific metadata
                    search_results = dict.get('search_results', {})
                    self.uri = search_results.get('video_url') or search_results.get('uri')
                    self.name = search_results.get('title') or search_results.get('name')
                    self.artist = search_results.get('channel_name') or search_results.get('artist')
                    self.s_len = search_results.get('duration') or search_results.get('s_len')
                    self.album = search_results.get('album') or "YouTube"  # Set default album for YouTube
                    self.albumname = "YouTube"  # Add this for frontend compatibility
                    self.albumcover = search_results.get('thumbnail_url') or search_results.get('albumcover', '')
                    self.video_id = search_results.get('video_id', '')
                else:
                    # Handle Spotify-specific metadata
                    search_results = dict.get('search_results', {})
                    self.uri = search_results.get('uri')
                    self.s_len = search_results.get('s_len')
                    self.name = search_results.get('name')
                    self.album = search_results.get('album')
                    self.albumname = search_results.get('album')  # Add this for frontend compatibility
                    self.artist = search_results.get('artist')
                    self.albumcover = search_results.get('albumcover', '')
                    self.video_id = ''  # No video ID for Spotify

                self.id = None
                self.submissionID = dict.get('submissionID', 0)
            else:
                raise ValueError('status of json not acceptable')
        else:
            # Recovery mode - song data is directly in the dictionary
            self.uri = dict.get('uri')
            self.s_len = dict.get('s_len')
            self.name = dict.get('name')
            self.album = dict.get('album')
            self.albumname = dict.get('albumname') or dict.get('album')  # Add this
            self.artist = dict.get('artist')
            self.platform = dict.get('platform', 'Spotify')  # Default to Spotify if platform is not provided
            self.albumcover = dict.get('albumcover', '')
            self.video_id = dict.get('video_id', '')
            self.submissionID = dict.get('submissionID', 0)
            self.id = None

    def set_id(self, id):
        """
        Setter for the song's unique ID. Called when inserting a song into the universal queue.

        @param id: Unique ID created by the universal queue.
        """
        self.id = id

    def to_dict(self):
        """
        Convert song to dictionary for JSON serialization and frontend consumption.
        
        @return: Dictionary representation of the song
        """
        return {
            'name': getattr(self, 'name', ''),
            'artist': getattr(self, 'artist', ''),
            'albumname': getattr(self, 'albumname', getattr(self, 'album', '')),
            'albumcover': getattr(self, 'albumcover', ''),
            'platform': getattr(self, 'platform', 'Spotify'),
            'uri': getattr(self, 'uri', ''),
            'video_id': getattr(self, 'video_id', ''),
            'submissionID': getattr(self, 'submissionID', 0),
            's_len': getattr(self, 's_len', 0),
            'id': getattr(self, 'id', None)
        }

    def __str__(self):
        """String representation of the song"""
        return f"{self.name} by {self.artist} ({self.platform})"

    def __repr__(self):
        """Detailed string representation for debugging"""
        return f"Song(name='{self.name}', artist='{self.artist}', platform='{self.platform}', uri='{self.uri}')"