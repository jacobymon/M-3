/*The Website Queue will give a visible representation of the current state of
 the Universal Queue to all users of the website, which will allow them to see
 what songs are playing, which will play in the future, and whether their songs
got properly added to the queue. For hosts, it will also include the 
functionality that the host can use to manage the Universal Queue- removing 
songs, and suspending or unsuspending the queue. Finally, it will also include 
tools for the host to pause and play the music, and control the volume.*/

import React, { useState, useEffect, useRef} from 'react';
import './WebsiteQueue.css' // eventually import a proper css file
import axios from 'axios';
//const axios = require('axios').default;

const MAX_QUEUE_RE_REQUESTS = 2;
const WAIT_AFTER_FAILED_RQU = 60*1000 //miliseconds
const HOSTTOOLS_WARNING_TIME = 5*1000 //miliseconds
const REQUEST_QUEUE_CALL = "http://localhost:8080/request_update"
const REQUEST_QUEUE_UPDATE_CALL = "http://localhost:8080/update_ui"
const TESTSONGS = [
	{
		"id": "3v66DjMBSdWY0jy5VVjHI2",
		"name": "All I Want For Christmas Is You",
		"artist": "Mariah Carey",
		"albumcover": "https://m.media-amazon.com/images/I/71X9F2m7-kL._UF1000,1000_QL80_.jpg",
		"submissionID": 2
	}, {
		"id": "xkcdykcd",
		"name": "testsong",
		"artist": "totaly real artist",
		"albumcover": "https://m.media-amazon.com/images/I/71X9F2m7-kL._UF2000,1000_QL80_.jpg",
		"submissionID": 3
	}
]


var isHost = true; //Global variable to determine whether to render host-only elements. Should not be changed after startup.
//const isHostContext = createContext();
var cookie = "h"

// External Interface Functions

/**
 * Request Queue API call to the Universal Queue. 
 * 
 * The Universal Queue will send back the data of all songs in the queue, which the website queue can then use to show all songs currently in the queue.
 *
 * @param {function} updateQueueError The function to set a new error code (and
 * 										force the component to re-render)
 * @param {function} updateSongs The function from displayedQueue to change the data in
 * 									songs (and re-render the displayed queue)
 */
async function requestQueue(updateQueueError, updateSongs) {
	// Send a request queue API call to the universal queue.
	try {
		const response = await axios.get(REQUEST_QUEUE_CALL);
		updateSongs(response.data.songs);
		updateQueueError(0) // all is well
	} catch (error) {
		if(error.response) {
			updateQueueError(error.response.status)
		} else {
			updateQueueError(500)
		}
	}
}

/**
 * Sends a request to the Universal Queue to notify this website instance of any
 * changes to the queue. If it gets a response, immedaitely set the displayed
 * queue to use the new up-to-date data.
 * 
 * @param {function} updateQueueError The function to set a new error code (and
 * 										force the component to re-render)
 * @param {function} updateSongs The function from displayedQueue to change the data in
 * 									songs (and re-render the displayed queue)
 */
