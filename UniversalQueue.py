""" This module implements the Universal Queue class """
class UniversalQueue:
    """
    Stores all of the song requests in a queue order
    """

    def __init__(self) -> list:
        """
            intializes a queue object as an empty list
            initializes an instance of the spotify interface class
        """

    def insert(self, song): 
        """
        inserts a song into the queue and calls update_UI()

        @param song: a song object that contains all of the attributes needed
        to display info to UI and playback
        """

    def flush_queue(self):
        """
        Goes through queue and plays songs, updating display queue
        as necessary by calling update_UI()

        """
    
    def update_ui(self):
        """
        Sends the current state of the queue to the UI for all users
        
        """
    def request_update(user):
        """
        allows a specific user to request the current state of the queue to be displayed for them
        (ie when they first click on to the website link)
        
        """

    def remove_from_queue(self, index):
        """
        a privileged host-only function that removes songs from queue.
        removing the current song goes to the next song.

        @param index: index recieved from host corresponding song the want removed from queue
        #remove song at index in queue
        del queue[index]
        if index == 0: 
            #If the song that deleted is currently playing, start playing the next one
            flush_queue()
        write()
        """
    def suspend_toggle(flag):
        """
        toggle for the queue for accepting song equests or not.

        @param flag: a boolean value that is true when the queue is NOT accepting requests
        false when the queue is accepting requests.
        
        """

    

    def insert_into_queue(self, index, song): 
        """
        Privileged host-only function that inserts song object into an index of the queue

        @param index: index to insert song object into

        @param song: song object
        """
    
    def cookie_verifier(cookie):
        """
        verifies that the privileged functions are being called host

        @param cookie: cookie that is being checked to be the hosts, created in startup component
        """
