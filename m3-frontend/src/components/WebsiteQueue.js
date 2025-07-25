/*The Website Queue will give a visible representation of the current state of
 the Universal Queue to all users of the website, which will allow them to see
 what songs are playing, which will play in the future, and whether their songs
got properly added to the queue. For hosts, it will also include the 
functionality that the host can use to manage the Universal Queue- removing 
songs, and suspending or unsuspending the queue. Finally, it will also include 
tools for the host to pause and play the music, and control the volume.*/

import React, { useState, useEffect, useRef, 
				createContext, useContext} from 'react';

// import io from 'socket.io-client';

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

const BACKEND_IP = process.env.REACT_APP_BACKEND_IP || 'localhost';
const VERIFY_HOST_CALL = `http://${BACKEND_IP}:8080/verify_host`;
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
const YouTubeControlContext = createContext();

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

// NEW: WebSocket-enabled YouTube Player Component
function YouTubeQueuePlayer({ currentSong, onSongEnd }) {
    const playerRef = useRef(null);
    const [isPlayerReady, setIsPlayerReady] = useState(false);
    const [currentVideoId, setCurrentVideoId] = useState(null);
    const [currentSubmissionId, setCurrentSubmissionId] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);

    // Initialize YouTube Player
    useEffect(() => {
        if (!window.YT) {
            const tag = document.createElement('script');
            tag.src = "https://www.youtube.com/iframe_api";
            const firstScriptTag = document.getElementsByTagName('script')[0];
            firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
        }

        window.onYouTubeIframeAPIReady = initializePlayer;
        
        if (window.YT && window.YT.Player) {
            initializePlayer();
        }
    }, []);

    // Handle song changes
    useEffect(() => {
        if (currentSong && isPlayerReady && playerRef.current) {
            console.log("Current song changed:", currentSong);
            
            const isYouTubeSong = currentSong.platform === "YouTube" || 
                                 currentSong.albumname === "YouTube";
            
            if (isYouTubeSong && currentSong.video_id) {
                const isDifferentVideo = currentVideoId !== currentSong.video_id;
                const isDifferentSubmission = currentSubmissionId !== currentSong.submissionID;
                
                if (isDifferentVideo || isDifferentSubmission) {
                    console.log(`Loading YouTube video: ${currentSong.video_id} (submission: ${currentSong.submissionID})`);
                    setCurrentVideoId(currentSong.video_id);
                    setCurrentSubmissionId(currentSong.submissionID);
                    setIsPlaying(false);
                    
                    setTimeout(() => {
                        if (playerRef.current) {
                            playerRef.current.loadVideoById(currentSong.video_id);
                        }
                    }, 100);
                } else {
                    console.log("Same video and submission already loaded, not reloading");
                }
            } else {
                setCurrentVideoId(null);
                setCurrentSubmissionId(null);
                setIsPlaying(false);
                if (playerRef.current) {
                    playerRef.current.stopVideo();
                }
            }
        }
    }, [currentSong, isPlayerReady, currentVideoId, currentSubmissionId]);

    // ADD THESE MISSING FUNCTIONS:
    const initializePlayer = () => {
        playerRef.current = new window.YT.Player("youtube-player", {
            height: "0",
            width: "0",
            videoId: "",
            playerVars: {
                autoplay: 1,
                controls: 0,
                disablekb: 1,
                fs: 0,
                modestbranding: 1,
                rel: 0,
                showinfo: 0,
                mute: 0,
                volume: 100
            },
            events: {
                onReady: onPlayerReady,
                onStateChange: onPlayerStateChange,
            },
        });
    };

    const onPlayerReady = () => {
        setIsPlayerReady(true);
        console.log("YouTube player ready");
        
        // Ensure player is unmuted and volume is set
        if (playerRef.current) {
            playerRef.current.unMute();
            playerRef.current.setVolume(100);
            console.log("YouTube player unmuted and volume set to 100%");
        }
    };

    const onPlayerStateChange = (event) => {
        console.log("YouTube player state changed:", event.data);
        
        const stateNames = {
            '-1': 'unstarted',
            '0': 'ended',
            '1': 'playing',
            '2': 'paused',
            '3': 'buffering',
            '5': 'cued'
        };
        
        console.log(`YouTube state: ${stateNames[event.data] || event.data}`);
        
        if (event.data === window.YT.PlayerState.ENDED) {
            console.log("YouTube song ended naturally");
            setIsPlaying(false);
            onSongEnd();
        } else if (event.data === window.YT.PlayerState.PLAYING) {
            console.log("YouTube song started playing");
            setIsPlaying(true);
            
            // Debug audio settings
            if (playerRef.current) {
                const isMuted = playerRef.current.isMuted();
                const volume = playerRef.current.getVolume();
                console.log(`Audio debug - Muted: ${isMuted}, Volume: ${volume}%`);
                
                if (isMuted) {
                    playerRef.current.unMute();
                    console.log("Force unmuted player");
                }
                if (volume < 100) {
                    playerRef.current.setVolume(100);
                    console.log("Set volume to 100%");
                }
            }
        } else if (event.data === window.YT.PlayerState.PAUSED) {
            console.log("YouTube song paused");
            setIsPlaying(false);
        } else if (event.data === window.YT.PlayerState.BUFFERING) {
            console.log("YouTube song buffering");
        } else if (event.data === window.YT.PlayerState.CUED) {
            console.log("YouTube song cued, starting playback");
            if (playerRef.current && !isPlaying) {
                setTimeout(() => {
                    playerRef.current.playVideo();
                }, 100);
            }
        } else if (event.data === window.YT.PlayerState.UNSTARTED) {
            console.log("YouTube player unstarted");
            setIsPlaying(false);
        }
    };

    // Control functions for host tools
    const controls = {
        playVideo: (videoId) => {
            if (playerRef.current && videoId) {
                if (currentVideoId !== videoId) {
                    playerRef.current.loadVideoById(videoId);
                    setCurrentVideoId(videoId);
                } else {
                    playerRef.current.playVideo();
                }
            }
        },
        pauseVideo: () => {
            if (playerRef.current) {
                playerRef.current.pauseVideo();
            }
        },
        stopVideo: () => {
            if (playerRef.current) {
                playerRef.current.stopVideo();
                setIsPlaying(false);
            }
        },
        isPlaying: () => isPlaying
    };

    return (
        <YouTubeControlContext.Provider value={controls}>
            <div id="youtube-player" style={{ display: "none" }}></div>
        </YouTubeControlContext.Provider>
    );
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

