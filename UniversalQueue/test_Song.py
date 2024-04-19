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

        with open('SongTest3.json', 'r') as file:
            self.SongTest3_data = file.read()

        with open('SongTest4.json', 'r') as file:
            self.SongTest4_data = file.read()

        with open('SongTest5.json', 'r') as file:
            self.SongTest5_data = file.read()

    
    def test_init(self):
        song1 = Song(self.SongTest_data)

        self.assertEqual(song1.uri, "asadfas")
        self.assertEqual(song1.s_len, 123)
        self.assertEqual(song1.name, "breh")
        self.assertEqual(song1.album, "the breh album")
        self.assertEqual(song1.artist, "dude")
        self.assertEqual(song1.id, None)

        #bad json tests
        #*****Add these tests after checking with max*********
        # self.assertRaises(ValueError, Song, self.SongTest4_data)

        # self.assertRaises(ValueError, Song, self.SongTest5_data)
        #*****Add these tests after checking with max*********
        
        self.assertRaises(ValueError, Song, self.SongTest2_data)

    def test_set_id(self):

        song1 = Song(self.SongTest_data)
        song3 = Song(self.SongTest3_data)
        song1.set_id(0)
        song3.set_id(1)

        self.assertEqual(song1.id, 0)
        self.assertEqual(song3.id, 1)
        self.assertNotEqual(song1.id, song3.id)

if __name__ == "__main__":
    unittest.main()