async function requestQueueUpdates (updateQueueError, updateSongs) {
	function sleep(ms) {return new Promise(resolve => setTimeout(resolve, ms))}

	while(true) {
		try {
			// it could take minutes to get this response, since it 
			// only gets returned once the queue changes.
			const response = await axios.get(REQUEST_QUEUE_UPDATE_CALL);
			updateSongs(response.data.songs);
			updateQueueError(0) // all is well
		} catch (error) {
			var errorcode;
			if (error.status) errorcode = error.status;
			else errorcode = 500;

			if (errorcode === 408) { //Request Timeout
				/* Our request timed out (too long without the Unversal Queue updating),
				* but we still want to be notified of updates, so request again 
				* immedaitely.*/
				// do nothing and loop back
			} else if (errorcode === 429 ) { //Too many requests
				/* The server is under strain, so don't make a request for a while.*/
				await sleep(WAIT_AFTER_FAILED_RQU)
			} else {
				/* Something unexpected has happened, set an actual error */
				updateQueueError(errorcode)
				//Sleep for WAIT_AFTER_FAILED_RQU seconds
				await sleep(WAIT_AFTER_FAILED_RQU)
			}
		}
	}
};

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
		// Set hostToolsError
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
	// If failed: set hostToolsError to error
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
	// If failed: set hostToolsError to error
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
	// If failed: set hostToolsError to error
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
	// If failed: set hostToolsError to error
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
	// If failed: set hostToolsError to error
	// Return the status of the request
	return 0;
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
	 <div className="songListItem">
	  {/* Display the Name, album cover, Artist, etc*/}
	  <div className="songTitle">{props.name}</div>
	  <div className="songArtist">{props.artist}</div>
	  <img className="songCover" src={props.albumcover} alt=""></img>
	  <DeleteButton submissionID={props.submissionID}/>
	 </div>
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
		return <>
		{/* HTML containing a button that calls removeSong(submissionID)*/}
		</>
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
function DisplayedQueue(props) {

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

	/**
	 * queueError: the most recent errorcode for updating the queue
	 * @type {int}
	 */
	const [queueError, updateQueueError] = useState(0);

	/**
	 * hostToolsError: the most recent errorcode for host tools
	 * @type {int}
	 */
	const [hostToolsError, updateHostToolsError] = useState(0);

	/**
	 * failedRequests: counter for how many requests have failed in a row.
	 * useRef preserves this between renders.
	 */
	const failedRequests = useRef(0);


	/* On startup (aka using useEffect({},[])),call the requestQueue() function
	 asynchronously with useEffect and use it to update songs */
	 useEffect( () => {
		requestQueue(updateQueueError, updateSongs)
	}, [])
	
	// Set isHost and cookie to match whatever is in props
	useEffect( () => {
		isHost = props.isHost
		cookie = props.cookie
	}, [props])

	
	// On startup, start an async function to request any updates to the queue
	useEffect( () => {
		requestQueueUpdates(updateQueueError, updateSongs)
	}, [])

	/* When queueError changes (aka using useEffect({},[queueError])),
		attempt to recover from the error and get an up-to-date queue.
	*/
	useEffect( () => {
		if (queueError === 0) {
			failedRequests.current = 0
		} else if (failedRequests.current <= MAX_QUEUE_RE_REQUESTS) {
			// If queue update fails, re-request the queue.
			failedRequests.current += 1
			requestQueue(updateQueueError, updateSongs)
		} else {
			// If too many requests fail in a row, notify the user
			// The simplest solution is to create a fake "queue out of sync, please refresh" song
			updateSongs([{
				"id": "", "submission_id": 0,
				"name": "QUEUE OUT OF SYNC",
				"artist": "please refresh the page",
				"albumcover": ""
			}])
		}
	}, [queueError])

	// When HostToolsError changes, attempt to recover.
	useEffect( () => {
		// Set hostToolsError to 0 after some time passes, 
		// so the "submission failed" warning dissapears.
		setTimeout(
			() => {updateHostToolsError(0)},
			HOSTTOOLS_WARNING_TIME
		)
	}, [hostToolsError]) 
	
	
	return (
	 <>

	  {/*If there's an error in the host tools, display an error message*/}
	  {hostToolsError!==0 &&
	   <>
	    {/*TODO Display the error message*/}
	   </>
	  }
	
	  {/*If you're a host, display the host controls*/}
	  {isHost===true &&
	   <>
	    {/*TODO Buttons to start/stop the queue and play/pause the music
		   and a slider to set volume*/}
	   </>
	  }

	  {/*Regardless of whether you're a host or not, 
	  	display an array of songs in the queue*/}
	  <div className="songListContainer">

		<div className="songListTitle">Current Queue</div>

	   {/* For each song in songs, generate an entry*/}
	   { songs?.map(
		(song) => <Song
		 id={song.id} 
		 name={song.name} 
		 albumcover={song.albumcover} 
		 artist={song.artist}
		 submissionID={song.submissionID} 
		 key={song.submissionID}>
		 {/*the key element used by react to better handle song objects */}
		</Song>
	   )}
	  </div>

	 </>
	);
}
export default DisplayedQueue;

// For testing only
export {requestQueue, requestQueueUpdates};
export {Song};
export {REQUEST_QUEUE_CALL, REQUEST_QUEUE_UPDATE_CALL};