function HostToolsMenu({ songs }) {
    const isHost = useContext(IsHostContext);
    const cookie = useContext(CookieContext);
    const updateHostToolsError = useContext(HostToolsContext);
    const youtubeControls = useContext(YouTubeControlContext);
  
    const handlePlay = async () => {
        if (songs.length === 0) {
            console.log("No songs in the queue.");
            return;
        }
  
        const currentSong = songs[0];
        console.log("Attempting to play:", currentSong);
        
        if (currentSong.platform === "YouTube") {
            const videoId = extractVideoIdFromUri(currentSong.uri);
            console.log("Extracted video ID:", videoId);
            
            if (videoId) {
                try {
                    // Call backend to control YouTube
                    const response = await axios.post(
                        `http://${process.env.REACT_APP_BACKEND_IP}:8080/youtube_unpause`,
                        { video_id: videoId, cookie: cookie }
                    );
                    console.log("YouTube play response:", response.data);
                    
                    // Also control frontend player
                    if (youtubeControls) {
                        youtubeControls.playVideo(videoId);
                    }
                } catch (error) {
                    console.error("Error controlling YouTube:", error);
                    updateHostToolsError(500);
                }
            }
        } else {
            // Spotify or other platform
            resumeMusic(cookie, updateHostToolsError);
        }
    };
  
    const handlePause = async () => {
        if (songs.length === 0) {
            console.log("No songs in the queue.");
            return;
        }
  
        const currentSong = songs[0];
        console.log("Attempting to pause:", currentSong);
        
        if (currentSong.platform === "YouTube") {
            try {
                // Call backend to control YouTube
                const response = await axios.post(
                    `http://${process.env.REACT_APP_BACKEND_IP}:8080/youtube_pause`,
                    { cookie: cookie }
                );
                console.log("YouTube pause response:", response.data);
                
                // Also control frontend player
                if (youtubeControls) {
                    youtubeControls.pauseVideo();
                }
            } catch (error) {
                console.error("Error controlling YouTube:", error);
                updateHostToolsError(500);
            }
        } else {
            // Spotify or other platform
            pauseMusic(cookie, updateHostToolsError);
        }
    };

    const extractVideoIdFromUri = (uri) => {
        if (!uri) return null;
        if (uri.includes("youtube.com/watch?v=")) {
            return uri.split("v=")[1].split("&")[0];
        } else if (uri.includes("youtu.be/")) {
            return uri.split("youtu.be/")[1].split("?")[0];
        }
        return null;
    };
  
    if (isHost) {
        return (
            <div className="hostToolbar">
                <button className="hostToolButton" onClick={handlePause}>
                    Pause
                </button>
                <button className="hostToolButton" onClick={handlePlay}>
                    Resume
                </button>
                <button
                    className="hostToolButton"
                    onClick={() => suspendQueue(cookie, updateHostToolsError)}
                >
                    Suspend Queue
                </button>
                <button
                    className="hostToolButton"
                    onClick={() => resumeQueue(cookie, updateHostToolsError)}
                >
                    Resume Queue
                </button>
            </div>
        );
    }
    return <></>;
}


