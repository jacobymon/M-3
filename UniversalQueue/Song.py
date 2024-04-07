""" This module implements the Song class which takes in json data sent from the UI to create a song object """
class Song:

    def __init__(self, uri, s_len, name, album, artist, id):
        """
        creates a song object

        @param uri: uri of the submitted song

        @param s_len: length of the song in milli seconds

        @param name: the song's name

        @param album: the album of the song

        @param artist: artist of the song

        @param id: unique id of the song

        """

        # self.uri = uri
        # self.s_len = s_len
        # self.name = name
        # self.album = album
        # self.artist = artist

    def set_id(self, id):
        """
        setter for the songs unique id. Called when inserting a song into the universal queue

        @param id: unique id created by the universal queue
        """
        #self.id = id
 



