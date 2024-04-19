import unittest
from UniversalQueueDesign import UniversalQueue

class TestUniQueue(unittest.TestCase):

    def setUp(self):
        self.uniQueue = UniversalQueue()

        #create mock user requests via json with cookies
        with open('UniQueueTest.json', 'r') as file:
            self.hostCookie = file.read()

        with open('UniQueueTest2.json', 'r') as file:
            self.userCookie = file.read()

        with open('UniQueueTest3.json', 'r') as file:
            self.badRequest = file.read()
    def test_init(self):

        self.assertEqual(self.uniQueue.data, [])

        self.assertFalse(self.uniQueue.suspend_toggle)

        self.assertFalse(self.uniQueue.pause_toggle)


        #IMPORTANT this is a place holder for checking if we have a real instance
        #of the spotify interface class, not a mock

    def test_cookie_verifier(self):

        #when integration comes we will add tests with patch and mocked requests
        #for now we will use a static json

        
        self.assertFalse(UniversalQueueDesign.cookie_verifier(self.userCookie))

        self.assertTrue(UniversalQueueDesign.cookie_verifier(self.hostCookie))

        self.assertRaises(ValueError, UniversalQueue, self.badRequest)



if __name__ == "__main__":
    unittest.main()
        