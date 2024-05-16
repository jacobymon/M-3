/*The Website Queue will give a visible representation of the current state of
 the Universal Queue to all users of the website, which will allow them to see
 what songs are playing, which will play in the future, and whether their songs
got properly added to the queue. For hosts, it will also include the 
functionality that the host can use to manage the Universal Queue- removing 
songs, and suspending or unsuspending the queue. Finally, it will also include 
tools for the host to pause and play the music, and control the volume.*/

import React, { useState, useEffect, useRef, 
				createContext, useContext} from 'react';
import './WebsiteQueue.css' // eventually import a proper css file
import axios from 'axios';
import volume_down from "../content/volume_down.png"
import volume_up from "../content/volume_up.png"
//const axios = require('axios').default;

const MAX_QUEUE_RE_REQUESTS = 2;
const WAIT_AFTER_FAILED_RQU = 60*1000 //miliseconds
const HOSTTOOLS_WARNING_TIME = 15*1000 //miliseconds
const QUEUE_POLLING_TIME = 1*1000 //miliseconds
const RECHECK_ISHOST_TIME = 1*1000 //miliseconds

const VERIFY_HOST_CALL = `http://${process.env.REACT_APP_BACKEND_IP}:8080/verify_host`

const REQUEST_QUEUE_CALL = `http://${process.env.REACT_APP_BACKEND_IP}:8080/request_update`
const REQUEST_QUEUE_UPDATE_CALL = `http://${process.env.REACT_APP_BACKEND_IP}:8080/update_ui` //TODO, on backburner

const DELETE_SONG_CALL = `http://${process.env.REACT_APP_BACKEND_IP}:8080/remove_song` 

const PAUSE_SONG_CALL = `http://${process.env.REACT_APP_BACKEND_IP}:8080/pause_music` 
const RESUME_SONG_CALL = `http://${process.env.REACT_APP_BACKEND_IP}:8080/unpause_music` 
const SUSPEND_QUEUE_CALL = `http://${process.env.REACT_APP_BACKEND_IP}:8080/suspend_queue`
const RESUME_QUEUE_CALL = `http://${process.env.REACT_APP_BACKEND_IP}:8080/unsuspend_queue` 
const CHANGE_VOLUME_CALL = `http://${process.env.REACT_APP_BACKEND_IP}:8080/change_volume` //TODO, on backburner


// eslint-disable-next-line
const TESTSONGS = [ // For making sure rendering works visually
	{
		"name": "All I Want For Christmas Is You",
		"artist": "Mariah Carey",
		"albumname": "Mariah Carey's Best Hits",
		"albumcover": "https://m.media-amazon.com/images/I/71X9F2m7-kL._UF1000,1000_QL80_.jpg",
		"submissionID": 2
	}, {
		"name": "testsong",
		"artist": "totaly real artist",
		"albumname": "100% real album",
		"albumcover": "https://m.media-amazon.com/images/I/71X9F2m7-kL._UF2000,1000_QL80_.jpg",
		"submissionID": 3
	}
]

const IsHostContext = createContext(); // context to share whether you're the host or not
const CookieContext = createContext(); // context to share the cookie
const HostToolsContext = createContext(); // context to share updateHostToolsError with other functions

// External Interface Functions

/**
 * Function to check whether you're the host or not,
 * Then call the hooks to update this 
 */
async function verify_host(updateIsHost, updateCookie) {
	try {
		const response = await axios.get(VERIFY_HOST_CALL, {timeout: 5000});

		console.log("***********************" + response.data[0])

		updateIsHost(response.data["updateIsHost"])
		updateCookie(response.data["updateCookie"])
	} catch (error) {
		// Keep displaying the user UI, and rerequest soon.
		setTimeout(() => {verify_host(updateIsHost, updateCookie)}, RECHECK_ISHOST_TIME)
	}
}

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
		const response = await axios.get(REQUEST_QUEUE_CALL, {timeout: 5000});

		console.log(response)

		updateSongs(response.data);
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
 * Short Polling - poll the server every so often to update the queue
 * 
 * @param {function} updateQueueError The function to set a new error code (and
 * 										force the component to re-render)
 * @param {function} updateSongs The function from displayedQueue to change the data in
 * 									songs (and re-render the displayed queue)
 */
async function autoCallRequestQueue(updateQueueError, updateSongs) {
	function sleep(ms) {return new Promise(resolve => setTimeout(resolve, ms))}
	while (true) {
		await sleep(QUEUE_POLLING_TIME)
		requestQueue(updateQueueError, updateSongs)
	}
}

/**
 * Sends a request to the Universal Queue to notify this website instance of any
 * changes to the queue. If it gets a response, immedaitely set the displayed
 * queue to use the new up-to-date data.
 * 
 * Not in use currently, temporarily using short polling instead.
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

			// Handle response here

			updateSongs(response.data);
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
async function removeSong(submissionID, cookie, updateHostToolsError) {

	try {
		const response = await axios.post(DELETE_SONG_CALL,
											{"id":submissionID, "cookie":cookie}, 
											{timeout:5000})

		return response.status;
	} catch (error) {
		updateHostToolsError(error.status? error.status : 500)
		return error.status? error.status : 500;
	}
}

/**
 * Sends a Suspend Queue API call to the Spotify class. 
 * 
 * This will cause every submitted song to automatically reject, regardless of the source.
 * 
 * @return {int} status of api call
 */
