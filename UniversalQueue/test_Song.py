import unittest
from Song import Song
import SongTest

class TestSong(unittest.TestCase):

    #when integration comes we will add tests with patch and mocked requests
    #for now we will use a static json
    def test_init(self):
        song1 = Song(SongTest.json)

        self.assertEqual(song1.uri, "asadfas")
        self.assertEqual(song1.song_len, 123)
        self.assertEqual(song1.name, "breh")
        self.assertEqual(song1.album, "the breh album")
        self.assertEqual(song1.artist, "dude")
        self.assertEqual(song1.id, None)

        #bad request in json
        self.assertRaises(ValueError, Song.__init__, SongTest2.json)








