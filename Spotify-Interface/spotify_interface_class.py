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

    def play(self, track_id): 
        """
        plays a song on the spotify playback

        @attribute uri: The uri of the song to be played
        @attribute spotify: The spotify tekore object
        """
        #Play the uri of the song on playback
        print(track_id)
        self.spotify.playback_start_tracks(track_ids=[track_id], device_id=self.device_id) 
        current_track = self.spotify.playback_currently_playing()
        if current_track.item.id == track_id:
            return 0
        else: 
            #Should raise an exception here later down the line
            return 1

    def pause(self): 
        """
        pauses the spotify playback
        @attribute spotify: The spotify tekore object
        """
        #pause the playback
        #If you pause while the player is already paused, it causes a 403 error
        self.spotify.playback_pause()
        current_state = self.spotify.playback()

        # Might need to add a sleep call here to make sure the playback actually starts before the check
        # occurs

        if current_state.is_playing == False:
            return 0
        else: 
            return 1

    def unpause(self):
        """
        unpauses the spotify playback
        @attribute spotify: The spotify tekore object
        """
        #unpause the playback
        self.spotify.playback_resume()

        current_state = self.spotify.playback()
        # Might need to add a sleep call here to make sure the playback actually starts before the check
        # occurs
        if current_state.is_playing:
            return 0
        else: 
            return 1

    def return_results(self, search_string):
        """
        unpauses the spotify playback

        @param search_string: The string that is fed into the spotify search API endpoint
        @attribute spotify: The spotify tekore object
        """
        #return song objects to the front-end for the user to select from in the UI

        tracks, = self.spotify.search(query=search_string, limit=NUM_ITEMS)

        return tracks
