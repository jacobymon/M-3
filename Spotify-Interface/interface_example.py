from spotify_interface_class import Spotify_Interface_Class

# This file is an example for how the class works. You will require correct credentials and a valid account
# for this example to work

# Initalizing the Spotify Interface 
s = Spotify_Interface_Class()

# To do anything interesting, we'll need a track id. We can get this by passing a string to "return_results"

# data = s.return_results("Get Back The Beatles")
print(s.from_url("https://open.spotify.com/track/7dflu0aBzB9kpcSinIph9r?si=8956bcb862e64a46"))

# print(data)

# This tracks object actually contains a lot of potential results (20 currently, set by a macro), but we'll
# assume the first result is probably what we wanted and take its id

# track_id = tracks.items[0].id

# Now let's play the track

# s.play(track_id)

# Running this should start "Get Back" on the playback Now

# We can also pause and unpause the playback. Uncomment these method calls if you want to see how that works
# (and don't forget to comment out the 'play' call above, or else it'll restart the playback) 

# s.pause()
# s.unpause()

# And that's pretty much the basics of what the SpotifY Interface Class does.
