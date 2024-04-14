""" This module implements the Universal Queue class """
from time import sleep

""" This module allows us to log our errors"""
import logging

class UniversalQueue:
    """
    Stores all of the song requests in a queue order
    """

    def __init__(self) -> list:
        """
            creates a Universal Queue object
            intializes a queue object as an empty list
            initializes an instance of the spotify interface class
            in order to interact with song playback

            @attribute suspend_toggle: a boolean value where true suspends the
            queue from song requests and false allows

            @attribute pause_toggle: a boolean value where true indicates pausing, false is playing                                      
        """
        #self.queue = []
        #self.spotify = Spotify_Interface_Class()
        #self.suspend_toggle = False

    def insert(self, song): 
        """
        When queue is not upsended
        inserts a song into the queue and calls update_UI()

        @param song: a song object that contains all of the attributes needed
        to display info to UI and playback, passed in from the UI
        """
        #if suspend toggle is False
        #Get the made song object from the front-end
        #self.queue.append(song) 
        #call write()


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
        #verify cookie is the host's
        #try
        #  #remove song by it's id from queue
        # if index == 0: 
        #     #If the song that deleted is currently playing, start playing the next one
        #     flush_queue()
        # write()
        #exceptions as e:
            #send e to front end

    def set_suspend_toggle(self, flag):
        """
        privileged host-only function

        toggle for the queue for accepting song requests or not.

        @param flag: a boolean value that is true when the queue is NOT accepting requests
        false when the queue is accepting requests.
        
        """
        #verify cookie is host's
        #if flag == True:
        #   self.suspend_toggle = True
        #else:
        #   self.suspend_toggle = False

    def clear_queue(self):
        """
        privileged host-only function

        sets the queue back to an empty list
        """

    
    def cookie_verifier(cookie):
        """
        verifies that the privileged functions are being called by the host.
        throw error when return is false.
        
        If the cookie is actually the hosts
        and this is false we log the error and shut down. (Our host is not recognized as the host anymore!).
        ***Not sure how we would know this though

        @param cookie: cookie that is being checked to be the hosts, created in startup component

        @return Bool: True when the cookie matches the host's else and error
        """
        # if cookie == Host's
            #return True
        # else:
            #return error

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
