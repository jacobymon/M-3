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
    # Global variable to store latest YouTube progress
    latest_youtube_progress = {
        "current_time": 0,
        "duration": 0,
        "remaining_seconds": 0,
        "timestamp": 0,
        "video_id": ""
    }


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
        self.suspend_toggle = False
        self.pause_toggle = False
        self.hostCookie = "host"
        self.idCount = 0

        self.spotify = Spotify_Interface_Class()
        self.youtube = YouTube_Interface_Class()

        # CHANGE: Load API keys dynamically from config
        api_keys = self.load_api_keys_from_config()  # Call as method
        if api_keys:
            self.youtube_api = YouTubeAPI(api_keys=api_keys)
            print(f"YouTube API initialized with {len(api_keys)} API key(s)")
        else:
            print("Warning: No YouTube API keys available - YouTube functionality disabled")
            self.youtube_api = None

        self.flush_exit = threading.Event()
        self.pause_exit = threading.Event()

    def load_api_keys_from_config(self):
        """
        Load YouTube API key from config file created during startup
        """
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            CONFIG_FILE = os.path.join(path, 'api_credentials.config')
            
            if not os.path.exists(CONFIG_FILE):
                print("Config file not found - YouTube API key not available")
                return []
            
            with open(CONFIG_FILE, 'r') as file:
                for line in file:
                    if "YOUTUBE_API_KEY" in line and "=" in line:
                        api_key = line.split("=", 1)[1].strip()
                        if api_key and api_key != "":
                            print("Successfully loaded YouTube API key from config")
                            return [api_key]  # Return as list for compatibility
            
            print("YouTube API key not found in config file")
            return []
            
        except Exception as e:
            print(f"Error loading YouTube API key: {e}")
            return []

    
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
        Main queue processing method
        """
        while True:
            try:
                if len(self.data) == 0:
                    print("Queue is empty, waiting for songs...")
                    
                    # Make sure all playback is stopped when queue is empty
                    try:
                        if hasattr(self, 'youtube'):
                            print("Stopping YouTube interface (empty queue)")
                            self.youtube.stop()
                        print("Pausing Spotify (empty queue)")
                        self.spotify.pause()
                    except Exception as e:
                        if "403" not in str(e) and "Player command failed" not in str(e):
                            print(f"Error stopping playback on empty queue: {e}")
                    
                    time.sleep(1)
                    continue
                    
                current_song = self.data[0]
                print(f"=== STARTING SONG PLAYBACK ===")
                print(f"Queue length: {len(self.data)}")
                print(f"Now playing: {current_song.name} (ID: {current_song.submissionID})")
                print(f"Song platform: {getattr(current_song, 'platform', 'Spotify')}")
                
                # Store the current song ID to track if it gets removed
                current_song_id = current_song.submissionID
                
                # Start playing the song
                if hasattr(current_song, 'platform') and current_song.platform == "YouTube":
                    video_id = self.youtube.extract_video_id(current_song.uri)
                    if video_id:
                        print(f"Playing YouTube video: {video_id}")
                        self.youtube.set_video_duration(current_song.s_len / 1_000_000)
                        self.youtube.play(video_id)
                        current_song.start_time = time.time()
                    else:
                        print(f"Could not extract video ID from: {current_song.uri}")
                        self.data.pop(0)
                        self.write()
                        continue
                else:
                    print(f"Playing Spotify song: {current_song.uri}")
                    self.spotify.play(current_song.uri)
                    current_song.start_time = time.time()
                    
                # Calculate wait time based on platform
                if hasattr(current_song, 'platform') and current_song.platform == "YouTube":
                    wait_time = current_song.s_len / 1_000_000
                    print(f"YouTube song - Waiting {wait_time} seconds for song to finish")
                else:
                    wait_time = current_song.s_len / 1_000
                    print(f"Spotify song - Waiting {wait_time} seconds for song to finish")
                
                # MAIN WAITING LOOP
                while True:
                    print(f"=== WAITING FOR SONG EVENT (queue length: {len(self.data)}) ===")
                    print(f"Current song ID being tracked: {current_song_id}")
                    
                    # Wait for the song to finish or be interrupted
                    song_finished = self.flush_exit.wait(wait_time)
                    
                    print(f"Wait finished. song_finished={song_finished}, queue_length={len(self.data)}")
                    
                    # FIRST: Check if queue became empty (manual removal of last song)
                    if len(self.data) == 0:
                        print("Queue became empty during wait - manual removal detected")
                        print("Breaking to empty queue handler")
                        break  # Exit inner loop and go back to empty queue handling
                    
                    # SECOND: Check if the current song was manually removed
                    elif len(self.data) > 0 and self.data[0].submissionID != current_song_id:
                        print(f"Current song (ID: {current_song_id}) was manually removed")
                        print(f"New first song: {self.data[0].name} (ID: {self.data[0].submissionID})")
                        print("Breaking to start next song")
                        break  # Exit inner loop and start next song
                    
                    # THIRD: Check if we were interrupted by pause
                    elif self.pause_toggle == True:  
                        print("Song was paused, handling pause logic...")
                        # Your existing pause handling code...
                        # (keep all the existing pause logic here)
                        
                        # Wait for unpause
                        print("Waiting for unpause signal...")
                        while self.pause_toggle:
                            time.sleep(0.1)
                        
                        print("Queue unpaused, continuing...")
                        
                    else:
                        # Song finished naturally
                        print(f"Song finished naturally: {current_song.name}")
                        
                        # Remove if it still exists and is still the current song
                        if (len(self.data) > 0 and 
                            hasattr(self.data[0], 'submissionID') and 
                            self.data[0].submissionID == current_song_id):
                            
                            print(f"Removing naturally finished song: {current_song.name}")
                            self.data.pop(0)
                            self.write()
                            print(f"Queue after natural finish: {len(self.data)} songs")
                            
                            # If this was the last song, stop playback
                            if len(self.data) == 0:
                                print("Last song finished naturally - stopping all playback")
                                try:
                                    if hasattr(current_song, 'platform') and current_song.platform == "YouTube":
                                        if hasattr(self, 'youtube'):
                                            self.youtube.stop()
                                    else:
                                        self.spotify.pause()
                                except Exception as e:
                                    if "403" not in str(e) and "Player command failed" not in str(e):
                                        print(f"Error stopping playback after last song: {e}")
                        else:
                            print("Song was already removed manually, skipping natural removal")
                        
                        print("Breaking to start next song or handle empty queue")
                        break  # Exit inner loop
                        
            except Exception as e:
                print(f"Error in flush_queue: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)

    def pause_queue(self, cookie):
        """
        Pause the queue - works for both Spotify and YouTube
        """
        if not self.cookie_is_valid(cookie):
            raise ValueError('invalid id')

        if self.pause_toggle == False:
            self.pause_toggle = True
            
            # Pause the appropriate platform
            if len(self.data) > 0:
                current_song = self.data[0]
                if hasattr(current_song, 'platform') and current_song.platform == "YouTube":
                    print("Pausing YouTube playback via backend")
                    try:
                        # Get current playback time from frontend
                        # This would require a separate call or websocket communication
                        print("YouTube pause - time tracking will be handled in flush_queue")
                    except Exception as e:
                        print(f"Error pausing YouTube: {e}")
                else:
                    print("Pausing Spotify playback")
                    try:
                        self.spotify.pause()
                    except Exception as e:
                        print(f"Error pausing Spotify: {e}")
            
            self.flush_exit.set()
            self.flush_exit.clear()
            print("Queue paused")

    def unpause_queue(self, cookie):
        """
        Unpause the queue - works for both Spotify and YouTube
        """
        if not self.cookie_is_valid(cookie):
            raise ValueError('invalid id')

        if self.pause_toggle == True:
            self.pause_toggle = False 
            
            # Resume the appropriate platform
            if len(self.data) > 0:
                current_song = self.data[0]
                if hasattr(current_song, 'platform') and current_song.platform == "YouTube":
                    print("Resuming YouTube playback via backend")
                    try:
                        # YouTube resume logic - let the frontend handle the actual playback
                        # The flush_queue will continue with the remaining time
                        pass
                    except Exception as e:
                        print(f"Error resuming YouTube: {e}")
                else:
                    print("Resuming Spotify playback")
                    try:
                        self.spotify.unpause()
                    except Exception as e:
                        print(f"Error resuming Spotify: {e}")
            
            self.pause_exit.set()
            self.pause_exit.clear()
            
            print("Queue unpaused")
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
        A privileged host-only function that removes songs from queue.
        """
        if not self.cookie_is_valid(cookie):
            raise ValueError('invalid id')

        print(f"=== REMOVE FROM QUEUE DEBUG ===")
        print(f"Trying to remove song with ID: {id}")
        
        for s in self.data:
            song_id = getattr(s, 'id', None)
            submission_id = getattr(s, 'submissionID', None)
            
            if song_id == id or submission_id == id:
                print(f"Found matching song: {s.name} (id: {song_id}, submissionID: {submission_id})")
                
                # If we're removing the first item in the queue (currently playing)
                if s == self.data[0]:
                    print("Removing currently playing song")
                    
                    # Check if this is the last song in the queue
                    if len(self.data) == 1:
                        print("This is the last song - manual removal")
                        
                        # DON'T stop YouTube here - frontend already stopped it
                        # Only stop Spotify since it's controlled by backend
                        try:
                            if hasattr(s, 'platform') and s.platform == "YouTube":
                                print("YouTube song - frontend already stopped it")
                                # Just reset the backend state without sending stop signal
                                self.current_video_id = None
                                self.is_playing = False
                                self.is_paused = False
                            else:
                                print("Stopping Spotify playback (last song)")
                                self.spotify.pause()
                        except Exception as e:
                            print(f"Error stopping playback: {e}")
                        
                        # Remove the song from queue
                        self.data.remove(s)
                        self.write()
                        
                        # Signal flush_queue to exit
                        print("Signaling flush_queue to stop (empty queue)")
                        self.flush_exit.set()
                        self.flush_exit.clear()
                        
                    else:
                        print("Removing current song, moving to next")
                        
                        # For YouTube, don't send stop signal - frontend already stopped
                        try:
                            if hasattr(s, 'platform') and s.platform == "YouTube":
                                print("YouTube song - frontend already stopped, just resetting state")
                                # Reset backend state without sending signals
                                self.current_video_id = None
                                self.is_playing = False
                                self.is_paused = False
                            else:
                                print("Pausing Spotify playback for removal")
                                self.spotify.pause()
                        except Exception as e:
                            print(f"Error stopping playback: {e}")
                        
                        # Remove the song from queue
                        self.data.remove(s)
                        self.write()
                        
                        # Signal flush_queue to start next song
                        print("Signaling flush_queue to start next song")
                        self.flush_exit.set()
                        self.flush_exit.clear()
                
                else:
                    # Remove non-current songs normally
                    print("Removing non-current song from queue")
                    self.data.remove(s)
                    self.write()
                
                print(f"Song removed successfully. Queue now has {len(self.data)} songs")
                return
        
        raise ValueError(f"Song with ID {id} was not found in the queue")   

       

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

