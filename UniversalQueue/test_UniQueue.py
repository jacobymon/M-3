import unittest
import UniversalQueueDesign
import json

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




if __name__ == "__main__":
    unittest.main()
        