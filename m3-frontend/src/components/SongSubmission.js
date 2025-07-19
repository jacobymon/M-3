import React, { useState, useCallback, useEffect } from "react";
import axios from "axios";
import debounce from "lodash.debounce";
import "./SongSubmission.css";



/**
 * API Call to search for songs on YouTube.
 * 
 * @param {string} searchbar_query The string used to search for songs on YouTube.
 * 
 * @returns {JSON} A JSON object containing the *status* of the request (int) and the *response*
 * in the form of an array of song JSON objects (if status == 200), or an error message (string).
 */
export async function searchYouTubeSongs(searchbar_query) {
  if (searchbar_query === "") {
    return {
      status: 400,
      response: "Please enter a song name to search.",
    };
  }

  try {
    const response = await axios.get(
      `http://${process.env.REACT_APP_BACKEND_IP}:8080/youtube_search?search_string=${searchbar_query}`, 
      { timeout: 5000 }
    );

    console.log("YouTube search response:", response.data); // Log backend response


    switch (response.data.status) {
      case 200:
        console.log("Search results:", response.data.results); // Log search results
        return {
          status: response.data.status,
          response: response.data.results,
        };
      case 500:
        return {
          status: response.data.status,
          response: "An internal server error has occurred. Please try again.",
        };
      default:
        return {
          status: 500,
          response: "An error has occurred in the backend.",
        };
    }
  } catch (error) {
    console.log("Error response: ", error);

    return {
      status: 500,
      response: "A network error has occurred while searching YouTube songs.",
    };
  }
}

/**
 * API Call to submit a YouTube song to the queue based on its URL.
 * 
 * @param {string} url_textbox_input The string representing the YouTube URL to be submitted to the queue.
 * 
 * @returns {JSON} A JSON object containing the *status* of the request (int) and the *response*
 * on success/failure in the form of a string.
 */
export async function submitYouTubeURLSong(url_textbox_input) {
  console.log("Submitting YouTube URL:", url_textbox_input); // Log the URL being submitted

  if (url_textbox_input === "") {
    return {
      status: 400,
      response: "No URL was provided.",
    };
  }

  const backendURL = `http://${process.env.REACT_APP_BACKEND_IP}:8080/youtube_submit_url`;
  console.log("Backend URL:", backendURL); // Log the constructed backend URL

  try {
    const response = await axios.post(
      backendURL,
      { youtube_url: url_textbox_input }, // Send the URL as JSON in the request body
      { timeout: 5000 }
    );

    switch (response.data.status) {
      case 200:
        return {
          status: response.data.status,
          response: "YouTube song successfully submitted.",
        };
      case 404:
        return {
          status: response.data.status,
          response: "No song was found for that URL.",
        };
      case 500:
        return {
          status: response.data.status,
          response: "An internal server error has occurred. Please try again.",
        };
      default:
        return {
          status: 500,
          response: "An error has occurred in the backend.",
        };
    }
  } catch (error) {
    console.log("Error response: ", error);

    return {
      status: 500,
      response: "A network error has occurred while submitting the YouTube song URL.",
    };
  }
}



/**
 * API Call to request a search for songs from the backend.
 * 
 * The Spotify Class Interface will return an array of the relevant songs.
 * 
 * @param {function} searchbar_query The string that is used to search for songs in the backend
 * 
 * @returns {JSON} A JSON object containing the *status* of the request (int) and the *response*
 * in the form of an array of song JSON objects (if status == 200), or an error message (string)
 * 
 */
export async function searchSongs(searchbar_query) {

  // console.log("Attempting to search for songs...");

  if (searchbar_query === "") {
    return {
      status: 400,
      response: "Please enter a song name to search.",
    };
  }

  try {
    const response = await axios.get(

      `http://${process.env.REACT_APP_BACKEND_IP}:8080/return_results?search_string=${searchbar_query}`, {timeout: 5000}
    );

    switch(response.data.search_string.status) {
      case 200:
        return {
          status: response.data.search_string.status,
          response: response.data.search_string.results,
        };
      case 403:
        return {
          status: response.data.search_string.status,
          response: 'Bad OAuth request.',
        };
      case 429:
        return {
          status: response.data.search_string.status,
          response: 'Exceeded Spotify search limit. Please wait a few seconds before retrying.',
        };
      default:
        return {
          status: 500,
          response: 'An error has occured in the backend.',
        };
    }
    
  } catch (error) {
    console.log("Error response: ", error);

    return {
      status: 500,
      response: "A network error has occurred while searching songs.",
    };

  }

}

