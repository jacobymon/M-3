""" This module implements the Universal Queue class """
from re import A
from time import sleep
""" This module allows us to log our errors"""
import logging

from flask import Flask, jsonify, request 
from flask_cors import CORS, cross_origin
 
import json
from Spotify_Interface.spotify_interface_class import Spotify_Interface_Class
from Song import Song

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

        self.queue_flag = True

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
        while len(self.data) != 0 and self.queue_flag:
            self.spotify.play(self.data[0].uri)
            sleep(self.data[0].s_len / 1000)
            self.data = self.data[1:]

        self.queue_flag = True


    def pause_queue(self):
        """
        allows us to pause the queu and play the queue.

        @return bool: true when queue is paused, false when queue is unpaused

        """
        # if self.pause_toggle == False:
            #self.pause_toggle = True
        # else:
            #self.pause_toggle = False


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

    def remove_from_queue(self, id):
        """
         a privileged host-only function that removes songs from queue.
        removing the current song goes to the next song.

        Throw exception when the song we want to remove is not in the Universal queue

        calls update_ui

        @param index: index recieved from host corresponding song the want removed from queue
       
        """
        #MOCKED verify cookie is host's, would pass the cookie in from request instead
        #of self.cookie
        #IMPORTANT removal of first song starts playing next song is checked manually
        #IMPORTANT this operation is curretnly O(n). Look into making it O(1) with dictionary
        self.queue_flag = False
        if self.cookie_verifier(self.hostCookie):
            for s in self.data:
                if s.id == id:
                    if s.id == self.data[0].id:
                        self.data.remove(s)
                        #play next song
                        #flush_queue
                        self.flush_queue()

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
    print(response)
    return response

@app.route('/submit_song', methods=['GET', 'POST'])
@cross_origin()
def submit_song():

    song_data = request.get_json()
    # jsonify(song_data)
    song_data = json.dumps(song_data)
    print(song_data)
    print("######TYPE#####", type(song_data))
    song = Song(song_data)

    UQ.insert(song)
    print(UQ.data) 
    return song_data
    
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=8080) 

