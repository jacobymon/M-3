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
    const currentVideoIdRef = useRef(null);
    const [isPlayerReady, setIsPlayerReady] = useState(false);
    const [currentVideoId, setCurrentVideoId] = useState(null);
    const [currentSubmissionId, setCurrentSubmissionId] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);

    // ADD: Method to get current playback time
    const getCurrentTime = () => {
        if (playerRef.current && typeof playerRef.current.getCurrentTime === 'function') {
            try {
                const currentTime = playerRef.current.getCurrentTime();
                console.log(`Current YouTube time: ${currentTime} seconds`);
                return currentTime;
            } catch (error) {
                console.error("Error getting current time:", error);
                return 0;
            }
        }
        return 0;
    };

    // ADD: Method to get total duration
    const getDuration = () => {
        if (playerRef.current && typeof playerRef.current.getDuration === 'function') {
            try {
                const duration = playerRef.current.getDuration();
                console.log(`YouTube duration: ${duration} seconds`);
                return duration;
            } catch (error) {
                console.error("Error getting duration:", error);
                return 0;
            }
        }
        return 0;
    };

    // ADD: Method to calculate remaining time
    const getRemainingTime = () => {
        const currentTime = getCurrentTime();
        const duration = getDuration();
        const remaining = Math.max(0, duration - currentTime);
        console.log(`Remaining time: ${remaining} seconds`);
        return remaining;
    };

	const sendProgressToBackend = async () => {
		try {
			const currentTime = getCurrentTime();
			const duration = getDuration();
			
			console.log(`Sending progress to backend: ${currentTime}/${duration} seconds`);
			
			const response = await fetch('http://localhost:8080/get_youtube_progress', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					current_time: currentTime,
					duration: duration,
					video_id: currentVideoId
				})
			});
			
			const data = await response.json();
			console.log('Backend progress response:', data);
			return data;
			
		} catch (error) {
			console.error('Error sending progress to backend:', error);
			return null;
		}
	};

	


    // UPDATE: Expose these methods to parent components via context or props
	useEffect(() => {
		window.youtubePlayerControls = {
			getCurrentTime,
			getDuration,
			getRemainingTime,
			sendProgressToBackend,
			playerRef: playerRef.current,
			// ADD: Direct pause/play methods
			pause: () => {
				console.log("Direct pause called");
				if (playerRef.current) {
					playerRef.current.pauseVideo();
				}
			},
			play: () => {
				console.log("Direct play called");
				if (playerRef.current) {
					playerRef.current.playVideo();
				}
			}
		};
		
		console.log('YouTube player controls exposed globally');
	}, [isPlayerReady, currentVideoId]);


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
            
            console.log("Is YouTube song:", isYouTubeSong);
            console.log("Player ready:", isPlayerReady);
            
            if (isYouTubeSong && currentSong.video_id) {
                // This is a YouTube song - play it
                const isDifferentVideo = currentVideoIdRef.current !== currentSong.video_id; // USE REF
                const isDifferentSubmission = currentSubmissionId !== currentSong.submissionID;
                
                // CHANGE: Always reload if we previously stopped the player for a Spotify song
                const wasPlayerStopped = currentVideoIdRef.current === null; // USE REF
                
                if (isDifferentVideo || isDifferentSubmission || wasPlayerStopped) {
                    console.log(`Loading YouTube video: ${currentSong.video_id} (submission: ${currentSong.submissionID})`);
                    console.log(`Reason: differentVideo=${isDifferentVideo}, differentSubmission=${isDifferentSubmission}, wasPlayerStopped=${wasPlayerStopped}`);
                    
                    // UPDATE BOTH STATE AND REF IMMEDIATELY
                    setCurrentVideoId(currentSong.video_id);
                    currentVideoIdRef.current = currentSong.video_id; // IMMEDIATE UPDATE
                    setCurrentSubmissionId(currentSong.submissionID);
                    setIsPlaying(false);
                    
                    setTimeout(() => {
                        if (playerRef.current) {
                            playerRef.current.loadVideoById(currentSong.video_id);
                        }
                    }, 100);
                } else {
                    console.log("Same video and submission already loaded");
                    // CHANGE: But check if player is actually playing
                    if (playerRef.current && !isPlaying) {
                        console.log("Player not playing, starting playback");
                        setTimeout(() => {
                            playerRef.current.playVideo();
                        }, 100);
                    }
                }
            } else {
                // This is NOT a YouTube song - stop and clear YouTube player
                console.log("=== NON-YOUTUBE SONG DETECTED - STOPPING YOUTUBE PLAYER ===");
                console.log("Stopping YouTube player for Spotify song:", currentSong?.name || "unknown");
                
                try {
                    // Stop the YouTube player completely
                    if (playerRef.current) {
                        playerRef.current.stopVideo();
                        playerRef.current.clearVideo();
                        console.log("YouTube player stopped and cleared");
                    }
                    
                    // Reset BOTH STATE AND REF
                    setCurrentVideoId(null);
                    currentVideoIdRef.current = null; // IMMEDIATE UPDATE
                    setCurrentSubmissionId(null);
                    setIsPlaying(false);
                    
                } catch (error) {
                    console.error("Error stopping YouTube player:", error);
                }
            }
        }
    }, [currentSong, isPlayerReady]);

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
		console.log("Current song at state change:", currentSong);
		
		// CHANGE: More robust check for YouTube songs
		const isCurrentSongYouTube = currentSong && 
			(currentSong.platform === "YouTube" || currentSong.albumname === "YouTube");
		
		// CHANGE: Use REF for immediate video ID check
		const hasVideoLoaded = currentVideoIdRef.current !== null && currentVideoIdRef.current !== "";
		
		console.log("Is current song YouTube?", isCurrentSongYouTube);
		console.log("Has video loaded?", hasVideoLoaded);
		console.log("Current video ID (ref):", currentVideoIdRef.current);
		console.log("Current video ID (state):", currentVideoId);
		
		// CHANGE: Allow state changes if we have a video loaded OR if it's a YouTube song
		if (!isCurrentSongYouTube && !hasVideoLoaded) {
			console.log("Ignoring YouTube state change - no YouTube song or video loaded");
			
			// Force stop the YouTube player if it's trying to play
			if (event.data === 1) { // Playing state
				console.log("Force stopping YouTube player - no valid YouTube context");
				if (playerRef.current) {
					playerRef.current.stopVideo();
				}
			}
			return;
		}
		
		// Rest of your existing YouTube state change logic...
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
			console.log("YouTube song paused - sending current progress to backend");
			// ADD: Automatically send progress when paused
			sendProgressToBackend();
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
        console.log("YouTube controls - playVideo called with:", videoId);
        if (playerRef.current) {
            if (videoId && currentVideoId !== videoId) {
                // Loading a new video
                console.log("Loading new video:", videoId);
                playerRef.current.loadVideoById(videoId);
                setCurrentVideoId(videoId);
            } else {
                // Just resuming current video
                console.log("Resuming current video");
                playerRef.current.playVideo();
            }
        }
    },
    pauseVideo: () => {
        console.log("YouTube controls - pauseVideo called");
        if (playerRef.current) {
            playerRef.current.pauseVideo();
        }
    },
    stopVideo: () => {
        console.log("YouTube controls - stopVideo called");
        if (playerRef.current) {
            playerRef.current.stopVideo();
            setIsPlaying(false);
        }
    },
    isPlaying: () => isPlaying
};

