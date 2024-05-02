""" This module implements the Song class which takes in json data sent from the UI to create a song object """
import json
class Song:

    def __init__(self, json_data):
        """
        creates a song object

        @param uri: uri of the submitted song

        @param s_len: length of the song in milli seconds

        @param name: the song's name

        @param album: the album of the song

        @param artist: artist of the song

        @param id: unique id of the song

        """


        # Loading JSON data into a Python dictionary
        dict = json.loads(json_data)

        # Accessing the JSON attributes to initialize Song attributes
        status = dict.get('status')

        if status == 200:

            #***********Need to check this error logic with Max**********
            # try:
            #     dict.get('search_results')
            # except:
            #     raise ValueError('search_result field missing in json')
            

            # try:
            #     dict.get('search_results').get('uri')
            # except:
            #     raise ValueError('search_result key missing in json')
            
            
            # if dict.get('search_results').get('uri') == None:
            #     raise ValueError('search_result value is null')
            
            # else:
            #     self.uri = dict.get('search_results').get('uri')
            #***********Need to check this error logic with Max**********


            self.uri = dict.get('search_results').get('uri')   
            self.s_len = dict.get('search_results').get('s_len')
            self.name = dict.get('search_results').get('name')
            self.album = dict.get('search_results').get('album')
            self.artist = dict.get('search_results').get('artist')
            self.image = dict.get('search_results').get('image')
            self.id = None

        else:
            raise ValueError('status of json not acceptable')


    def set_id(self, id):
        """
        setter for the songs unique id. Called when inserting a song into the universal queue

        @param id: unique id created by the universal queue
        """
        self.id = id



