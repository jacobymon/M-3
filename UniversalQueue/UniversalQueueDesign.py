""" This module implements the Universal Queue class """
from time import sleep
""" This module allows us to log our errors"""
import logging

from flask import Flask, request 
from flask_cors import CORS, cross_origin
 
import json
import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path +"/Spotify_Interface")

from Spotify_Interface.spotify_interface_class import Spotify_Interface_Class
from Song import Song

import threading


import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_ip = s.getsockname()[0]
s.close()

print(local_ip)


app = Flask(__name__)
CORS(app) 

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
        self.data = []

        #PSUEDO CODE FOR NOW UNTIL MOCK COMES: self.spotify = Spotify_Interface_Class()

        self.suspend_toggle = False

        self.pause_toggle = False

        #this is a MOCK for testing purposes!!!
        self.hostCookie = "host"

        self.idCount = 0

        self.spotify = Spotify_Interface_Class()

        self.flush_exit = threading.Event()

        self.pause_exit = threading.Event()

    def insert(self, song): 
        """
        When queue not suspended
        inserts a song into the queue with a unique id using the song classes set_id() method
        and calls update_UI()

        @param song: a song object that contains all of the attributes needed
        to display info to UI and playback
        """
        if self.suspend_toggle == False:
            song.set_id(self.idCount)
            self.idCount += 1 #update the next id to be unique for the next set
            self.data.append(song)
            #write() #NOT IMPLEMENTED YET

            if len(self.data) == 1:
                self.flush_queue()
        else:
            raise ValueError('can not insert')


    def flush_queue(self):
        """
        Goes through queue and plays songs or pauses, updating display queue
        as necessary by calling update_UI() 

        """
        #Queue the song for playback
        #while the queue is not empty
        #use the spotify interface instance to play the song at the front of queue
        #sleep until the song is finished playing, using a time with respect to song.s_len
        #if puase_queue == True use spotify interface instance to pause and stop timer
        #when song is finished delete it from queue
        #call update_UI()
        #call write()
        while len(self.data) != 0:
            self.spotify.play(self.data[0].uri)
            self.flush_exit.wait((self.data[0].s_len / 1000))
            print("WAIT ENDED")

            if self.pause_toggle == True:
                remaining_time = self.data[0].s_len - self.spotify.get_current_playback_info().progress_ms
                self.data[0].s_len = remaining_time
                self.pause_exit.wait()
                continue
                



            self.data = self.data[1:]

    def pause_queue(self, cookie):
        """
        allows us to pause the queu and play the queue.

        @return bool: true when queue is paused, false when queue is unpaused

        """

        if not self.cookie_verifier(cookie):
            raise ValueError('invalid id')

        if self.pause_toggle == False:
            self.pause_toggle = True
            
            self.spotify.pause()
            self.flush_exit.set()
        


    def unpause_queue(self, cookie):
        """
        allows us to pause the queu and play the queue.

        @return bool: true when queue is paused, false when queue is unpaused

        """

        if not self.cookie_verifier(cookie):
            raise ValueError('invalid id')

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
        #loop through the users and send them the current state of the queu
        
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
        if self.cookie_verifier(cookie):
            for s in self.data:
                if s.id == id:
                    #If we're removing the first item in the queue which is currently playing, just kill the
                    #current wait call on flush queue as it will remove the first item 
                    if s.id == self.data[0].id:
                        self.flush_exit.set()
                    #If we're removing anything else, just remove it from the queue
                    else:
                        self.data.remove(s)
                    #write()
                    return
            else:
                raise ValueError('invalid id')

            # except:
            #     raise ValueError('invalid id')
        

       

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

    def set_suspend_toggle(self, flag, cookie):
        """
        privileged host-only function

        toggle for the queue for accepting song requests or not.

        @param flag: a boolean value that is true when the queue is NOT accepting requests
        false when the queue is accepting requests.
        
        """
        #MOCKED verify cookie is host's, would pass the cookie in from request instead
        #of self.cookie
        if self.cookie_verifier(cookie):

            if flag == True:
                self.suspend_toggle = True

            else:
                self.suspend_toggle = False

    def clear_queue(self):
        """
        privileged host-only function

        sets the queue back to an empty list
        """

    def write(self, file):
        """
        Writes the queue to a file in json format on
        the hosts local machine
        

        @param file: the file we are writing to, created during startup 
        """ 

        #break down the song objects into jsonifiable data
        #write to the file

    def recover(self, file):
        """
        recovers the current state of the queue. in case of a system crash.

        @param file: the file we are reading from (same file as the one we wrote to)
        """
        #when there's a system crash
        #read from the file
        #re insert all of the song objects back into a new queue
        #update_ui

