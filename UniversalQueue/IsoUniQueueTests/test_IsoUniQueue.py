import unittest
import IsoUniversalQueue
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
        self.uniQueue = IsoUniversalQueue.UniversalQueue()

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


    def test_insert_and_removal(self):
        #note that while it is possible to insert the same mocked song object here, it would not be
        #in a real use case, thus it's not tested for.

        self.uniQueue.insert(self.song1)

        self.assertEqual(self.uniQueue.data[0], self.song1)

        self.uniQueue.insert(self.song3)

        self.assertEqual(self.uniQueue.data[-1], self.song3)

        self.uniQueue.insert(self.song6)

        #testing id functionality
        self.assertNotEqual(self.uniQueue.data[0].id, self.uniQueue.data[1].id)

        self.assertNotEqual(self.uniQueue.data[0].id, self.uniQueue.data[2].id)

        self.assertNotEqual(self.uniQueue.data[1].id, self.uniQueue.data[2].id)

        #testing error handleing
        self.uniQueue.set_suspend_toggle(True)

        self.assertRaises(ValueError, self.uniQueue.insert, self.song1)

        #cleanup
        self.uniQueue.set_suspend_toggle(False)


        #***************remove_from_queue tests**********************
        self.uniQueue.remove_from_queue(1)

        self.assertRaises(ValueError, self.uniQueue.remove_from_queue, 3) #remove id that's not in queue
        

        self.assertEqual(self.uniQueue.data[0].id, 0)
        self.assertEqual(self.uniQueue.data[-1].id, 2)

        self.uniQueue.remove_from_queue(0)

        self.assertEqual(self.uniQueue.data[0].id, 2)

        self.uniQueue.remove_from_queue(2)

        self.assertEqual(self.uniQueue.data, [])

        self.assertRaises(ValueError,self.uniQueue.remove_from_queue, 0) #removal of empty queue


    def test_write_and_recover(self):

        #note that insert() and remove_from_queue have write() in them.
        self.uniQueue.insert(self.song1)

        with open('Write.json', 'r') as file:
            self.Write_data = file.read()

        with open('WriteTest.json', 'r') as file:
            self.WriteTest_data = file.read()

        self.assertEqual(self.Write_data, self.WriteTest_data)

        self.uniQueue.insert(self.song3)

        with open('Write.json', 'r') as file:
            self.Write_data = file.read()
        
        with open('WriteTest2.json', 'r') as file:
            self.WriteTest2_data = file.read()


        self.assertEqual(self.Write_data, self.WriteTest2_data)


        self.uniQueue.insert(self.song6)

        with open('Write.json', 'r') as file:
            self.Write_data = file.read()

        with open('WriteTest3.json', 'r') as file:
            self.WriteTest3_data = file.read()

        self.assertEqual(self.Write_data, self.WriteTest3_data)


        formerURIs = []
        for s in self.uniQueue.data:
            formerURIs.append(s.uri)

        #**** simulated crash 1
        self.uniQueue.data = None

        self.uniQueue = IsoUniversalQueue.UniversalQueue().recover('Write.json')

        recoveredURIs = []
        for s in self.uniQueue.data:
            recoveredURIs.append(s.uri)

        self.assertEqual(recoveredURIs, formerURIs)

    
        self.uniQueue.remove_from_queue(2)

        with open('Write.json', 'r') as file:
            self.Write_data = file.read()

        self.assertEqual(self.Write_data, self.WriteTest2_data)



        self.uniQueue.remove_from_queue(1)

        formerURIs = []
        for s in self.uniQueue.data:
            formerURIs.append(s.uri)

        #simulated crash 2
        self.uniQueue.data = None

        with open('Write.json', 'r') as file:
            self.Write_data = file.read()

        self.assertEqual(self.Write_data, self.WriteTest_data)

        self.newUniQueue = IsoUniversalQueue.UniversalQueue().recover('Write.json')

        recoveredURIs = []
        for s in self.newUniQueue.data:
            recoveredURIs.append(s.uri)
            
        
        self.assertEqual(formerURIs, recoveredURIs)


        self.newUniQueue.remove_from_queue(0)


        self.assertEqual(self.newUniQueue.data, [])


        #**** simulated crash 2
        self.newUniQueue.data = None

        self.newUniQueue2 = IsoUniversalQueue.UniversalQueue().recover("Write.json.txt")

        self.assertEqual(self.newUniQueue2.data, [])



if __name__ == "__main__":
    unittest.main()
        