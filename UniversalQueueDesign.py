""" This module implements the Universal Queue class """
from time import sleep

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

            @attribute suspend_toggle: a boolean value where true
                                        suspends the queue from song requests
                                        and false allows                                        
        """
        #self.suspend_toggle = False

    def insert(self, song): 
        """
        inserts a song into the queue and calls update_UI()

        @param song: a song object that contains all of the attributes needed
        to display info to UI and playback, passed in from the UI
        """
        #Get the made song object from the front-end
        #self.queue.append(song) 
        #call write()


    def flush_queue(self):
        """
        Goes through queue and plays songs, updating display queue
        as necessary by calling update_UI()

        """
        #Queue the song for playback
        #while the queue is not empty
        #use the spotify interface instance to play the song at the front of queue
        #sleep until the song is finished playing, using song.s_len
        #when song is finished delete it from queue
        #call update_UI()
        #call write()


    def update_ui(self):
        """
        Sends the current state of the queue to the UI for all users
        to be displayed on their front end
        

        @return the current state of the queue to all users
        """
        #loop through the users and send them the current state of the queu
        



    def request_update(self, user):
        """
        allows a specific user to request the current state of the queue to be displayed for them
        (ie when they first click on to the website link)

        @param: the user that called the function, passed in from
        front end
        
        @return: the current state of the queue to the specific user
        """
        #send current queue state to user

    def remove_from_queue(self, index):
        """
        a privileged host-only function that removes songs from queue.
        removing the current song goes to the next song.

        calls update_ui

        @param index: index recieved from host corresponding song the want removed from queue
       
        """
        #verify cookie is the host's
        #  #remove song at index in queue
        # del queue[index]
        # if index == 0: 
        #     #If the song that deleted is currently playing, start playing the next one
        #     flush_queue()
        # write()
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


    def insert_into_queue(self, index, song): 
        """
        Privileged host-only function that inserts song object into an index of the queue

        @param index: index to insert song object into

        @param song: song object
        """
        #verify cookie is host's
        #insert song into a specific place in the queue
        # queue.insert(index, song)
        # write()
    
    def cookie_verifier(cookie):
        """
        verifies that the privileged functions are being called by the host

        @param cookie: cookie that is being checked to be the hosts, created in startup component
        """

    def write(self, file):
        """
        Writes the queue to a file in json format on
        the hosts local machine
        

        @param file: the file we are writing to, created during startup 
        """ 

        #break down the song objects into jsonifiable data
        #write to the file
