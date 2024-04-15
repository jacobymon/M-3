/*The Website Queue will give a visible representation of the current state of
 the Universal Queue to all users of the website, which will allow them to see
 what songs are playing, which will play in the future, and whether their songs
got properly added to the queue. For hosts, it will also include the 
functionality that the host can use to manage the Universal Queue- removing 
songs, and suspending or unsuspending the queue. Finally, it will also include 
tools for the host to pause and play the music, and control the volume.*/

import React, { useState, useEffect } from 'react';
import axios from 'axios';
//import './components.css' // eventually import a proper css file


var isHost = true; //Global variable to determine whether to render host-only elements. Should not be changed after startup.
//const isHostContext = createContext();
var cookie = "h"
var queueError = 0;
var hostToolsErrorCode = 0;

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
	// If Successful:
		// Returns the list of songs currently in the queue.
	// ELse If Request Error but no response:
		// Set the error code globally
		// Return an empty queue
	// Else If Server Returns an Error:
		// Set the error code globally
		// Return an empty queue
	return []

}

/**
 * Sends a Remove from Queue API call to the Universal Queue. 
 * 
 * This will remove the specified instance of that song from the queue, and then result in the Universal Queue sending back an Update Queue call.
 *
 * @param {int} submissionID The ID of the song in the queue to remove
 * 
 * @return {int} status of api call
 */
function removeSong(submissionID) {
	// Send a remove song API call to the universal queue.
	// If song already not there:
		// Request queue
	// If cookie wrong / any other failure:
		// Set hostToolsErrorCode
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
	// If failed: set hostToolsErrorCode to error
	// Return the status of the request
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
	// If failed: set hostToolsErrorCode to error
	// Return the status of the request
	return 0;
}

/**
 * Sends a Pause API call to the Spotify class. 
 * 
 * @return {int} status of api call
 */
function pauseMusic() {
	// Send a pause music API call to the universal queue.
	// If failed: set hostToolsErrorCode to error
	// Return the status of the request
	return 0;
}

/**
 * Sends a Resume API call to the Spotify class. 
 * 
 * @return {int} status of api call
 */
function resumeMusic() {
	// Send a resume music API call to the universal queue.
	// If failed: set hostToolsErrorCode to error
	// Return the status of the request
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
	// If failed: set hostToolsErrorCode to error
	// Return the status of the request
	return 0;
}


/**
 * Sends a request to the Universal Queue to notify this website instance of any
 * changes to the queue. If it gets a response, immedaitely set the displayed
 * queue to use the new up-to-date data.
 * 
 * @param {function} updateSongs The function from displayedQueue to change the data in
 * 									songs (and re-render the displayed queue)
 */
function requestQueueUpdates(updateSongs) {
	//Call Request Queue Updates
	//If response is 201: we're given a new queue to use
		// update songs to be that queue
		// Call requestQueueUpdates again immediately
	//Else If response is 408 (Request Timeout)
		/* Our request timed out (too long without the Unversal Queue updating),
	     * but we still want to be notified of updates, so request again 
		 * immedaitely */
		// Call requestQueueUpdates again immediately
	//Else If response is 429 (Too Many Requests)
		/* The server is under strain, so don't make a request for a while.*/
		// Call requestQueueUpdates after a 1-min delay
	//Else if any other queue errors:
		// set queueError
	
}

// GUI functions

/**
 * React component to display the data of a single song in the queue
 * 
 * @param {String} props.id id of song in Spotify
 * @param {String} props.name name of song
 * @param {String} props.albumcover link to an image of the song's album cover
 * @param {String} props.artist the artist
 * @param {int} props.submissionID unique ID for each song entry in the queue
 * 
 * @return HTML code for one song entry
 */
function Song(props) {
	// Returns the HTML to display one song in the queue.
	return ( 
	 <>
	  {/* Display the Name, album cover, Artist, etc*/}
	  <DeleteButton submissionID={props.submissionID}/>
	 </>
	);
}


/**
 * React component to conditionally display a "delete song" button
 * 
 * @param {int} props.submissionID the ID of this song
 * 
 * @return HTML code for the button
 */
function DeleteButton(props) {
	// Returns the HTML to conditionally display a delete button
	// props.submissionID - the song submission to remove
	if (isHost) {
		return <>({/* HTML containing a button that calls removeSong(submissionID)*/})</>
	}
	return <></>
}


/**
 * React component to display the current queue of songs.
 * 
 * @param {Boolean} props.isHost
 * @param {String} props.cookie the host cookie is sent along with any host-only API request
 * 
 * @return HTML code for the current song queue.
 */
function DisplayedQueue() {

	/**
   	 * songs: a list of song objects
	 * Each song has the following attributes:
	 * 	id {int} the song's Spotify ID
	 *  name {String} 
	 *  artist {String} 
	 *  albumcover {String} A link to an image of the song's cover
	 *  submissionID {int} ID for each song submission
   	 * @type {Array}
   	*/
	const [songs, updateSongs] = useState([]);
	
	// On startup (aka using useEffect({},[])), initialize isHost using prop.isHost
	// Note: may have to switch isHost to a context instead
	useEffect( () => {
		//isHost = prop.isHost
		// cookie = prop.cookie
	}, [])

	/* On startup, call the requestQueue() function asynchronously with useEffect
	 and use it to update songs */
	useEffect( () => {
		//call requestQueue()
		//set songs to the result
	}, [])

	
	// On startup, start an async function to request any updates to the queue
	useEffect( () => {
		// Asynchronously start requestQueueUpdates(), and pass it updateSongs
	}, [])

	/* When queueError changes (aka using useEffect({},[queueError])),
		attempt to recover from the error and get an up-to-date queue.
	*/
	useEffect( () => {
		// If queueError != 0:
			//attempt to call request queue

		// If too many requests fail in a row, notify the user
			// (easiest: could empty out songs and replace it with a fake 'queue out of sync, please refresh' song
			// (could also make the stack conditional)
			// (could also make a separate 'queue out of sync' popup)
	}, [queueError])

	//Handle any host tool errors
	useEffect( () => {
		// Set hostToolsErrorCode to 0 after some time passes, 
		// so that the error message dissapears
	}, [hostToolsErrorCode]) 
	
	
	return (
	 <>

	  {/*If there's an error code, display that*/}
	  {hostToolsErrorCode!=0 &&
	   <>
	    {/*Display the error message*/}
	   </>
	  }
	
	  {/*If you're a host, display the host controls*/}
	  {isHost==true &&
	   <>
	    {/*Buttons to start/stop the queue and play/pause the music
		   and a slider to set volume*/}
	   </>
	  }

	  {/*Regardless of whether you're a host or not, 
	  	display an array of songs in the queue*/}

	  <>
	   {/* For each song in songs, generate an entry*/}
	   {songs.map(
		(song) => <Song >
		 {/*to optimize this: include a key that is unique to each entry*/}
		 id={song.id} 
		 name={song.name} 
		 albumcover={song.albumcover} 
		 artist={song.artist}
		 submissionID={song.submissionID}
		</Song>
	   )} 
	  </>

	 </>
	);
}
export default DisplayedQueue
