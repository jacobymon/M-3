import unittest
import UniversalQueueDesign
import json
# import sys
# import os

# path = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(path +"/Spotify_Interface")

# from Spotify_Interface.spotify_interface_class import Spotify_Interface_Class
# from Song import Song

from Song import Song

class TestUniQueue(unittest.TestCase):

    def setUp(self):
        self.uniQueue = UniversalQueueDesign.UniversalQueue()

        #create mock user requests via json with cookies
        with open('UniQueueTest.json', 'r') as file:
            hostRequestData= file.read()
            hostRequestData = json.loads(hostRequestData)
            self.hostCookie = hostRequestData.get('cookie')


        with open('UniQueueTest2.json', 'r') as file:
            userRequestData= file.read()
            userRequestData = json.loads(userRequestData)
            self.userCookie = userRequestData.get('cookie')

        #MAYBE DELETEME
        #  with open('UniQueueTest3.json', 'r') as file:
        #     self.badRequest = file.read()

        #mock Songs
        with open('SongTest.json', 'r') as file:
            self.SongTest_data = file.read()

        self.song1 = Song(self.SongTest_data)

        with open('SongTest3.json', 'r') as file:
            self.SongTest3_data = file.read()

        self.song3 = Song(self.SongTest3_data)

        with open('SongTest6.json', 'r') as file:
            self.SongTest6_data = file.read()

        self.song6 = Song(self.SongTest6_data)


    def test_init(self):

        self.assertEqual(self.uniQueue.data, [])

        self.assertFalse(self.uniQueue.suspend_toggle)

        self.assertFalse(self.uniQueue.pause_toggle)


        #IMPORTANT this is a place holder for checking if we have a real instance
        #of the spotify interface class, not a mock

    def test_cookie_verifier(self):

        #when integration comes we will add tests with patch and mocked requests
        #for now we will use a static json

        self.assertFalse(self.uniQueue.cookie_verifier(self.userCookie))

        self.assertTrue(self.uniQueue.cookie_verifier(self.hostCookie))


    def test_set_suspend_toggle(self):

        self.uniQueue.set_suspend_toggle(False)

        self.assertFalse(self.uniQueue.suspend_toggle)

        self.uniQueue.set_suspend_toggle(True)

        self.assertTrue(self.uniQueue.suspend_toggle)


    def test_insert(self):
        #must have a spotify app running in order to perform this test!
        #This will play a series of 3 short songs/skits resulting in about 51 seconds of testing.
        #1. suffer by Napalm Deaeth
        #2. Her Majesty by The Beatles
        #3. Intro (skit) by Kanye West

        self.uniQueue.insert(self.song1)

        self.uniQueue.insert(self.song3)

        self.uniQueue.insert(self.song6)




if __name__ == "__main__":
    unittest.main()
        