/**
 * API Call to submit a song to be added to the queue based on its JSON in selected_song.
 * 
 * The Spotify Class Interface will a response to indicate sucess or failure.
 * 
 * @param {function} selected_song The JSON representing the song to be submitted to the queue
 * 
 * @returns {JSON} A JSON object containing the *status* of the request (int) and the *response*
 * on success/failure in the form of a string. Failure messages (status != 200) should be
 * used to set the error messages that are displayed to the user.
 * 
 */
export async function submitSong(selected_song) {

  if (selected_song === null) {
    return {
      status: 400,
      response: "No song was selected.",
    };
  }else if (selected_song.title === undefined) {
    return {
      status: 400,
      response: "Could not find the song’s title."
    }
  }else if (selected_song.uri === undefined) {
    return {
      status: 400,
      response: "Could not find the song’s URI."
    }
  }else if (selected_song.artist === undefined) {
    return {
      status: 400,
      response: "Could not find the song’s artist."
    }
  }else if (selected_song.album === undefined) {
    return {
      status: 400,
      response: "Could not find the song’s album."
    }
  }else if (selected_song.s_len === undefined) {
    return {
      status: 400,
      response: "Could not find the song’s length."
    }
  }

  // console.log("Attempting to submit song..."); 

  try {


    const response = await axios.post(`http://${process.env.REACT_APP_BACKEND_IP}:8080/submit_song`, 
    {
      status: 200,
      search_results: selected_song,
    }, 
    {timeout: 7000});

    // console.log(response);

    console.log(response);


    switch(response.data.status){
      case 200: 
        return {
          status: response.data.status,
          response: "My success message (submitSong)",
        };
      case 500:
        return {
          status: response.data.status,
          response: "An internal server error has occurred. Please try again."
        }
      default: 
        return {
          status: 500,
          response: "An error has occured in the backend."
        }
    }
    
  } catch (error) {
    console.log(error);

    return {
      status: 500,
      response: "A network error has occurred while submitting the song.",
    };

  }
}


/**
 * API Call to submit a song to the queue based on its URL when sharing a song on Spotify.
 * 
 * The Spotify Class Interface will a response to indicate sucess or failure.
 * 
 * @param {function} url_textbox_input The string representing the URL to be submitted to the queue
 * 
 * @returns {JSON} A JSON object containing the *status* of the request (int) and the *response*
 * on success/failure in the form of a string. Failure messages (status != 200) should be
 * used to set the error messages that are displayed to the user.
 * 
 */
export async function submitURLSong(url_textbox_input) {

  if (url_textbox_input === "") {
    return {
      status: 400,
      response: "No URL was provided.",
    };
  }

  // console.log("Attempting to submit URL...");

  try {

    const response = await axios.post(`http://${process.env.REACT_APP_BACKEND_IP}:8080/return_results_from_url?spotify_url=${url_textbox_input}`, null, {timeout: 5000});
    // console.log(response);

    switch(response.data.spotify_url.status) {
      case 200:
        return {
          status: response.data.spotify_url.status,
          response: "My Success Message (Submit URL Song)",
        };
      case 404:
        return {
          status: response.data.spotify_url.status,
          response: "No song was found for that URL.",
        };
      case 500:
        return {
          status: response.data.spotify_url.status,
          response: "An internal server error has occurred. Please try again."
        };
      default:
        return {
          status: 500,
          response: "An error has occured in the backend."
        }; 
    }
    
  } catch (error) {
    console.log("Error response: ", error);

    return {
      status: 500,
      response: "A network error has occured while submitting the song URL.",
    };
  }

}

/**
 * The fields and buttons that handle submitting songs to the Universal Queue in the backend.
 * It allows for searching of songs and submitting those songs by clicking on them or by
 * entering in a song's URL.
 * 
 * It displays error messages related to the status of the backend API requests, indicating
 * what went wrong with the given transaction.
 * 
 * @returns The JSX component of SongSubmission and all of its functionality
 */
