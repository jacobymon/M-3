""" This module implements the Universal Queue class """
import time
""" This module allows us to log our errors"""
import json
import logging
import os
import sys
import isodate

# from flask_socketio import SocketIO, emit
from Youtube_Interface_Class.Youtube_Interface_Class import YouTube_Interface_Class


from flask import Flask, request
from flask_cors import CORS, cross_origin

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path +"/Spotify_Interface")

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path + "/IsoUniQueueTests")  # Add IsoUniQueueTests directory to the Python path


from YouTube_API import YouTubeAPI

from flask import Flask, request, jsonify

import socket
import threading

from Song import Song
from Spotify_Interface.spotify_interface_class import Spotify_Interface_Class

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_ip = s.getsockname()[0]
s.close()

print(local_ip)


# Initialize Flask app with SocketIO
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# socketio = SocketIO(app, cors_allowed_origins="*")

class UniversalQueue:
    """
    Stores all of the song requests in a queue order
    """

    API_KEYS = [
    "AIzaSyCvQt4I9nFifFCdhkf6aA7xwWTlI1V6LYE",
    "AIzaSyC948uX02ZYvomTfRfw9eSwQJDE9bnIId4",
    "AIzaSyCDAeaAOmP3M-TLn59923SGQTr7o1w1F4Y",
    "AIzaSyCxzo4ExRujDH9kv1SysovtSSWTBXKDFec",
    "AIzaSyAvOmpwSH-nePF4zeqEJwD8CfKX6dP4pTg"
]

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
        self.data = []

        #PSUEDO CODE FOR NOW UNTIL MOCK COMES: self.spotify = Spotify_Interface_Class()

        self.suspend_toggle = False

        self.pause_toggle = False

        #this is a MOCK for testing purposes!!!
        self.hostCookie = "host"

        self.idCount = 0

        self.spotify = Spotify_Interface_Class()
        self.youtube = YouTube_Interface_Class()  # Add this line


        self.youtube_api = YouTubeAPI(api_keys=self.API_KEYS)

        self.flush_exit = threading.Event()

        self.pause_exit = threading.Event()

    def insert(self, song, recover=False): 
        """
        When queue not suspended
        inserts a song into the queue with a unique id using the song classes set_id() method
        and calls update_UI()

        @param song: a song object that contains all of the attributes needed
        to display info to UI and playback
        """
        
        try:
            if recover == False:
                if self.suspend_toggle == False:
                    song.set_id(self.idCount)
                    self.idCount += 1
                    self.data.append(song)
                    self.write()

                    # CHANGE: Only start flush_queue if no songs are playing
                    if len(self.data) == 1 and not hasattr(self, 'flush_thread'):
                        # Start flush_queue in a separate thread
                        self.flush_thread = threading.Thread(target=self.flush_queue, daemon=True)
                        self.flush_thread.start()
                    
                    print(f"Song inserted successfully. Queue now has {len(self.data)} songs")
                    return 0
                else:
                    print("Queue is suspended, cannot insert")
                    return 1
        
            else: #special recovery version (doesn't write())
                if self.suspend_toggle == False:
                    song.set_id(self.idCount)
                    self.idCount += 1 #update the next id to be unique for the next set
                    self.data.append(song)

                    if len(self.data) == 1:
                        self.flush_queue()
                    
                    print(f"Song recovered successfully. Queue now has {len(self.data)} songs")
                    return 0  # ADD THIS - Return 0 for success
                else:
                    print("Queue is suspended, cannot recover")
                    return 1  # ADD THIS - Return 1 for failure
                    
        except Exception as e:
            print(f"Error inserting song: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1  # ADD THIS - Return 1 for error
                

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
        
    def parse_duration(self, duration):
        """
        Helper function to parse ISO 8601 duration strings into microseconds
        """
        try:
            # Convert ISO 8601 duration to total seconds, then to microseconds
            return int(isodate.parse_duration(duration).total_seconds() * 1_000_000)
        except Exception as e:
            logging.error(f"Error parsing duration: {str(e)}")
            return 0
                


    # def flush_queue(self):
    #     """
    #     Goes through queue and plays songs or pauses, updating display queue
    #     as necessary by calling update_UI() 

    #     """
        #Queue the song for playback
        #while the queue is not empty
        #use the spotify interface instance to play the song at the front of queue
        #sleep until the song is finished playing, using a time with respect to song.s_len
        #if puase_queue == True use spotify interface instance to pause and stop timer
        #when song is finished delete it from queue
        #call update_UI()
        #call write()

        # just_unpaused = False

        # while len(self.data) != 0:
        #     if just_unpaused == False:
        #         self.spotify.play(self.data[0].uri)
        #     else: 
        #         just_unpaused = False
        #     self.flush_exit.wait((self.data[0].s_len / 1000))
        #     print("WAIT ENDED")

        #     if self.pause_toggle == True:
        #         remaining_time = self.data[0].s_len - self.spotify.get_current_playback_info().progress_ms
        #         self.data[0].s_len = remaining_time
        #         self.pause_exit.wait()
        #         just_unpaused = True

        #         continue
            
        #     self.data = self.data[1:]

    def flush_queue(self):
        """
        Updated flush_queue to run continuously and handle queue changes
        """
        print("Starting flush_queue background service")
        
        while True:  # Run continuously
            if len(self.data) == 0:
                # No songs in queue, wait a bit and check again
                time.sleep(1)
                continue
                
            current_song = self.data[0]
            print(f"Playing song: {current_song.name} (Platform: {getattr(current_song, 'platform', 'Spotify')})")
            
            try:
                # Start playing the song
                if hasattr(current_song, 'platform') and current_song.platform == "YouTube":
                    video_id = self.youtube.extract_video_id(current_song.uri)
                    if video_id:
                        print(f"Playing YouTube video: {video_id}")
                        self.youtube.set_video_duration(current_song.s_len / 1_000_000)
                        self.youtube.play(video_id)
                    else:
                        print(f"Could not extract video ID from: {current_song.uri}")
                else:
                    print(f"Playing Spotify song: {current_song.uri}")
                    self.spotify.play(current_song.uri)
                    
                # Calculate wait time based on platform
                if hasattr(current_song, 'platform') and current_song.platform == "YouTube":
                    # YouTube duration is in microseconds
                    wait_time = current_song.s_len / 1_000_000
                    print(f"YouTube song - Waiting {wait_time} seconds for song to finish")
                else:
                    # Spotify duration is in milliseconds  
                    wait_time = current_song.s_len / 1_000
                    print(f"Spotify song - Waiting {wait_time} seconds for song to finish")
                
                # MAIN WAITING LOOP - This is where the magic happens
                while True:  # ← ADD THIS INNER LOOP
                    # Wait for the song to finish or be interrupted
                    song_finished = self.flush_exit.wait(wait_time)
                    
                    # Check if we were interrupted by pause
                    if self.pause_toggle == True:  
                        print("Song was paused, handling pause logic...")
                        
                        # Calculate remaining time if Spotify
                        if not (hasattr(current_song, 'platform') and current_song.platform == "YouTube"):
                            try:
                                playback_info = self.spotify.get_current_playback_info()
                                print(f"Playback info: {playback_info}")
                                
                                if playback_info and hasattr(playback_info, 'progress_ms') and playback_info.progress_ms is not None:
                                    progress_ms = playback_info.progress_ms
                                    
                                    # Check if s_len is in microseconds or milliseconds
                                    if current_song.s_len > 10000000:  # If > 10M, likely microseconds
                                        song_duration_ms = current_song.s_len / 1000  # Convert to milliseconds
                                        print(f"Song duration (converted from microseconds): {song_duration_ms}ms")
                                    else:
                                        song_duration_ms = current_song.s_len  # Already in milliseconds
                                        print(f"Song duration (already in milliseconds): {song_duration_ms}ms")
                                    
                                    print(f"Current progress: {progress_ms}ms")
                                    print(f"Original song length: {current_song.s_len}")
                                    
                                    # Calculate remaining time in original units
                                    if current_song.s_len > 10000000:  # Was in microseconds
                                        remaining_time_ms = song_duration_ms - progress_ms
                                        remaining_time_microseconds = remaining_time_ms * 1000
                                        current_song.s_len = max(remaining_time_microseconds, 0)
                                        wait_time = remaining_time_ms / 1000  # Update wait_time for next iteration
                                        print(f"Updated remaining time: {remaining_time_microseconds} microseconds ({remaining_time_ms}ms)")
                                    else:  # Was in milliseconds
                                        remaining_time_ms = song_duration_ms - progress_ms
                                        current_song.s_len = max(remaining_time_ms, 0)
                                        wait_time = remaining_time_ms / 1000  # Update wait_time for next iteration
                                        print(f"Updated remaining time: {remaining_time_ms}ms")
                                        
                                else:
                                    print("No valid playback info available, keeping original song length")
                                    
                            except Exception as e:
                                print(f"Error getting playback info: {e}")
                                print("Keeping original song length due to error")
                        
                        # Wait for unpause
                        print("Waiting for unpause signal...")
                        self.pause_exit.wait()
                        print("Unpaused, continuing song with remaining time...")
                        
                        # DON'T break or continue - just loop back to wait for remaining time
                        print(f"Will now wait {wait_time} seconds for remaining song time")
                        
                    else:
                        # Song finished naturally (timeout occurred)
                        print(f"Song finished naturally: {current_song.name}")
                        break  # Break out of inner while loop
                
                # Song finished naturally, remove from queue
                print(f"Song finished: {current_song.name}")
                
                # Stop the current song to prevent overlap
                if hasattr(current_song, 'platform') and current_song.platform == "YouTube":
                    try:
                        self.youtube.stop()  # Stop YouTube playback
                    except Exception as e:
                        print(f"Error stopping YouTube: {e}")
                else:
                    try:
                        self.spotify.pause()  # Pause Spotify to prevent overlap
                    except Exception as e:
                        print(f"Error pausing Spotify: {e}")
                
                # Remove the finished song from queue
                self.data = self.data[1:]
                self.write()
                
                print(f"Queue now has {len(self.data)} songs remaining")
                
            except Exception as e:
                print(f"Error playing song {current_song.name}: {e}")
                # Remove problematic song and continue
                self.data = self.data[1:]
                self.write()
                continue
            
            # If no more songs, break the loop
            if len(self.data) == 0:
                print("Queue is empty, stopping flush_queue")
                if hasattr(self, 'flush_thread'):
                    delattr(self, 'flush_thread')
                break

    def pause_queue(self, cookie):
        """
        allows us to pause the queu and play the queue.

        @return bool: true when queue is paused, false when queue is unpaused

        """

        if not self.cookie_is_valid(cookie):
            raise ValueError('invalid id')

        if self.pause_toggle == False:
            self.pause_toggle = True
            
            self.spotify.pause()
            self.flush_exit.set()
            self.flush_exit.clear()
        


    def unpause_queue(self, cookie):
        """
        allows us to pause the queue and play the queue.

        @return bool: true when queue is paused, false when queue is unpaused
        """

        if not self.cookie_is_valid(cookie):
            raise ValueError('invalid id')

        if self.pause_toggle == True:
            self.pause_toggle = False 
            
            # Resume Spotify playback from where it was paused
            try:
                self.spotify.unpause()  # ← ADD THIS BACK - Let Spotify resume naturally
            except Exception as e:
                print(f"Error resuming Spotify: {e}")
            
            self.pause_exit.set()
            self.pause_exit.clear()
            
            print("Queue unpaused - Spotify should resume from where it left off")
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

    def remove_from_queue(self, id, cookie):
        """
         a privileged host-only function that removes songs from queue.
        removing the current song goes to the next song.

        Throw exception when the song we want to remove is not in the Universal queue

        calls update_ui

        @param index: index recieved from host corresponding song the want removed from queue
       
        """
        #IMPORTANT removal of first song starts playing next song is checked manually
        #IMPORTANT this operation is curretnly O(n). Look into making it O(1) with dictionary
        if self.cookie_is_valid(cookie):

            for s in self.data:
                if s.id == id:
                    #If we're removing the first item in the queue which is currently playing, just kill the
                    #current wait call on flush queue as it will remove the first item 
                    if s.id == self.data[0].id:
                        self.flush_exit.set()
                        self.flush_exit.clear()
                        #if the last song is being deleted, stop playback
                        if len(self.data) == 1:
                            self.spotify.pause()
                        
                    #If we're removing anything else, just remove it from the queue
                    else:
                        
                        self.data.remove(s)
                        
                        
                    self.write()
                    return
            #If no song retuns
            raise ValueError(f"id {id} was not a song in the queue")
        else:
            raise ValueError(f"Cookie {cookie} was invalid")

        

       

    def cookie_is_valid(self, cookie):
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
            print(f"Given cookie {cookie} did not match host cookie {self.hostCookie}")
            return False

    def set_suspend_toggle(self, flag, cookie):
        """
        privileged host-only function

        toggle for the queue for accepting song requests or not.

        @param flag: a boolean value that is true when the queue is NOT accepting requests
        false when the queue is accepting requests.
        
        """
        #MOCKED verify cookie is host's, would pass the cookie in from request instead
        #of self.cookie
        if self.cookie_is_valid(cookie):

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
        Writes the queue to a file in json format on
        the hosts local machine
        O(n) complexity, where n is len(self.data)

        @param file: the file we are writing to, created during startup 
        """ 

        #break down the song objects into jsonifiable data
        #write to the file
        data = []
        for i in range(len(self.data)):
            songObject = {
                    "uri": self.data[i].uri,
                    "s_len": self.data[i].s_len,
                    "name" : self.data[i].name,
                    "album": self.data[i].album,
                    "artist": self.data[i].artist
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



UQ = UniversalQueue()
# List of API keys
API_KEYS = [
                "AIzaSyCGJ1UXzFF7QL3X5WHdMhWIGJjhu1BBqh8",
                "AIzaSyC948uX02ZYvomTfRfw9eSwQJDE9bnIId4",
                "AIzaSyCDAeaAOmP3M-TLn59923SGQTr7o1w1F4Y",
                "AIzaSyCxzo4ExRujDH9kv1SysovtSSWTBXKDFec",
                "AIzaSyAvOmpwSH-nePF4zeqEJwD8CfKX6dP4pTg"
]

# Initialize YouTubeAPI with multiple keys
youtube_api = YouTubeAPI(api_keys=API_KEYS)

UQ.youtube_api = youtube_api
# UQ.youtube = YouTube_Interface_Class(socketio=None)  # Add this line


# # Add WebSocket event handlers
# @socketio.on('connect')
# def handle_connect():
#     print('Client connected to WebSocket')

# @socketio.on('disconnect')
# def handle_disconnect():
#     print('Client disconnected from WebSocket')

# @socketio.on('youtube_song_ended')
# def handle_youtube_song_ended(data):
#     """
#     Handle when a YouTube song ends on the frontend
#     """
#     print(f"YouTube song ended: {data.get('video_id')}")
#     # You can add logic here to move to the next song
#     # For example: UQ.remove_current_song()

# @socketio.on('youtube_position_update')
# def handle_position_update(data):
#     """
#     Handle position updates from frontend YouTube player
#     """
#     if hasattr(UQ, 'youtube') and UQ.youtube:
#         UQ.youtube.update_position(data.get('position', 0))

@app.route('/', methods=['GET'])
@cross_origin()
def root():
    return jsonify({"status": 200, "message": "Server is running!"})


@app.route('/return_results', methods=['GET', 'POST'])
@cross_origin()
def return_results():
    search_string = request.args.get('search_string')
    response = {'search_string': UQ.spotify.return_data(search_string)}
    print(response)
    return response


@app.route('/return_results_from_url', methods=['GET', 'POST'])
@cross_origin()
def return_results_from_url():
    url = request.args.get('spotify_url')
    # response = {'spotify_url': UQ.spotify.from_url(url)}

    print(UQ.spotify.from_url(url)['results'][0])
    pre_dump = {
        'status': 200,
        'search_results': UQ.spotify.from_url(url)['results'][0]
    }
    song_data = json.dumps(pre_dump)
    print(song_data)
    song = Song(song_data)

    UQ.insert(song)
    return song_data

@app.route('/submit_song', methods=['GET', 'POST'])
@cross_origin()
def submit_song():
    song_data = request.get_json()
    print("ORIGINAL SONG DATA:", song_data)
    
    song_data['search_results']['name'] = song_data['search_results']['title']
    
    print(f"Song duration before Song creation: {song_data['search_results'].get('s_len', 'NOT FOUND')}")
    
    song_data = json.dumps(song_data)
    song = Song(song_data)
    
    print(f"Song duration after Song creation: {song.s_len}")
    print(f"Song duration in seconds: {song.s_len / 1_000_000}")
    
    UQ.insert(song)
    return song_data

@app.route('/pause', methods=['GET', 'POST'])
@cross_origin()
def pause_route():
    UQ.pause_queue()

@app.route('/unpause', methods=['GET', 'POST'])
@cross_origin()
def unpause_route():
    UQ.unpause_queue()

@app.route('/request_update', methods=['GET'])
@cross_origin()
def request_update():
    try:
        songs_data = []
        for song in UQ.data:
            song_dict = song.to_dict()
            # print(f"Sending song to frontend: {song_dict}")  # Debug log
            songs_data.append(song_dict)
        
        print(f"Total songs in response: {len(songs_data)}")  # Debug log
        return jsonify(songs_data)
    except Exception as e:
        print(f"Error in request_update: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/verify_host', methods=['GET', 'POST'])
@cross_origin()
def verify_host():
    if request.method == 'GET':
        incomingIP = request.remote_addr
        print(f"Incoming IP: {incomingIP}, Local IP: {local_ip}")
        
        # Accept connections from the actual IP, localhost, or 127.0.0.1
        if incomingIP in [local_ip, '127.0.0.1', 'localhost', '::1']:
            return {"updateIsHost": True, "updateCookie": UQ.hostCookie}
        else:
            return {"updateIsHost": False, "updateCookie": ""}

@app.route('/remove_song', methods=['GET', 'POST'])
@cross_origin()
def remove_song():
    id_to_remove = int(request.json['id'])
    cookie =request.json['cookie']
    UQ.remove_from_queue(id_to_remove, cookie)
    return str(id)

@app.route('/suspend_queue', methods=['GET', 'POST'])
@cross_origin()
def suspend_queue():
    cookie =request.json['cookie']
    UQ.set_suspend_toggle(True, cookie)
    return ""

@app.route('/unsuspend_queue', methods=['GET', 'POST'])
@cross_origin()
def unsuspend_queue():
    cookie =request.json['cookie']
    UQ.set_suspend_toggle(False, cookie)
    return ""

@app.route('/pause_music', methods=['GET', 'POST'])
@cross_origin()
def pause_music():
    cookie =request.json['cookie']
    UQ.pause_queue(cookie)
    return ""

@app.route('/unpause_music', methods=['GET', 'POST'])
@cross_origin()
def unpause_music():
    cookie =request.json['cookie']
    UQ.unpause_queue(cookie)
    return ""

@app.route('/youtube_search', methods=['GET'])
@cross_origin()
def youtube_search():
    search_string = request.args.get('search_string')
    if not search_string:
        return jsonify({"status": 400, "response": "Search string is required."})

    try:
        results = youtube_api.search_videos(search_string, max_results=4)  # Perform a search
        return jsonify({"status": 200, "results": results})
    except Exception as e:
        logging.error(f"Error in YouTube search: {str(e)}")
        return jsonify({"status": 500, "response": "An internal server error occurred."})

"""
Helper function to parse ISO 8601 duration strings into microseconds
"""
def parse_duration(duration):
    try:
        # Convert ISO 8601 duration to total seconds, then to microseconds
        return int(isodate.parse_duration(duration).total_seconds() * 1_000_000)  # Convert to microseconds
    except Exception as e:
        logging.error(f"Error parsing duration: {str(e)}")
        return 0

# @app.route('/youtube_play', methods=['POST'])
# @cross_origin()
# def youtube_play():
#     try:
#         data = request.json
#         video_id = data.get('video_id')
#         start_time = data.get('start_time', 0)
        
#         if hasattr(UQ, 'youtube') and UQ.youtube:
#             result = UQ.youtube.play(video_id, start_time)
#             return jsonify({
#                 "status": 200 if result == 0 else 500,
#                 "response": "YouTube play command sent"
#             })
#         else:
#             return jsonify({"status": 500, "response": "YouTube interface not available"})
#     except Exception as e:
#         return jsonify({"status": 500, "response": str(e)})

# @app.route('/youtube_pause', methods=['POST'])
# @cross_origin()
# def youtube_pause():
#     try:
#         if hasattr(UQ, 'youtube') and UQ.youtube:
#             result = UQ.youtube.pause()
#             return jsonify({
#                 "status": 200 if result == 0 else 500,
#                 "response": "YouTube pause command sent"
#             })
#         else:
#             return jsonify({"status": 500, "response": "YouTube interface not available"})
#     except Exception as e:
#         return jsonify({"status": 500, "response": str(e)})

# @app.route('/youtube_unpause', methods=['POST'])
# @cross_origin()
# def youtube_unpause():
#     try:
#         if hasattr(UQ, 'youtube') and UQ.youtube:
#             result = UQ.youtube.unpause()
#             return jsonify({
#                 "status": 200 if result == 0 else 500,
#                 "response": "YouTube unpause command sent"
#             })
#         else:
#             return jsonify({"status": 500, "response": "YouTube interface not available"})
#     except Exception as e:
#         return jsonify({"status": 500, "response": str(e)})

@app.route('/youtube_submit_url', methods=['POST'])
@cross_origin()
def youtube_submit_url():
    print("=== YOUTUBE SUBMIT URL ROUTE CALLED ===")

    try:
        data = request.json
        url = data.get('youtube_url')
        
        if not url:
            return jsonify({"status": 400, "response": "No URL provided"})
        
        # Extract video ID and get metadata (your existing code)
        video_id = None
        if "youtube.com/watch?v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
        
        if not video_id:
            return jsonify({"status": 400, "response": "Invalid YouTube URL"})
        
        print(f"Extracted video ID: {video_id}")
        
        # Get video info from YouTube API
        video_title = f"YouTube Video ({video_id})"
        channel_name = "YouTube Channel"
        thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/default.jpg"
        duration = 180000000  # Default: 3 minutes in microseconds
        
        if hasattr(UQ, 'youtube_api') and UQ.youtube_api:
            try:
                video_info = UQ.youtube_api.get_video_details(video_id)
                if video_info:
                    video_title = video_info.get('title', video_title)
                    channel_name = video_info.get('channel_title', channel_name)
                    thumbnail_url = video_info.get('thumbnail_url', thumbnail_url)
                    
                    # Convert ISO 8601 duration to microseconds
                    duration_iso = video_info.get('duration', 'PT3M')
                    if duration_iso and duration_iso.startswith('PT'):
                        try:
                            import isodate
                            duration_seconds = isodate.parse_duration(duration_iso).total_seconds()
                            duration = int(duration_seconds * 1_000_000)  # Convert to microseconds
                            print(f"Converted duration {duration_iso} to {duration} microseconds")
                        except Exception as duration_error:
                            print(f"Duration conversion error: {duration_error}")
                            duration = 180000000  # Default fallback
                    
            except Exception as e:
                print(f"YouTube API error: {e}")
        
        # Create the song data structure
        song_data = {
            "status": 200,
            "platform": "YouTube",
            "search_results": {
                "video_url": url,
                "uri": url,
                "title": video_title,
                "name": video_title,
                "channel_name": channel_name,
                "artist": channel_name,
                "duration": duration,  # Now in microseconds
                "s_len": duration,     # Now in microseconds
                "album": "YouTube",
                "thumbnail_url": thumbnail_url,
                "albumcover": thumbnail_url,
                "video_id": video_id
            },
            "submissionID": UQ.idCount
        }
        
        print(f"Creating YouTube song with data: {song_data}")
        
        # Create Song object
        song = Song(song_data, recover=False)
        print(f"Created song object: {song}")
        
       # Insert into queue - this now returns immediately!
        result = UQ.insert(song)
        
        if result is None or result == 0:
            # Return immediately - don't wait for song to play
            return jsonify({
                "status": 200, 
                "response": "YouTube song added successfully",
                "song_info": song.to_dict()
            })
        else:
            return jsonify({"status": 500, "response": "Failed to add song to queue"})
            
    except Exception as e:
        print(f"Error in youtube_submit_url: {str(e)}")
        return jsonify({"status": 500, "response": str(e)})

@app.route('/test_youtube_song', methods=['POST'])
@cross_origin()
def test_youtube_song():
    try:
        # Create a simple test YouTube song
        song_data = {
            "status": 200,
            "platform": "YouTube",
            "search_results": {
                "uri": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "video_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "name": "Test Song",
                "title": "Test Song",
                "artist": "Test Artist",
                "channel_name": "Test Artist",
                "album": "YouTube",
                "albumcover": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
                "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
                "video_id": "dQw4w9WgXcQ",
                "s_len": 213000,
                "duration": 213000
            },
            "submissionID": UQ.idCount
        }
        
        print(f"Test song data: {song_data}")
        
        song = Song(song_data, recover=False)
        print(f"Created test song: {song}")
        
        result = UQ.insert(song)
        print(f"Insert result: {result}")
        
        return jsonify({
            "status": 200,
            "response": "Test song added",
            "song": song.to_dict()
        })
        
    except Exception as e:
        print(f"Error in test: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": 500, "response": str(e)})
    
with open(path + '/../m3-frontend/.env', 'w') as f_obj:
    f_obj.write('REACT_APP_BACKEND_IP="'+local_ip+'"')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)  # Change from socketio.run to app.run