async function suspendQueue(cookie, updateHostToolsError) {
	// Send a suspend queue API call to the universal queue.
	// If failed: set hostToolsError to error
	// Return the status of the request

	try {
		const response = await axios.post(SUSPEND_QUEUE_CALL, {"cookie":cookie}, {timeout:5000})

		// Handle the response from here

		return response.status;
	} catch (error) {
		updateHostToolsError(error.status? error.status : 500)
		return error.status? error.status : 500;
	}
}

/**
 * Sends a Resume Queue API call to the Spotify class. 
 * 
 * If the queue is currently suspended, it will be unsuspended.
 * 
 * @return {int} status of api call
 */
async function resumeQueue(cookie, updateHostToolsError) {
	// Send a resume queue API call to the universal queue.
	// If failed: set hostToolsError to error
	// Return the status of the request

	try {
		const response = await axios.post(RESUME_QUEUE_CALL, {"cookie":cookie}, {timeout:5000})

		// Handle the response from here

		return response.status;
	} catch (error) {
		updateHostToolsError(error.status? error.status : 500)
		return error.status? error.status : 500;
	}
}

/**
 * Sends a Pause API call to the Spotify class. 
 * 
 * @return {int} status of api call
 */
async function pauseMusic(cookie, updateHostToolsError) {
	// Send a pause music API call to the universal queue.
	// If failed: set hostToolsError to error
	// Return the status of the request

	try {
		const response = await axios.post(PAUSE_SONG_CALL, {"cookie":cookie}, {timeout:5000})

		// Handle the response from here

		return response.status;
	} catch (error) {
		updateHostToolsError(error.status? error.status : 500)
		return error.status? error.status : 500;
	}
}

/**
 * Sends a Resume API call to the Spotify class. 
 * 
 * @return {int} status of api call
 */
async function resumeMusic(cookie, updateHostToolsError) {
	// Send a resume music API call to the universal queue.
	// If failed: set hostToolsError to error
	// Return the status of the request

	try {
		const response = await axios.post(RESUME_SONG_CALL, {"cookie":cookie}, {timeout:5000})

		// Handle the response from here

		return response.status;
	} catch (error) {
		updateHostToolsError(error.status? error.status : 500)
		return error.status? error.status : 500;
	}
}

/**
 * Sends a Change Volume API call to the Spotify class. 
 * 
 * @param {int} vol The volume to set the music to.
 * 
 * @return {int} status of api call
 */
async function changeVolume(vol, cookie, updateHostToolsError) {
	// TODO: no actual use for this until superusers

	// Send a change volume API call to the universal queue.
	// If failed: set hostToolsError to error
	// Return the status of the request
	
	console.log(vol);
	try {
		const response = await axios.post(CHANGE_VOLUME_CALL, {"vol": vol,"cookie":cookie}, {timeout:5000})

		// Handle the response from here

		return response.status;
	} catch (error) {
		updateHostToolsError(error.status? error.status : 500)
		return error.status? error.status : 500;
	}
}

// GUI functions

/**
 * React component to display the data of a single song in the queue
 * 
 * @param {String} props.name name of song
 * @param {String} props.albumname name of album the song is on
 * @param {String} props.albumcover link to an image of the song's album coversong's album cover
 * @param {String} props.artist name of song's artist
 * @param {int} props.submissionID unique ID for each song entry in the queue
 * 
 * @return HTML code for one song entry
 */