UQ = UniversalQueue()

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
    response = {'spotify_url': UQ.spotify.from_url(url)}

    song_data = json.dumps(response)
    song = Song(song_data)

    UQ.insert(song)
    print(song_data)
    return song_data

@app.route('/submit_song', methods=['GET', 'POST'])
@cross_origin()
def submit_song():

    song_data = request.get_json()
    print("SONGDATA SONGDATA BEFORE", song_data)
    song_data['search_results']['name'] = song_data['search_results']['title']
    song_data = json.dumps(song_data)
    print("SONGDATA SONGDATA", song_data)
    song = Song(song_data)

    UQ.insert(song)


    print(UQ.data) 
    return song_data


@app.route('/pause', methods=['GET', 'POST'])
@cross_origin()
def pause_route():
    UQ.pause_queue()

@app.route('/unpause', methods=['GET', 'POST'])
@cross_origin()
def unpause_route():
    UQ.unpause_queue()

@app.route('/request_update', methods=['GET', 'POST'])
@cross_origin()
def update_visual_queue():

    # current_queue_data = UQ.datak
    # current_queue_data = json.dumps(current_queue_data)
    data = []
    for i in range(len(UQ.data)):
        songObject = {
                'name': UQ.data[i].name,
                'artist': UQ.data[i].artist,
                'albumname': UQ.data[i].album,
                'albumcover': UQ.data[i].image,
                'submissionID': 1,
                'id': ""
                    }
        # print( "NAMENAMENAMENAMENAMENANEMEANE " + UQ.data[i].name, songObject['name'])
        data.append(songObject)

    jsonData = json.dumps(data)
    # print('#################' + jsonData + '#################')
    return jsonData

@app.route('/verify_host', methods=['GET', 'POST'])
@cross_origin()
def verify_host():
    if request.method == 'GET':
        incomingIP = request.remote_addr
        if incomingIP == local_ip:
            return [True, UQ.hostCookie]
        else:
            return [False, ""]

@app.route('/remove_song', methods=['GET', 'POST'])
@cross_origin()
def remove_song():
    id_to_remove = request.args.get('id')
    cookie = request.args.get('cookie')
    UQ.remove_from_queue(id, cookie)
    return id

@app.route('/suspend_queue', methods=['GET', 'POST'])
@cross_origin()
def suspend_queue():
    cookie = request.args.get('cookie')
    UQ.set_suspend_toggle(True, cookie)
    return True

@app.route('/unsuspend_queue', methods=['GET', 'POST'])
@cross_origin()
def unsuspend_queue():
    cookie = request.args.get('cookie')
    UQ.set_suspend_toggle(False, cookie)
    return True

@app.route('/pause_music', methods=['GET', 'POST'])
@cross_origin()
def pause_music():
    cookie = request.args.get('cookie')
    UQ.pause_queue(cookie)
    return True

@app.route('/unpause_music', methods=['GET', 'POST'])
@cross_origin()
def unpause_music():
    cookie = request.args.get('cookie')
    UQ.unpause_queue(cookie)
    return True

if __name__ == '__main__':
    with open('../m3-frontend/.env', 'w') as f_obj:
        f_obj.write('REACT_APP_BACKEND_IP="'+local_ip+'"')

    app.run(host = '0.0.0.0', port=8080) 