console.log("YouTube controls object created:", controls); // ADD THIS DEBUG LINE

    return (
        <YouTubeControlContext.Provider value={controls}>
			{console.log("YouTubeControlContext.Provider rendering with controls:", controls)}
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

function HostToolsMenu({ songs, youtubeControls }) {  
    const isHost = useContext(IsHostContext);
    const cookie = useContext(CookieContext);
    const updateHostToolsError = useContext(HostToolsContext);
  
    const handlePlay = async () => {
		if (songs.length === 0) {
			console.log("No songs in the queue.");
			return;
		}
	
		const currentSong = songs[0];
		console.log("=== RESUME DEBUG ===");
		console.log("Attempting to resume:", currentSong);
		console.log("Is YouTube song:", currentSong.platform === "YouTube" || currentSong.albumname === "YouTube");
		console.log("YouTube controls available:", !!youtubeControls);
		console.log("YouTube player controls global:", !!window.youtubePlayerControls);
		
		// Use unified resume for both YouTube and Spotify
		try {
			console.log("Sending resume request to backend...");
			const response = await resumeMusic(cookie, updateHostToolsError);
			console.log("Backend resume response:", response);
			
			if (response === 200) {
				console.log("Successfully resumed playback");
				
				// For YouTube songs, resume the player
				if ((currentSong.platform === "YouTube" || currentSong.albumname === "YouTube")) {
					// Try multiple methods to resume YouTube playback
					if (youtubeControls) {
						console.log("Resuming YouTube player via context...");
						youtubeControls.playVideo(); // Don't pass videoId, just resume
					} else if (window.youtubePlayerControls && window.youtubePlayerControls.playerRef) {
						console.log("Resuming YouTube player via global controls...");
						window.youtubePlayerControls.playerRef.playVideo();
					} else {
						console.log("No YouTube controls available for resume!");
					}
				}
			}
		} catch (error) {
			console.error("Error resuming playback:", error);
			updateHostToolsError(500);
		}
	};
  
    const handlePause = async () => {
		if (songs.length === 0) {
			console.log("No songs in the queue.");
			return;
		}
	
		const currentSong = songs[0];
		console.log("=== PAUSE DEBUG ===");
		console.log("Attempting to pause:", currentSong);
		console.log("Is YouTube song:", currentSong.platform === "YouTube" || currentSong.albumname === "YouTube");
		console.log("YouTube controls available:", !!youtubeControls);
		console.log("YouTube player controls global:", !!window.youtubePlayerControls);
		
		// For YouTube songs, send progress FIRST, then pause
		if ((currentSong.platform === "YouTube" || currentSong.albumname === "YouTube")) {
			// First, manually send current progress
			if (window.youtubePlayerControls && window.youtubePlayerControls.sendProgressToBackend) {
				console.log("Sending current progress before pausing...");
				await window.youtubePlayerControls.sendProgressToBackend();
			}
			
			// Then pause the YouTube player - try multiple methods
			if (youtubeControls) {
				console.log("Pausing YouTube player via context...");
				youtubeControls.pauseVideo();
			} else if (window.youtubePlayerControls && window.youtubePlayerControls.playerRef) {
				console.log("Pausing YouTube player via global controls...");
				window.youtubePlayerControls.playerRef.pauseVideo();
			} else {
				console.log("Trying direct player access...");
				// Try to find the player directly
				const playerElements = document.querySelectorAll('#youtube-player iframe');
				if (playerElements.length > 0) {
					console.log("Found YouTube iframe, trying to pause via postMessage");
					// This is a fallback - might not work due to CORS
				}
			}
		}
		
		// Send pause request to backend (this should now have progress data)
		try {
			console.log("Sending pause request to backend...");
			const response = await pauseMusic(cookie, updateHostToolsError);
			console.log("Backend pause response:", response);
			
			if (response === 200) {
				console.log("Successfully paused playback");
			}
		} catch (error) {
			console.error("Error pausing playback:", error);
			updateHostToolsError(500);
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

	// Set current song as first in queue with debouncing
	useEffect(() => {
		console.log("=== UPDATING CURRENT SONG ===");
		console.log("Songs array:", songs);
		console.log("Songs length:", songs.length);
		
		// Add a small delay to prevent race conditions with queue polling
		const timeoutId = setTimeout(() => {
			if (songs.length > 0) {
				const newSong = songs[0];
				console.log("Setting current song to:", newSong);
				
				// Only update if it's actually different
				setCurrentSong(prevSong => {
					if (!prevSong || prevSong.submissionID !== newSong.submissionID) {
						console.log("Current song actually changed, updating");
						return newSong;
					} else {
						console.log("Same song, not updating");
						return prevSong;
					}
				});
			} else {
				// Only clear after a longer delay to prevent race conditions
				console.log("No songs in queue - waiting before clearing current song");
				// Don't set currentSong to null immediately to prevent race conditions
			}
		}, 100); // 100ms delay to let queue polling settle

		return () => {
			clearTimeout(timeoutId);
		};
	}, [songs]);

    const handleSongEnd = async () => {
		console.log("Song ended, moving to next in queue");
		
		if (currentSong && currentSong.submissionID !== -1) {
			console.log(`Removing finished song: ${currentSong.name} (ID: ${currentSong.submissionID})`);
			
			try {
				// Call the backend to remove the finished song
				const response = await axios.post(
					DELETE_SONG_CALL,
					{ "id": currentSong.submissionID, "cookie": cookie },
					{ timeout: 5000 }
				);
				
				if (response.status === 200) {
					console.log("Successfully removed finished song from queue");
					// The queue will be updated automatically through polling
				} else {
					console.error("Failed to remove song:", response.status);
				}
				
			} catch (error) {
				console.error("Error removing finished song:", error);
				updateHostToolsError(error.status || 500);
			}
		} else {
			console.log("No valid current song to remove");
		}
	};
  
    return (
		<>
			{/* Add the YouTube player - this provides the YouTubeControlContext */}
			<YouTubeQueuePlayer currentSong={currentSong} onSongEnd={handleSongEnd} />
			
			<IsHostContext.Provider value={isHost}>
				<CookieContext.Provider value={cookie}>
					<HostToolsContext.Provider value={updateHostToolsError}>
						{hostToolsError !== 0 && (
							<>
								<h2>Error with Host Tools: Code {hostToolsError}</h2>
							</>
						)}
	
						{/* CHANGE: Wrap HostToolsMenu with YouTubeControlContext.Consumer */}
						<YouTubeControlContext.Consumer>
							{(youtubeControls) => (
								<HostToolsMenu songs={songs} youtubeControls={youtubeControls} />
							)}
						</YouTubeControlContext.Consumer>
	
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
