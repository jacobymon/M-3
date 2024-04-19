import unittest
from Song import Song
import json

class TestSong(unittest.TestCase):

    #when integration comes we will add tests with patch and mocked requests
    #for now we will use a static json
    def setUp(self):
        with open('SongTest.json', 'r') as file:
            self.SongTest_data = file.read()

        with open('SongTest2.json', 'r') as file:
            self.SongTest2_data = file.read()

    
    def test_init(self):
        song1 = Song(self.SongTest_data)

        self.assertEqual(song1.uri, "asadfas")
        self.assertEqual(song1.s_len, 123)
        self.assertEqual(song1.name, "breh")
        self.assertEqual(song1.album, "the breh album")
        self.assertEqual(song1.artist, "dude")
        self.assertEqual(song1.id, None)

        #bad request in json
        self.assertRaises(ValueError, Song, self.SongTest2_data)

if __name__ == "__main__":
    unittest.main()






