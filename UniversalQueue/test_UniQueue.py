import unittest
import UniversalQueueDesign
import json
import Song

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

    #IN PROGRESS
    def test_insert(self):

        self.uniQueue.data.insert(self.song1)

        self.assertEqual(self.uniQueue.data[0], self.song1)

        self.uniQueue.data.insert(self.song3)

        self.assertEqual(self.uniQueue.data[-1], self.song3)

        self.uniQueue.data.insert(self.song1)

        self.assertNotEqual(self.uniQueue.data[0].id, self.uniQueue.data[1].id)

        self.assertNotEqual(self.uniQueue.data[0].id, self.uniQueue.data[2].id)

        self.assertNotEqual(self.uniQueue.data[1].id, self.uniQueue.data[2].id)

        #cleanup will be removing song from queue, the function is not written yet






        

        

        







if __name__ == "__main__":
    unittest.main()
        