/**
 * React component to display the current queue of songs.
 * 
 * @return HTML code for the current song queue.
 */

function DisplayedQueue() {
    const [songs, updateSongs] = useState([]);
    const [currentSong, setCurrentSong] = useState(null);
    const [queueError, updateQueueError] = useState(-1);
    const [hostToolsError, updateHostToolsError] = useState(0);
    const failedRequests = useRef(0);
    const [isHost, updateIsHost] = useState(false);
    const [cookie, updateCookie] = useState("");

	useEffect(() => {
		if (songs.length > 0) {
			console.log("Current songs in queue:", songs);
			console.log("First song:", songs[0]);
			console.log("First song platform:", songs[0]?.platform);
			console.log("First song URI:", songs[0]?.uri);
		}
	}, [songs]);
  
    useEffect(() => {
        requestQueue(updateQueueError, updateSongs);
    }, []);
  
    useEffect(() => {
        verify_host(updateIsHost, updateCookie);
    }, []);
  
    useEffect(() => {
        autoCallRequestQueue(updateQueueError, updateSongs);
    }, []);

    // Handle queue errors
    useEffect(() => {
        if (queueError === 0) {
            failedRequests.current = 0;
        } else if (queueError === -1) {
            // do nothing
        } else if (failedRequests.current <= MAX_QUEUE_RE_REQUESTS) {
            updateQueueError(-1);
            failedRequests.current += 1;
            requestQueue(updateQueueError, updateSongs);
        } else {
            updateSongs([{
                "submissionID": -1,
                "name": "QUEUE OUT OF SYNC",
                "artist": "please refresh the page",
                "albumcover": ""
            }]);
        }
    }, [queueError]);

    // Handle host tools errors
    useEffect(() => {
        setTimeout(
            () => { updateHostToolsError(0) },
            HOSTTOOLS_WARNING_TIME
        );
    }, [hostToolsError]);

    // Set current song as first in queue
    useEffect(() => {
        if (songs.length > 0) {
            setCurrentSong(songs[0]);
        } else {
            setCurrentSong(null);
        }
    }, [songs]);

    const handleSongEnd = () => {
        console.log("Song ended, moving to next in queue");
        // You can implement logic here to remove the current song from queue
    };
  
    return (
        <>
            {/* Add the YouTube player */}
            <YouTubeQueuePlayer currentSong={currentSong} onSongEnd={handleSongEnd} />
            
            <IsHostContext.Provider value={isHost}>
                <CookieContext.Provider value={cookie}>
                    <HostToolsContext.Provider value={updateHostToolsError}>
                        {hostToolsError !== 0 && (
                            <>
                                <h2>Error with Host Tools: Code {hostToolsError}</h2>
                            </>
                        )}
  
                        <HostToolsMenu songs={songs}></HostToolsMenu>
  
                        <div className="songListContainer">
                            {songs?.map((song) => (
                                <Song
                                    name={song.name}
                                    albumname={song.albumname}
                                    albumcover={song.albumcover}
                                    artist={song.artist}
                                    submissionID={song.submissionID}
                                    key={song.submissionID}
                                ></Song>
                            ))}
                        </div>
                    </HostToolsContext.Provider>
                </CookieContext.Provider>
            </IsHostContext.Provider>
        </>
    );
}  
  // Keep DisplayedQueue as the default export

export default DisplayedQueue;

// For testing only
export {requestQueue};
export {Song};
export {VERIFY_HOST_CALL, REQUEST_QUEUE_CALL, REQUEST_QUEUE_UPDATE_CALL};