function Song(props) {
	return ( 
	 <div className="songListItem">
	  {/* Display the Name, album cover, Artist, etc*/}
	  <div className="songTitle">{props.name}</div>
	  <div className="songArtist">{props.artist}</div>
	  <div className="songAlbum">{props.albumname}</div>
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
	const isHost = useContext(IsHostContext)
	const cookie = useContext(CookieContext)
	const updateHostToolsError = useContext(HostToolsContext);

	if (isHost && (props.submissionID !== -1)) {
		return <button 
			data-testid="removeSongButton"
			className="removeSongButton"
			onClick={() => {removeSong(props.submissionID, cookie, updateHostToolsError)}}
		>X</button>
	} 
	return <></>
	
	
}

/**
 * React component to display host control tools.
 * 
 * @return HTML code for host tools.
 */
function HostToolsMenu() {
	const isHost = useContext(IsHostContext)
	const cookie = useContext(CookieContext)
	const updateHostToolsError = useContext(HostToolsContext)

	if (isHost) {
		return (
		<div className='hostToolbar'>
			<button className="hostToolButton" onClick={() => pauseMusic(cookie, updateHostToolsError)}>Pause</button>
			<button className="hostToolButton" onClick={() => resumeMusic(cookie, updateHostToolsError)}>Resume</button>
			<button className="hostToolButton" onClick={() => suspendQueue(cookie, updateHostToolsError)}>Suspend Queue</button>
			<button className="hostToolButton" onClick={() => resumeQueue(cookie, updateHostToolsError)}>Resume Queue</button>
			{/*<div className='volumeSliderContainer'>
			 <img className="volumeImage" src={volume_down} alt='Lower Volume'/>
			 <input className="volumeSlider" title="Change Volume" type="range" onMouseUp={(e) => changeVolume(e.target.value, cookie, updateHostToolsError)}/>
			 <img className="volumeImage" src={volume_up} alt='Raise Volume'/>
			</div>*/}
		</div>
		)
	} 
	return <></>
	
}

/**
 * React component to display the current queue of songs.
 * 
 * @return HTML code for the current song queue.
 */
function DisplayedQueue() {

	/**
   	 * songs: a list of song objects
	 * Each song has the following attributes:
	 *  name {String} 
	 *  artist {String} 
	 *  albumname {String} 
	 *  albumcover {String} A link to an image of the song's cover
	 *  submissionID {int} ID for each song submission
   	 * @type {Array}
   	*/
	const [songs, updateSongs] = useState([]);

	/**
	 * queueError: the most recent errorcode for updating the queue.
	 * 0 if the most recent call succeeded.
	 * -1 if no recent queue error.
	 * @type {int}
	 */
	const [queueError, updateQueueError] = useState(-1);

	/** hostToolsError: the most recent errorcode for host tools @type {int} */
	const [hostToolsError, updateHostToolsError] = useState(0);

	/**
	 * failedRequests: counter for how many requests have failed in a row.
	 * useRef preserves this between renders.
	 */
	const failedRequests = useRef(0);

	const [isHost, updateIsHost] = useState(false);

	/** cookie to be sent with any host-only api calls @type {string} */
	const [cookie, updateCookie] = useState("");



	/* On startup (aka using useEffect({},[])),call the requestQueue() function
	 asynchronously with useEffect and use it to update songs */
	 useEffect( () => {
		requestQueue(updateQueueError, updateSongs)
	}, [])
	
	// Check for whether you're the host or not
	useEffect(() => {
		verify_host(updateIsHost, updateCookie)
	}, [])

	
	// On startup, start an async function to request any updates to the queue
	useEffect( () => {
		// TEMP - long polling won't work on backend, so just short polling
		// requestQueueUpdates(updateQueueError, updateSongs)
		autoCallRequestQueue(updateQueueError, updateSongs)
	}, [])

	/* When queueError changes (aka using useEffect({},[queueError])),
		attempt to recover from the error and get an up-to-date queue.
	*/
	useEffect( () => {
		if (queueError === 0) {
			//If queueError changes to 0 (all is well), reset the counter
			failedRequests.current = 0
		} else if (queueError === -1) {
			// do nothing
		} else if (failedRequests.current <= MAX_QUEUE_RE_REQUESTS) {
			// If requestQueue returns 408 twice, queueError will not change,
			// so the hook will not fire. To fix this, set the most recent error to -1,
			// so that queueError will update no matter what.
			updateQueueError(-1)

			// If queue update fails, re-request the queue.
			failedRequests.current += 1
			requestQueue(updateQueueError, updateSongs)
		} else {
			// If too many requests fail in a row, notify the user
			// The simplest solution is to create a fake "queue out of sync, please refresh" song
			updateSongs([{
				"submission_id": -1,
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

	/* DEBUG ONLY: whenever songs changes, change it back to test songs. */
	useEffect( () => {
		// updateIsHost(true)
		// updateSongs(TESTSONGS)
	}, [isHost, songs])

	return (
	 <>
	  
	  {/* share isHost and cookie through the whole component*/}
	  <IsHostContext.Provider value={isHost}>
	  <CookieContext.Provider value={cookie}>
	  <HostToolsContext.Provider value={updateHostToolsError}>

	  {hostToolsError!==0 &&
	   <>
	    <h2>Error with Host Tools: Code {hostToolsError}</h2>
	   </>
	  }

	  {/*Display the host tools menu. It will only be visible if you're the host*/}
	  <HostToolsMenu></HostToolsMenu>

	  {/*Debug button for refreshing queue*/}
	  {/*<button className="hostToolButton refreshButton" onClick={() => requestQueue(updateQueueError, updateSongs)}>Refresh Queue</button>*/}

	  {/*Regardless of whether you're a host or not, 
	  	display an array of songs in the queue*/}
	  <div className="songListContainer">
	   {/* For each song in songs, generate an entry*/}
	   { songs?.map(
		(song) => <Song
		 name={song.name} 
		 albumname={song.albumname} 
		 albumcover={song.albumcover} 
		 artist={song.artist}
		 submissionID={song.submissionID} 
		 key={song.submissionID}>
		 {/*the key element used by react to better handle song objects */}
		</Song>
	   )}
	  </div>

      </HostToolsContext.Provider>
	  </CookieContext.Provider>
	  </IsHostContext.Provider>

	 </>
	);
}
export default DisplayedQueue;

// For testing only
export {requestQueue, requestQueueUpdates};
export {Song};
export {VERIFY_HOST_CALL, REQUEST_QUEUE_CALL, REQUEST_QUEUE_UPDATE_CALL};
