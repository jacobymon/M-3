import unittest
import IsoUniversalQueue
import json
from Song import Song

class TestUniQueue(unittest.TestCase):

    def setUp(self):
        self.uniQueue = IsoUniversalQueue.UniversalQueue()

        # Create mock user requests via JSON with cookies
        with open('UniQueueTest.json', 'r') as file:
            hostRequestData = json.load(file)
            self.hostCookie = hostRequestData.get('cookie')

        with open('UniQueueTest2.json', 'r') as file:
            userRequestData = json.load(file)
            self.userCookie = userRequestData.get('cookie')

        # Mock Songs
        with open('SongTest.json', 'r') as file:
            self.song1 = Song(file.read())

        with open('SongTest3.json', 'r') as file:
            self.song3 = Song(file.read())

        with open('SongTest6.json', 'r') as file:
            self.song6 = Song(file.read())

    def test_init(self):
        """Test initialization of UniversalQueue."""
        self.assertEqual(self.uniQueue.data, {})
        self.assertFalse(self.uniQueue.suspend_toggle)
        self.assertFalse(self.uniQueue.pause_toggle)

    def test_cookie_verifier(self):
        """Test cookie verification."""
        self.assertFalse(self.uniQueue.cookie_verifier(self.userCookie))
        self.assertTrue(self.uniQueue.cookie_verifier(self.hostCookie))

    def test_set_suspend_toggle(self):
        """Test setting the suspend toggle."""
        self.uniQueue.set_suspend_toggle(False)
        self.assertFalse(self.uniQueue.suspend_toggle)

        self.uniQueue.set_suspend_toggle(True)
        self.assertTrue(self.uniQueue.suspend_toggle)

    def test_insert_and_removal(self):
        """Test inserting and removing songs from the queue."""
        self.uniQueue.insert(self.song1)
        self.assertIn(self.song1.id, self.uniQueue.data)
        self.assertEqual(self.uniQueue.data[self.song1.id], self.song1)

        self.uniQueue.insert(self.song3)
        self.assertIn(self.song3.id, self.uniQueue.data)
        self.assertEqual(self.uniQueue.data[self.song3.id], self.song3)

        self.uniQueue.insert(self.song6)
        self.assertIn(self.song6.id, self.uniQueue.data)
        self.assertEqual(self.uniQueue.data[self.song6.id], self.song6)

        # Test unique IDs
        self.assertNotEqual(self.song1.id, self.song3.id)
        self.assertNotEqual(self.song1.id, self.song6.id)
        self.assertNotEqual(self.song3.id, self.song6.id)

        # Test error handling for suspend toggle
        self.uniQueue.set_suspend_toggle(True)
        self.assertRaises(ValueError, self.uniQueue.insert, self.song1)
        self.uniQueue.set_suspend_toggle(False)

        # Test removal
        self.uniQueue.remove_from_queue(self.song1.id)
        self.assertNotIn(self.song1.id, self.uniQueue.data)

        self.assertRaises(ValueError, self.uniQueue.remove_from_queue, 999)  # Non-existent ID

        self.uniQueue.remove_from_queue(self.song3.id)
        self.assertNotIn(self.song3.id, self.uniQueue.data)

        self.uniQueue.remove_from_queue(self.song6.id)
        self.assertEqual(self.uniQueue.data, {})

        self.assertRaises(ValueError, self.uniQueue.remove_from_queue, self.song6.id)  # Empty queue

    def test_write_and_recover(self):
        """Test writing to and recovering from a file."""
        self.uniQueue.insert(self.song1)
        self.uniQueue.insert(self.song3)
        self.uniQueue.insert(self.song6)

        # Write data to file
        self.uniQueue.write()

        # Simulate crash and recover
        self.uniQueue.data = None
        recoveredQueue = self.uniQueue.recover(None)

        # Verify recovered data
        self.assertIn(self.song1.id, recoveredQueue.data)
        self.assertIn(self.song3.id, recoveredQueue.data)
        self.assertIn(self.song6.id, recoveredQueue.data)

        self.assertEqual(recoveredQueue.data[self.song1.id].uri, self.song1.uri)
        self.assertEqual(recoveredQueue.data[self.song3.id].uri, self.song3.uri)
        self.assertEqual(recoveredQueue.data[self.song6.id].uri, self.song6.uri)

if __name__ == "__main__":
    unittest.main()