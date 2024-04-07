""" This module implements the Universal Queue class """
import tekore as tk

from auth import get_user_token
from player import get_first_available_device

#Method called on startup to retrieve the user token
token = get_user_token()
NUM_ITEMS = 20

class Spotify_Interface_Class:
    """
    Serves as a stanard interface / wrapper class around the spotify tekore object
    """

    def __init__(self): 
        """
        Creates a Spotify tekore object
        gets the device_id if the tekore object is successfully made for calling all useful methods

        @attribute spotify: The spotify tekore object
        @attribute device_id: The device id of the physical device running the external spotify session
        """
        self.spotify = tk.Spotify(token)
        self.device_id = get_first_available_device(self.spotify).id
        pass

    def play(self, uri): 
        """
        plays a song on the spotify playback

        @attribute uri: The uri of the song to be played
        @attribute spotify: The spotify tekore object
        """
        #Play the uri of the song on playback
        self.spotify.playback_start_tracks([uri], self.device_id) 

    def pause(self): 
        """
        pauses the spotify playback
        @attribute spotify: The spotify tekore object
        """
        #pause the playback
        self.spotify.playback_pause()

    def unpause(self):
        """
        unpauses the spotify playback
        @attribute spotify: The spotify tekore object
        """
        #unpause the playback
        self.spotify.playback_resume()

    def return_results(self, search_string):
        """
        unpauses the spotify playback

        @param search_string: The string that is fed into the spotify search API endpoint
        @attribute spotify: The spotify tekore object
        """
        #return song objects to the front-end for the user to select from in the UI

        tracks, = self.spotify.search(query=search_string, limit=NUM_ITEMS)
        return tracks


    