@app.route('/youtube_pause', methods=['POST'])
@cross_origin()
def youtube_pause():
    """Pause YouTube playback"""
    try:
        cookie = request.json['cookie']
        
        if not UQ.cookie_is_valid(cookie):
            return jsonify({"status": 400, "response": "Invalid cookie"})
        
        # Check if current song is YouTube
        if len(UQ.data) > 0:
            current_song = UQ.data[0]
            if hasattr(current_song, 'platform') and current_song.platform == "YouTube":
                # Use the same pause logic as Spotify
                UQ.pause_queue(cookie)
                return jsonify({"status": 200, "response": "YouTube playback paused"})
            else:
                return jsonify({"status": 400, "response": "Current song is not YouTube"})
        else:
            return jsonify({"status": 400, "response": "No songs in queue"})
            
    except Exception as e:
        print(f"Error in youtube_pause: {e}")
        return jsonify({"status": 500, "response": str(e)})

@app.route('/youtube_unpause', methods=['POST'])
@cross_origin()
def youtube_unpause():
    """Unpause YouTube playback"""
    try:
        cookie = request.json['cookie']
        
        if not UQ.cookie_is_valid(cookie):
            return jsonify({"status": 400, "response": "Invalid cookie"})
        
        # Check if current song is YouTube
        if len(UQ.data) > 0:
            current_song = UQ.data[0]
            if hasattr(current_song, 'platform') and current_song.platform == "YouTube":
                # Use the same unpause logic as Spotify
                UQ.unpause_queue(cookie)
                return jsonify({"status": 200, "response": "YouTube playback resumed"})
            else:
                return jsonify({"status": 400, "response": "Current song is not YouTube"})
        else:
            return jsonify({"status": 400, "response": "No songs in queue"})
            
    except Exception as e:
        print(f"Error in youtube_unpause: {e}")
        return jsonify({"status": 500, "response": str(e)})
    
