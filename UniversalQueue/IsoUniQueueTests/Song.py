# """ This module implements the Song class which takes in json data sent from the UI to create a song object """
# import json
# class Song:

#     def __init__(self, json_data, recover = False):
#         """
#         creates a song object

#         @param uri: uri of the submitted song

#         @param s_len: length of the song in milli seconds

#         @param name: the song's name

#         @param album: the album of the song

#         @param artist: artist of the song

#         @param id: unique id of the song

#         """
#         # Loading JSON data into a Python dictionary
#         dict = json.loads(json_data)

#         if recover == False:

#             # Accessing the JSON attributes to initialize Song attributes
#             status = dict.get('status')

#             if status == 200:

#                 #***********Need to check this error logic with Max**********
#                 # try:
#                 #     dict.get('search_results')
#                 # except:
#                 #     raise ValueError('search_result field missing in json')
                

#                 # try:
#                 #     dict.get('search_results').get('uri')
#                 # except:
#                 #     raise ValueError('search_result key missing in json')
                
                
#                 # if dict.get('search_results').get('uri') == None:
#                 #     raise ValueError('search_result value is null')
                
#                 # else:
#                 #     self.uri = dict.get('search_results').get('uri')
#                 #***********Need to check this error logic with Max**********


#                 self.uri = dict.get('search_results').get('uri')   
#                 self.s_len = dict.get('search_results').get('s_len')
#                 self.name = dict.get('search_results').get('name')
#                 self.album = dict.get('search_results').get('album')
#                 self.artist = dict.get('search_results').get('artist')
#                 self.id = None

#             else:
#                 raise ValueError('status of json not acceptable')
#         else:
#             self.uri = dict.get('uri')   
#             self.s_len = dict.get('s_len')
#             self.name = dict.get('name')
#             self.album = dict.get('album')
#             self.artist = dict.get('artist')
#             self.id = None


#     def set_id(self, id):
#         """
#         setter for the songs unique id. Called when inserting a song into the universal queue

#         @param id: unique id created by the universal queue
#         """
#         self.id = id


class Song:
    def __init__(self, json_data, recover=False):
        """
        Creates a song object.

        @param json_data: JSON data containing song attributes.
        @param recover: Boolean flag for recovery mode.
        """
        # Loading JSON data into a Python dictionary
        dict = json.loads(json_data)

        if recover == False:
            status = dict.get('status')

            if status == 200:
                self.platform = dict.get('platform', 'Spotify')  # Default to Spotify if platform is not provided

                if self.platform == "YouTube":
                    # Handle YouTube-specific metadata
                    self.uri = dict.get('search_results').get('video_url')
                    self.name = dict.get('search_results').get('title')
                    self.artist = dict.get('search_results').get('channel_name')
                    self.s_len = dict.get('search_results').get('duration')
                    self.album = None  # YouTube songs may not have an album
                else:
                    # Handle Spotify-specific metadata
                    self.uri = dict.get('search_results').get('uri')
                    self.s_len = dict.get('search_results').get('s_len')
                    self.name = dict.get('search_results').get('name')
                    self.album = dict.get('search_results').get('album')
                    self.artist = dict.get('search_results').get('artist')

                self.id = None
            else:
                raise ValueError('status of json not acceptable')
        else:
            self.uri = dict.get('uri')
            self.s_len = dict.get('s_len')
            self.name = dict.get('name')
            self.album = dict.get('album')
            self.artist = dict.get('artist')
            self.platform = dict.get('platform', 'Spotify')  # Default to Spotify if platform is not provided
            self.id = None

    def set_id(self, id):
        """
        Setter for the song's unique ID. Called when inserting a song into the universal queue.

        @param id: Unique ID created by the universal queue.
        """
        self.id = id
