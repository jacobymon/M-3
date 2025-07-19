""" This module implements the Universal Queue class """
from time import sleep
""" This module allows us to log our errors"""
import logging

# from flask import Flask, request 
# from flask_cors import CORS, cross_origin
 
import json
import sys
import os

# path = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(path +"/Spotify_Interface")

# from Spotify_Interface.spotify_interface_class import Spotify_Interface_Class
from Song import Song

import threading

from YouTube_API import YouTubeAPI


# app = Flask(__name__)
# CORS(app) 

class UniversalQueue:
    """
    Stores all of the song requests in a queue order
    """

    def __init__(self):
        """
            creates a Universal Queue object
            intializes a queue object as an empty list
            initializes an instance of the spotify interface class
            in order to interact with song playback

            @attribute suspend_toggle: a boolean value where true suspends the
            queue from song requests and false allows

            @attribute pause_toggle: a boolean value where true indicates pausing, false is playing                                      
        """
        self.data = {}  # Dictionary to store songs with their IDs as keys

        #PSUEDO CODE FOR NOW UNTIL MOCK COMES: self.spotify = Spotify_Interface_Class()

        self.suspend_toggle = False

        self.pause_toggle = False

        #this is a MOCK for testing purposes!!!
        #look into real cookie in the future
        self.hostCookie = "host"

        self.idCount = 0

        # self.spotify = Spotify_Interface_Class()

        self.flush_exit = threading.Event()

        self.pause_exit = threading.Event()

        self.youtube_api = YouTubeAPI(api_key = "AIzaSyCvQt4I9nFifFCdhkf6aA7xwWTlI1V6LYE")

    def insert_youtube_song(self, video_id):
        """
        Inserts a YouTube song into the queue.

        @param video_id: The ID of the YouTube video.
        """
        try:
            # Get video details from YouTube API
            video_details = self.youtube_api.get_video_details(video_id)
            print(f"Video details: {video_details}")  # Debug log
            
            # Map YouTube data to the format expected by Song class
            song_data = {
                "status": 200,
                "search_results": {
                    "uri": video_details.get("video_url", f"https://www.youtube.com/watch?v={video_id}"),
                    "name": video_details.get("title", "Unknown Title"),
                    "artist": video_details.get("artist", "Unknown Artist"),
                    "s_len": self.parse_duration(video_details.get("duration", "PT0S")),
                    "album": "YouTube",  # Placeholder since YouTube doesn't have albums
                    "image": video_details.get("thumbnail", ""),  # Use thumbnail as image
                    "platform": "YouTube"
                }
            }
            
            print(f"Mapped song data: {song_data}")  # Debug log
            
            # Convert to JSON and create Song object
            song_json = json.dumps(song_data)
            song = Song(song_json)
            
            # Insert into queue
            self.insert(song)
            print(f"Successfully inserted YouTube song: {video_details.get('title', 'Unknown')}")
            
        except Exception as e:
            print(f"Error in insert_youtube_song: {str(e)}")
            raise e
    def insert(self, song, recover = False): 
        """
        Inserts a song into the queue with a unique ID using the song class's set_id() method.
        Calls update_UI().

        @param song: A song object containing attributes needed for UI and playback.
        @param recover: Boolean flag for recovery mode (doesn't write to file).
        """
        if recover == False:
            if self.suspend_toggle == False:
                song.set_id(self.idCount)
                self.idCount += 1  # Update the next ID to be unique
                self.data[song.id] = song  # Add song to dictionary
                self.write()
            else:
                raise ValueError('can not insert')
        else:  # Special recovery version (doesn't write())
            if self.suspend_toggle == False:
                song.set_id(self.idCount)
                self.idCount += 1  # Update the next ID to be unique
                self.data[song.id] = song  # Add song to dictionary
            else:
                raise ValueError('can not insert')
                


    # def flush_queue(self):
    #     """
    #     Goes through queue and plays songs or pauses, updating display queue
    #     as necessary by calling update_UI() 

        
    #     """
    #     #Queue the song for playback
    #     #while the queue is not empty
    #     #use the spotify interface instance to play the song at the front of queue
    #     #sleep until the song is finished playing, using a time with respect to song.s_len
    #     #if puase_queue == True use spotify interface instance to pause and stop timer
    #     #when song is finished delete it from queue
    #     #call update_UI()
    #     #call write()
    #     while len(self.data) != 0:
    #         self.spotify.play(self.data[0].uri)
    #         self.flush_exit.wait((self.data[0].s_len / 1000))
    #         print("WAIT ENDED")

    #         if self.pause_toggle == True:
    #             remaining_time = self.data[0].s_len - self.spotify.get_current_playback_info().progress_ms
    #             self.data[0].s_len = remaining_time
    #             self.pause_exit.wait()
    #             continue
                



    #         self.data = self.data[1:]

    def pause_queue(self):
        """
        allows us to pause the queu and play the queue.

        @return bool: true when queue is paused, false when queue is unpaused

        """

        if self.pause_toggle == False:
            self.pause_toggle = True
            
            self.spotify.pause()
            self.flush_exit.set()

        else:
            print("Queue is already paused")

    def unpause_queue(self):
        """
        allows us to pause the queu and play the queue.

        @return bool: true when queue is paused, false when queue is unpaused

        """
        if self.pause_toggle == True:
            self.pause_toggle = False 
            
            self.spotify.unpause()
            self.pause_exit.set()



        else:
            print("Queue is currently Playing")


    def update_ui(self):
        """
        Sends the current state of the queue to the UI for all users. It will handle requests from users
        with long polling and will be called after any change is made to the queue. This is due
        axios only being able to send requests to the back end.
        

        @return the current state of the queue to all users
        """
        #loop through the users and send them the current state of the queue
        
    def request_update(self, user):
        """
        allows a specific user to request the current state of the queue to be displayed for them
        (ie when they first click on to the website link)
        throw a 400 bad request error if the queue can't be sent
        
        @return: the current state of the queue to the specific user
        """
        #try to send current queue state to user
        #except Exceptions as e:
             #send e to front end 

    def remove_from_queue(self, id):
        """
         a privileged host-only function that removes songs from queue.
        removing the current song goes to the next song.

        Throw exception when the song we want to remove is not in the Universal queue

        calls update_ui

        @param index: index recieved from host corresponding song the want removed from queue
       
        """
        # MOCKED verify cookie is host's, would pass the cookie in from request instead of self.cookie
        if self.cookie_verifier(self.hostCookie):
            # Check if the song exists in the dictionary
            if id in self.data:
                # If removing the first song in the queue, handle special logic
                if id == next(iter(self.data)):  # First song in the queue
                    # self.flush_exit.set()  # Uncomment if flush logic is implemented
                    pass
                # Remove the song from the dictionary
                del self.data[id]
                self.write()
            else:
                raise ValueError('invalid id')        

       

    def cookie_verifier(self, cookie):
        """
        verifies that the privileged functions are being called by the host.
        throw error when return is false.
        
        If the cookie is actually the hosts
        and this is false we log the error and shut down. (Our host is not recognized as the host anymore!).
        ***Not sure how we would know this though

        @param cookie: cookie that is being checked to be the hosts, created in startup component

        @return Bool: True when the cookie matches the host's else and error
        """
        #check status code first (we would do this in routes.py with flask)
        if cookie == self.hostCookie:
            return True
        else:
            return False

    def set_suspend_toggle(self, flag):
        """
        privileged host-only function

        toggle for the queue for accepting song requests or not.

        @param flag: a boolean value that is true when the queue is NOT accepting requests
        false when the queue is accepting requests.
        
        """
        #MOCKED verify cookie is host's, would pass the cookie in from request instead
        #of self.cookie
        if self.cookie_verifier(self.hostCookie):

            if flag == True:
                self.suspend_toggle = True

            else:
                self.suspend_toggle = False

    def clear_queue(self):
        """
        privileged host-only function

        sets the queue back to an empty list
        """

    def write(self):
        """
        Writes the queue to a file in JSON format on the host's local machine.
        O(n) complexity, where n is len(self.data).
        """
        data = []
        for song in self.data.values():
            songObject = {
                "uri": song.uri,
                "s_len": song.s_len,
                "name": song.name,
                "album": song.album,
                "artist": song.artist
            }
            data.append(songObject)

        with open("Write.json", "w") as json_file:
            json.dump(data, json_file)
    

          

    def recover(self, instance):
        """
        recovers the current state of the queue. in case of a system crash.

        @param file: the file we are reading from (same file as the one we wrote to)
        """
        #when there's a system crash
        #read from the file
        #re insert all of the song objects back into a new queue
        #update_ui

        #initialize a new queue
        newUniQueue = UniversalQueue()

        try:
            with open("Write.json", "r+") as json_file:
                json_file_data = json_file.read()
                myList = json.loads(json_file_data)
                for myDict in myList:
                    myJson = json.dumps(myDict)
                    SongObject = Song(myJson, True) #need special version of song initializer that takes in just the song data snippet
                    newUniQueue.insert(SongObject, True) #need special version of insert since it originally rewrites Write.json
                
                #update the UI (website queue)

                return newUniQueue

        except FileNotFoundError:
            print(f"Error: File 'Write.json' not found.")   
