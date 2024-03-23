""" This module implements the Song class which takes in json data sent from the UI to create a song object """
class Song:

    def __init__(self,uri, s_len, name, album):
        """
        constructs a song object

        @param uri: uri of the submitted song

        @param s_len: length of the song in milli seconds

        @param name: the song's name

        @param album: the album of the song

        """ 