export function SongSubmission() {
  const [searchBarError, setSearchBarError] = useState("");             // Hold error messages related to the search bar
  const [submitButtonError, setSubmitButtonError] = useState("");       // Hold error messages related to song submission
  const [spotifySearchQuery, setSpotifySearchQuery] = useState("");                   // Represents and holds the value in the search bar
  const [URLTextboxInput, setURLTextboxInput] = useState("");           // Represents and holds the value in the URL text box
  const [searchSongsResponse, setSearchSongsResponse] = useState(null); // Holds the returned value from searchSongs as it is being debounced
  const [searchResults, setSearchResults] = useState("");               // Holds an array of songs for the dropdown
  //const [hideSearchResults, setHideSearchResults] = useState(false);    // A toggle for hiding the dropdown if it is not clicked
  const [selectedSong, setSelectedSong] = useState(null);               // The song that has been selected from the dropdown
  const [searchYouTubeResults, setSearchYouTubeResults] = useState(""); // Holds an array of YouTube songs for the dropdown
  const [selectedYouTubeSong, setSelectedYouTubeSong] = useState(null); // The YouTube song selected from the dropdown
  const [youtubeSearchQuery, setYouTubeSearchQuery] = useState("");     // YouTube-specific search query
  const [hideSpotifySearchResults, setHideSpotifySearchResults] = useState(false); // Spotify dropdown visibility
  const [hideYouTubeSearchResults, setHideYouTubeSearchResults] = useState(false); // YouTube dropdown visibility
  /**
   * A useEffect to check if we are clicking outside the dropdown and run a function.
   *  
   * For all functions, it will run handleClickOutsideDropdown unless the 
   * command **e.stopPropagation() is run. Functions that contain this are
   * considered to be "inside" the dropdown or unaffected by this logic.
  */
  useEffect(() => {
    document.addEventListener("click", handleClickOutsideDropdown);

    return () => {
      document.removeEventListener("click", handleClickOutsideDropdown);
    };
  }, []);

  /**
   * Hides the search results dropdown.
   * It is only run when clicking outside the dropdown due to the useEffect above.
   */
  const handleClickOutsideDropdown = () => {
    setHideSpotifySearchResults(true); // Hide Spotify dropdown
    setHideYouTubeSearchResults(true); // Hide YouTube dropdown
  };


  /**
 * Handles running a debounced searchYouTubeSongs whenever the search bar is changed.
 * 
 * @param {Event} e The event response that comes with interacting with a component.
 */
  const debouncedSearchYouTubeSongs = useCallback(
    debounce((query) => {
      searchYouTubeSongs(query).then((response) => {
        console.log("YouTube search results:", response.response); // Log search results
  
        if (response.status === 200) {
          setSearchYouTubeResults(response.response);
          console.log("Updated searchYouTubeResults:", response.response); // Log updated state
          setSearchBarError("");
        } else {
          setSearchYouTubeResults(null);
          setSearchBarError(response.response);
        }
      });
    }, 500), // Debounce delay of 500ms
    []
  );
  
  const handleYouTubeSearchBarKeystroke = (e) => {
    setSearchBarError("");
    setSubmitButtonError("");
    setYouTubeSearchQuery(e.target.value); // Update YouTube-specific search query
    debouncedSearchYouTubeSongs(e.target.value); // Trigger debounced search
  };

/**
 * Handles calling submitYouTubeURLSong to submit the song stored in *URLTextboxInput* to the backend.
 */
const handleSubmitYouTubeURL = async () => {
  if (!selectedYouTubeSong || !selectedYouTubeSong.video_url) {
    setSubmitButtonError("Please select a valid YouTube song from the dropdown.");
    return;
  }

  setSubmitButtonError("Submitting YouTube URL...");

  // Use the video_url from the selected song
  let response_json = await submitYouTubeURLSong(selectedYouTubeSong.video_url);

  if (response_json.status === 200) {
    setSubmitButtonError("");
    setYouTubeSearchQuery(""); // Clear the search bar
    setSelectedYouTubeSong(null); // Clear the selected song
  } else {
    setSubmitButtonError(response_json.response);
  }
};

  /**
   * Handles emptying the search bar if a song has been selected but the search query is backspaced
   * Meant to simulate deleting the selected song from the search bar.
   * 
   * @param {Event} e The event response that comes with interacting with a component.
   * This is usually provided as an implicit paramter when the function is called.
  */ 
  const handleSearchBarKeyDown = (e, platform) => {
    if (platform === "Spotify" && selectedSong && e.key === "Backspace") {
      setSpotifySearchQuery(""); // Clear Spotify search query
      setSelectedSong(null); // Clear selected Spotify song
    } else if (platform === "YouTube" && selectedYouTubeSong && e.key === "Backspace") {
      setYouTubeSearchQuery(""); // Clear YouTube search query
      setSelectedYouTubeSong(null); // Clear selected YouTube song
    }
  };

  /**
  * A function wrapper for searchSongs that debounces the call.
  * That means, if called multiple times in the time interval specified,
  * it only returns the results of the most recent call of the function.
  * 
  * It sets the return value of searchSongs to searchSongsResponse.
  */ 
  const searchSongs_debounced = useCallback(
    debounce((searchInput) => 
      searchSongs(searchInput).then(setSearchSongsResponse), 500),
    [searchSongs, setSearchSongsResponse]
  );

  /**
   * Handles running a debounced searchSongs whenever the search bar is changed.
   * 
   * @param {Event} e The event response that comes with interacting with a component.
   * This is usually provided as an implicit paramter when the function is called.
  */ 
  const handleSearchBarKeystroke = async (e) => {
    setSearchBarError("");
    setSubmitButtonError("");
  
    setSpotifySearchQuery(e.target.value); // Update Spotify-specific search query
  
    searchSongs_debounced(e.target.value); // Trigger Spotify search
  };
  

  /**
   * A useEffect to handle the response to searchSongs after searchsongsResponse is
   * updated after handleSearchBarKeystroke finishes.
   * 
   * This function is created to allow for debouncing functionality as the debounce
   * delays our response. Doing it this way, we react to the response when it happens.
   *  
  */
  React.useEffect(() => {
    console.log(searchSongsResponse)

    if (searchSongsResponse === null) return;

    if (searchSongsResponse.status === 200) {
      setSearchResults(searchSongsResponse.response);
      setSearchBarError("");
    } else {
      setSearchResults(null);
      setSearchBarError(searchSongsResponse.response);
    }
  }, [searchSongsResponse]) // Run this useEffect whenever searchSongsResponse changes

  /**
   * Handles displaying the dropdown when clicking on the search bar, if it was previously 
   * hidden. This function does stopPropagation to ignore handleClickOutsideDropdown.
   * 
   * @param {Event} e The event response that comes with interacting with a component.
   * This is usually provided as an implicit paramter when the function is called.
  */ 
  const handleSearchBarClick = (e, platform) => {
    e.stopPropagation(); // Prevents the behavior of clicking outside the dropdown
  
    if (platform === "Spotify") {
      setHideSpotifySearchResults(false); // Show Spotify dropdown
      setHideYouTubeSearchResults(true);  // Hide YouTube dropdown
    } else if (platform === "YouTube") {
      setHideYouTubeSearchResults(false); // Show YouTube dropdown
      setHideSpotifySearchResults(true);  // Hide Spotify dropdown
    }
  };

  /**
   * Handle selecting a song from the dropdown.
   * 
   * This function ignores the handleClickOutsideDropdown as we are clicking in the dropdown.
   * 
   * @param {JSON} song The song JSON object that corresponds to the entry in the
   * dropdown menu that has been selected.
   * 
   * @param {Event} e The event response that comes with interacting with a component.
   * This is usually provided as an implicit paramter when the function is called.
  */ 
  const handleDropdownSelectSong = (song, e, platform) => {
    e.stopPropagation(); // Prevents the behavior of clicking outside the dropdown
  
    console.log(`Selected: ${song.title} from ${platform}`);
    if (platform === "Spotify") {
      setSpotifySearchQuery(song.title); // Update Spotify search query
      setSelectedSong(song); // Set selected Spotify song
      setSearchResults(null); // Clear Spotify dropdown results
    } else if (platform === "YouTube") {
      setYouTubeSearchQuery(song.title); // Update YouTube search query
      setSelectedYouTubeSong(song); // Set selected YouTube song
      setSearchYouTubeResults(null); // Clear YouTube dropdown results
    }
  };

  /**
   * Handles calling submitSong to submit the song stored in *selectedSong* to the backend.
  */ 
  const handleSubmitSong = async () => {

    setSubmitButtonError("Submitting song...");

    let response_json = await submitSong(selectedSong);

    if (response_json.status === 200) {
      setSelectedSong(null);
      setSpotifySearchQuery("");
      setSubmitButtonError("");
    }else {
      setSubmitButtonError(response_json.response)
    }
    
  }

  /**
   * Handles calling submitURLSong to submit the song stored in *URLTextboxInput* to the backend.
  */ 
  const handleSubmitURL = async () => {

    setSubmitButtonError("Submitting URL...");

    let response_json = await submitURLSong(youtubeSearchQuery);

    console.log(response_json)

    if (response_json.status === 200) {
      setSubmitButtonError("")
      setURLTextboxInput("")
    }else {
      setSubmitButtonError(response_json.response);
    }
  }

//   return (
//     <div className="songSubmission">
      
//       {/* The container for the search and submit functionality*/}
//       <div className="searchContainer">

//         {/* The input field for searching for songs */}
//         <input
//           className="searchBar"
//           data-testid="SearchBar"
//           placeholder="Search for songs..."
//           value={searchQuery}
//           onClick={handleSearchBarClick} // Handles showing the dropdown if it was previously hidden
//           onChange={handleSearchBarKeystroke} // Handling searching with each keystroke
//           onKeyDown={handleSearchBarKeyDown} // Handles if a song was selected but we want to re-search
//         />

//         {/* The conditionally rendering dropdown menu for selecting songs */}
//         {!hideSearchResults && searchResults && (
//           <div className="dropdownContainer">
//             {searchResults.map((item, index) => (
//               <div
//                 className="dropdownItem"
//                 data-testid={"Result" + index} // Give each item a numbered testid for testing
//                 key={index}
//                 onClick={(e) => handleDropdownSelectSong(item, e)}
//               >
//                 <div className="itemTitle">{item.title}</div>
//                 <div className="itemSubtitle">
//                   {item.artist} - {item.album}
//                 </div>
//               </div>
//             ))}
//           </div>
//         )}

//         {/* The button to submit the song that has been selected from the dropdown */}
//         <button
//           data-testid="SubmitButton"
//           className="submitButton"
//           onClick={handleSubmitSong}
//         >
//           Submit Song
//         </button>
//       </div>

//       {/* The container for the URL and submit functionality*/}
//       <div className="searchContainer">
//         {/* The input field for submitting song URLs to be added to the queue */}
//         <input
//           className="searchBar"
//           data-testid="URLTextBox"
//           placeholder="Paste a song URL..."
//           value={URLTextboxInput}
//           onChange={(e) => setURLTextboxInput(e.target.value)}
//         />

//         {/* The button to submit the song URL that was passed into the URL textbox */}
//         <button
//           data-testid="URLSubmitButton"
//           className="submitButton"
//           onClick={handleSubmitURL}
//         >
//           Submit URL
//         </button>
//       </div>

//       {/* The field where errors related to the search bar and URL textbox will be displayed */}
//       {searchBarError && (
//         <div className="errorMessage" data-testid="SearchBarError">{searchBarError}</div>
//       )}

//       {/* The field where errors related to song submission will be displayed */}
//       {submitButtonError && (
//         <div className="errorMessage" data-testid="SubmitButtonError">{submitButtonError}</div>
//       )}

//     </div>
//   );
// }

return (
  <div className="songSubmission">
    {/* Spotify Search and Submission */}
    <div className="searchContainer">
      <h3>Search Spotify Songs</h3>
      <input
        className="searchBar"
        data-testid="SpotifySearchBar"
        placeholder="Search for Spotify songs..."
        value={spotifySearchQuery} // Spotify-specific search query
        onClick={(e) => handleSearchBarClick(e, "Spotify")} // Handles showing the Spotify dropdown
        onChange={handleSearchBarKeystroke} // Handling searching with each keystroke
        onKeyDown={handleSearchBarKeyDown} // Handles if a song was selected but we want to re-search
      />
      {!hideSpotifySearchResults && searchResults && (
        <div className="dropdownContainer">
          {searchResults.map((item, index) => (
            <div
              className="dropdownItem"
              data-testid={"SpotifyResult" + index}
              key={index}
              onClick={(e) => handleDropdownSelectSong(item, e, "Spotify")}
            >
              <div className="itemTitle">{item.title}</div>
              <div className="itemSubtitle">
                {item.artist} - {item.album}
              </div>
            </div>
          ))}
        </div>
      )}
      <button
        data-testid="SpotifySubmitButton"
        className="submitButton"
        onClick={handleSubmitSong}
      >
        Submit Spotify Song
      </button>
    </div>

    {/* YouTube Search and Submission */}
    <div className="searchContainer">
      <h3>Search YouTube Songs</h3>
      <input
        className="searchBar"
        data-testid="YouTubeSearchBar"
        placeholder="Search for YouTube songs..."
        value={youtubeSearchQuery} // YouTube-specific search query
        onClick={(e) => handleSearchBarClick(e, "YouTube")} // Handles showing the YouTube dropdown
        onChange={handleYouTubeSearchBarKeystroke} // Handling searching with each keystroke
      />
      {!hideYouTubeSearchResults && searchYouTubeResults && (
        <div className="dropdownContainer">
          {searchYouTubeResults.map((item, index) => (
            <div
              className="dropdownItem"
              data-testid={"YouTubeResult" + index}
              key={index}
              onClick={(e) => handleDropdownSelectSong(item, e, "YouTube")}
            >
              <div className="itemTitle">{item.title}</div>
              <div className="itemSubtitle">{item.artist}</div>
            </div>
          ))}
        </div>
      )}
      <button
        data-testid="YouTubeSubmitButton"
        className="submitButton"
        onClick={handleSubmitYouTubeURL}
      >
        Submit YouTube Song
      </button>
    </div>
  </div>
);
}