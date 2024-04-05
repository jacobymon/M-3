from enum import Enum
import tekore as tk

from auth import get_user_token
from player import get_first_available_device


class Song(Enum):
    def __init__(self, uri, s_len, s_name, album): 
        self.uri = uri
        self.s_len = s_len
        self.s_name = s_name
        self.album = album

#Method called on startup to retrieve the user token
token = get_user_token()
NUM_ITEMS = 20

class Spotify_Interface_Class:

    def __init__(self): 
        self.spotify = tk.Spotify(token)
        self.device_id = get_first_available_device(self.spotify).id
        pass

    def get_first_available_device(self):
        available_devices = self.spotify.playback_devices()
        return available_devices[0] 

    def play(self, uri): 
        #Play the uri of the song on playback
        self.spotify.playback_start_tracks([uri], self.device_id) 
        pass

    def pause(self): 
        #pause the playback
        self.spotify.playback_pause()

    def unpause(self):
        #unpause the playback
        self.spotify.playback_resume()

    def return_results(self, search_string):
        #return song objects to the front-end for the user to select from in the UI

        tracks, = self.spotify.search(query=search_string, limit=NUM_ITEMS)
        return tracks


    
