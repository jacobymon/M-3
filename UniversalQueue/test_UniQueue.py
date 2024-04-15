import unittest
from UniversalQueueDesign import UniversalQueue

class TestUniQueue(unittest.TestCase):

    def setUp(self):
        self.queue = UniversalQueue()

    def test_init(self):

        self.assertEqual(self.queue.data, [])

        self.assertFalse(self.queue.suspend_toggle)

        self.assertFalse(self.queue.pause_toggle)


        #IMPORTANT this is a place holder for checking if we have a real instance
        #of the spotify interface class, not a mocl


if __name__ == "__main__":
    unittest.main()
        