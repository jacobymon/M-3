import json


class Song:
    def __init__(self, json_data, recover=False):
        """
        Creates a song object.

        @param json_data: JSON string or dictionary containing song attributes.
        @param recover: Boolean flag for recovery mode.
        """
        # Load JSON data into a Python dictionary
        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {e}")
        elif isinstance(json_data, dict):
            data = json_data  # Already a dictionary
        else:
            raise ValueError(f"json_data must be string or dict, got {type(json_data)}")

        # Handle recovery mode or direct playlist JSON
        if recover or "name" in data:
            # Direct mapping from playlist JSON
            self.name = data.get("name", "")
            self.artist = data.get("artist", "")
            self.albumname = data.get("albumname", "")
            self.album = data.get("album", self.albumname)  # Default to albumname if album is not present
            self.albumcover = data.get("albumcover", "")
            self.platform = data.get("platform", "Spotify")
            self.uri = data.get("uri", "")
            self.video_id = data.get("video_id", "")
            self.submissionID = data.get("submissionID", 0)
            self.s_len = data.get("s_len", 0)
            self.id = data.get("id", None)
        else:
            # Handle API response with `search_results`
            status = data.get("status", 200)  # Default to 200 if status is missing
            if status != 200:
                raise ValueError("status of json not acceptable")

            self.platform = data.get("platform", "Spotify")  # Default to Spotify if platform is not provided

            if self.platform == "YouTube":
                # Handle YouTube-specific metadata
                search_results = data.get("search_results", {})
                self.uri = search_results.get("video_url") or search_results.get("uri", "")
                self.name = search_results.get("title") or search_results.get("name", "")
                self.artist = search_results.get("channel_name") or search_results.get("artist", "")
                self.s_len = search_results.get("duration") or search_results.get("s_len", 0)
                self.albumname = "YouTube"
                self.album = "YouTube"  # Default album for YouTube
                self.albumcover = search_results.get("thumbnail_url") or search_results.get("albumcover", "")
                self.video_id = search_results.get("video_id", "")
            else:
                # Handle Spotify-specific metadata
                search_results = data.get("search_results", {})
                self.uri = search_results.get("uri", "")
                self.s_len = search_results.get("s_len", 0)
                self.name = search_results.get("name", "")
                self.albumname = search_results.get("album", "")
                self.album = search_results.get("album", self.albumname)  # Default to albumname if album is not present
                self.artist = search_results.get("artist", "")
                self.albumcover = search_results.get("albumcover", "")
                self.video_id = ""

            self.id = None
            self.submissionID = data.get("submissionID", 0)

    def set_id(self, id):
        """
        Setter for the song's unique ID. Called when inserting a song into the universal queue.

        @param id: Unique ID created by the universal queue.
        """
        self.id = id
        self.submissionID = id  # ADD THIS LINE - Set submissionID to match id
        print(f"Set song ID and submissionID to: {id}")  # Debug line

    def to_dict(self):
        """
        Convert song to dictionary for JSON serialization and frontend consumption.
        
        @return: Dictionary representation of the song
        """
        return {
            'name': getattr(self, 'name', ''),
            'artist': getattr(self, 'artist', ''),
            'albumname': getattr(self, 'albumname', ''),
            'album': getattr(self, 'album', self.albumname),  # Default to albumname if album is not present
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