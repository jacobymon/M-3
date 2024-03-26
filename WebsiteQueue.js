/*The Website Queue will give a visible representation of the current state of
 the Universal Queue to all users of the website, which will allow them to see
 what songs are playing, which will play in the future, and whether their songs
got properly added to the queue. For hosts, it will also include the 
functionality that the host can use to manage the Universal Queue- removing 
songs, and suspending or unsuspending the queue. Finally, it will also include 
tools for the host to pause and play the music, and control the volume.*/

import * as React from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
//import './components.css' // eventually import a proper css file


var isHost = true; //Global variable to determine whether to render host-only elements. Should not be changed after startup.

// External Interface Functions

/**
 * Request Queue API call to the Universal Queue. 
 * 
 * The Universal Queue will send back the data of all songs in the queue, which the website queue can then use to show all songs currently in the queue.
 *
 * @return {Array} list of songs
 */
function requestQueue() {
	// Send a request queue API call to the universal queue.
	// Returns the list of songs currently in the queue.
	return []

}

/**
 * Sends a Remove from Queue API call to the Universal Queue. 
 * 
 * This will remove the specified instance of that song from the queue, and then result in the Universal Queue sending back an Update Queue call.
 *
 * @param {song} song The full data of the song to remove
 * 
 * @return {int} status of api call
 */
function removeSong(song) {
	// Send a remove song API call to the universal queue.
	// Return the status of the call
	return 0;
}

/**
 * Sends a Suspend Queue API call to the Spotify class. 
 * 
 * This will cause every submitted song to automatically reject, regardless of the source.
 * 
 * @return {int} status of api call
 */
function suspendQueue() {
	// Send a suspend queue API call to the universal queue.
	// Return the status of the call
	return 0;
}

/**
 * Sends a Resume Queue API call to the Spotify class. 
 * 
 * If the queue is currently suspended, it will be unsuspended.
 * 
 * @return {int} status of api call
 */
function resumeQueue() {
	// Send a resume queue API call to the universal queue.
	// Return the status of the call
	return 0;
}

/**
 * Sends a Pause API call to the Spotify class. 
 * 
 * @return {int} status of api call
 */
function pauseMusic() {
	// Send a pause music API call to the universal queue.
	// Return the status of the call
	return 0;
}

/**
 * Sends a Resume API call to the Spotify class. 
 * 
 * @return {int} status of api call
 */
function resumeMusic() {
	// Send a resume music API call to the universal queue.
	// Return the status of the call
	return 0;
}

/**
 * Sends a Pause API call to the Spotify class. 
 * 
 * @param {int} vol The volume to set the music to.
 * 
 * @return {int} status of api call
 */
function changeVolume(vol) {
	// Send a change volume API call to the universal queue.
	// Return the status of the call
	return 0;
}

// GUI functions

function Song(props) {
	// Returns the HTML to display one song in the queue.
	// props.id - id of song in Spotify
	// props.name - name of song
	// props.albumcover - link to song's album art
	// props.artist - artist of song
	return ( 
	 <>
	  {/* Display the Name, album cover, Artist, etc*/}
	  <DeleteButton id={props.id}/>
	 </>
	);
}

function DeleteButton(props) {
	// Returns the HTML to conditionally display a delete button
	// props.id - song id to delete
	if (isHost) {
		return <>({/* HTML containing a button that calls removeSong*/})</>
	}
	return <></>
}

export default function DisplayedQueue(props) {
	//props.isHost: boolean

	/**
   	 * songs: a list of song objects
	 * Each song has the following attributes:
	 * 	id {int} the song's Spotify ID
	 *  name {String} 
	 *  artist {String} 
	 *  albumcover {String} A link to an image of the song's cover
   	 * @type {Array}
   	*/
	const [songs, updateSongs] = useState([]);
	
	// On startup (using useEffect({},[])), initialize isHost using prop.isHost
	// Note: may have to switch isHost to a context instead
	useEffect( () => {
		//isHost = prop.isHost
	}, [])

	/* On startup, call the requestQueue() function asynchronously with useEffect
	 and use it to update songs */
	
	// On startup, start an async function to handle update_ui
	useEffect( () => {
		//isHost = prop.isHost
	}, [])
	
	
	return (
	 <Box sx={{ width: '100%' }}>
	
	  {/*If you're a host, display the host controls*/}
	  {isHost==true &&
	   <>
	    {/*Buttons to start/stop the queue and play/pause the music
		   and a slider to set volume*/}
	   </>
	  }

	  {/*Regardless of whether you're a host or not, 
	  	make a stack to display the queue*/}

	  <Stack>
	   {/* For each song in songs, generate an entry*/}
	   {songs.map(
		(song) => <Song >
		 {/*to optimize this: include a key that is unique to each entry*/}
		 id={song.id} 
		 name={song.name} 
		 albumcover={song.albumcover} 
		 artist={song.artist}
		</Song>
	   )} 
	  </Stack>

	 </Box>
	);
}