@app.route('/get_youtube_progress', methods=['POST'])
@cross_origin()
def get_youtube_progress():
    """Get current YouTube playback progress from frontend"""
    global latest_youtube_progress
    
    try:
        data = request.json
        current_time_seconds = data.get('current_time', 0)
        duration_seconds = data.get('duration', 0)
        video_id = data.get('video_id', '')
        
        # Convert to microseconds to match your backend format
        current_time_microseconds = int(current_time_seconds * 1_000_000)
        duration_microseconds = int(duration_seconds * 1_000_000)
        remaining_microseconds = max(0, duration_microseconds - current_time_microseconds)
        remaining_seconds = remaining_microseconds / 1_000_000
        
        # Store the latest progress globally
        latest_youtube_progress = {
            "current_time": current_time_seconds,
            "duration": duration_seconds,
            "remaining_seconds": remaining_seconds,
            "timestamp": time.time(),
            "video_id": video_id
        }
        
        print(f"Updated YouTube progress: {current_time_seconds:.1f}/{duration_seconds:.1f}s, {remaining_seconds:.1f}s remaining")
        
        return jsonify({
            "status": 200,
            "current_time_microseconds": current_time_microseconds,
            "duration_microseconds": duration_microseconds,
            "remaining_microseconds": remaining_microseconds,
            "remaining_seconds": remaining_seconds
        })
        
    except Exception as e:
        print(f"Error getting YouTube progress: {e}")
        return jsonify({"status": 500, "response": str(e)})

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
    try:
        data = request.json
        id_to_remove = int(data['id'])
        cookie = data['cookie']
        
        print(f"Attempting to remove song with ID: {id_to_remove}")
        
        UQ.remove_from_queue(id_to_remove, cookie)
        
        return jsonify({
            "status": 200,
            "response": f"Song with ID {id_to_remove} removed successfully"
        })
        
    except ValueError as e:
        print(f"ValueError in remove_song: {e}")
        return jsonify({"status": 400, "response": str(e)})
    except Exception as e:
        print(f"Error in remove_song: {e}")
        return jsonify({"status": 500, "response": str(e)})

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
        # CHANGE: Use UQ.youtube_api instead of youtube_api
        if not UQ.youtube_api:
            return jsonify({"status": 500, "response": "YouTube API not available. Please check your API key configuration."})
        
        results = UQ.youtube_api.search_videos(search_string, max_results=4)
        return jsonify({"status": 200, "results": results})
    except Exception as e:
        logging.error(f"Error in YouTube search: {str(e)}")
        print(f"YouTube search error details: {e}")  # Add debug print
        import traceback
        traceback.print_exc()  # Print full traceback
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



if __name__ == '__main__':
    import os
    port = int(os.environ.get('FLASK_PORT', 8080))
    print(f"🎵 Starting M^3 Backend Server on port {port}...")
    print(f"🌐 Backend API available at http://0.0.0.0:{port}")
    
    # Initialize UniversalQueue
    UQ = UniversalQueue()
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=False,
        threaded=True,
        use_reloader=False
    )