import unittest
from UniversalQueueDesign import UniversalQueue

class TestUniQueue(unittest.TestCase):

    def setUp(self):
        self.queue = UniversalQueue()

    def test_init(self):

        self.assertEqual(self.queue, [])

        self.assertFalse(self.suspend_toggle)

        #IMPORTANT this is a place holder for checking if we have a real instance
        #of the spotify interface class, not a mocl
        