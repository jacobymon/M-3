import React, { useState, useCallback, useEffect } from "react";
import axios from "axios";
import debounce from "lodash.debounce";
import "./SongSubmission.css";

export async function searchSongs(searchbar_query) {

  console.log("Attempting to search for songs...");
  // Do the API request to Backend, get the results
  // May be good to ensure that there is at least 1 character in the search_query string

  // Check results. Was there an error?
  // If there was an error, set_searchbar_error(true) and        set_searchbar_error_message(“Relevant error message”)
  if (searchbar_query === "") {
    return {
      status: 400,
      response: "Please enter a song name to search.",
    };
  }

  // return {
  //   status: 200, // Status of what was actually returned
  //   response: [
  //     {
  //       id: 1,
  //       uri: "URI 1",
  //       s_len: 11,
  //       title: searchbar_query + " 1",
  //       artist: "Artist 1",
  //       album: "Album 1",
  //     },
  //     {
  //       id: 2,
  //       uri: "URI 2",
  //       s_len: 22,
  //       title: searchbar_query + " 2",
  //       artist: "Artist 2",
  //       album: "Album 2",
  //     },
  //     {
  //       id: 3,
  //       uri: "URI 3",
  //       s_len: 33,
  //       title: searchbar_query + " 3",
  //       artist: "Artist 3",
  //       album: "Album 3",
  //     },
  //     {
  //       id: 4,
  //       uri: "URI 4",
  //       s_len: 44,
  //       title: searchbar_query + " 4",
  //       artist: "Artist 4",
  //       album: "Album 4",
  //     },
  //     {
  //       id: 5,
  //       uri: "URI 5",
  //       s_len: 55,
  //       title: searchbar_query + " 5",
  //       artist: "Artist 5",
  //       album: "Album 5",
  //     },
  //   ],
  // };

  // If there was no error, set_searchbar_error(false) and set_searchbar_error_message(“No error”)
  // If there was no error, process the results into something usable by the program (ie. trim the JSONs to only include song name, URI, artist, album).
  // If data cannot be found, input a neutral value (ie. “Unknown”)
  // Do set_search_results(processed_data) to set the values of what should appear in the dropdown

  // axios.get("http://localhost:8080/return_results?search_string=" + searchbar_query)

  try {
    const response = await axios.get(
      "http://172.28.248.60:8080/return_results?search_string=" + searchbar_query, {timeout: 5000}
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

export async function submitSong(selected_song) {
  // Check that the selected_song is not null. If it is, set error messages:
  // set_submit_error(true), set_submit_error_message(“No song has been selected”)
  // Return early
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

  console.log("Attempting to submit song...");

  let post_data =  {
    status: 200,
    search_results: selected_song,
  }

  try {
    const response = await axios.post("http://172.28.248.60:8080/submit_song", post_data, {timeout: 5000});
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
    // console.log("Error response: ", error);
    console.log(error);

    // console.log("Submit button error!!!")
    return {
      status: 500,
      response: "A network error has occurred while submitting the song.",
    };

  }
}

export async function submitURLSong(url_textbox_input) {

  if (url_textbox_input === "") {
    return {
      status: 400,
      response: "No URL was provided.",
    };
  }

  console.log("Attempting to submit URL...");

  try {
    const response = await axios.post("http://172.28.248.60:8080/return_results_from_url?spotify_url=" + url_textbox_input, null, {timeout: 5000});
    console.log(response);

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
    // console.log(error);

    return {
      status: 500,
      response: "A network error has occured while submitting the song URL.",
    };
  }

  // const response = await axios.post('https://jsonplaceholder.typicode.com/albums', url_textbox_input);
  //   console.log("submitURLSong(" + url_textbox_input + ")");

  // return response.status;
}

export function SongSubmission({ data }) {
  const [searchBarError, setSearchBarError] = useState("");         // Hold error messages related to the search bar
  const [submitButtonError, setSubmitButtonError] = useState("");   // Hold error messages related to song submission
  const [searchQuery, setSearchQuery] = useState("");                 // Represents and holds the value in the search bar
  const [URLTextboxInput, setURLTextboxInput] = useState("");         // Represents and holds the value in the URL text box
  const [searchSongsResponse, setSearchSongsResponse] = useState(null);
  const [searchResults, setSearchResults] = useState("");             // Holds an array of songs for the dropdown
  const [hideSearchResults, setHideSearchResults] = useState(false);  // A toggle for hiding the dropdown if it is not clicked
  const [selectedSong, setSelectedSong] = useState(null);             // The song that has been selected from the dropdown

  
  // A use effect to check if we are clicking outside the dropdown and run a function.
  useEffect(() => {
    document.addEventListener("click", handleClickOutsideDropdown);

    return () => {
      document.removeEventListener("click", handleClickOutsideDropdown);
    };
  }, []);

  // Handles emptying the search bar if a song has been selected but the search query is backspaced
  // Meant to simulate deleting the selected song from the search bar
  const handleSearchBarKeyDown = (e) => {

    if (selectedSong && e.key === "Backspace") {
      setSearchQuery("");
      setSelectedSong(null);
    }
  };

  // A function wrapper for searchSongs that debounces the call.
  // That means, if called multiple times in the time interval specified,
  // it only returns the results of the most recent call of the function.
  // It then sets the return value of searchSongs to searchSongsResponse
  const searchSongs_debounced = useCallback(
    debounce((searchInput) => 
      searchSongs(searchInput).then(setSearchSongsResponse), 500),
    [searchSongs, setSearchSongsResponse]
  );

  // Handles running a debounced searchSongs whenever the search bar is changed
  const handleSearchBarKeystroke = async (e) => {

    setSearchBarError("");
    setSubmitButtonError("")

    setSearchQuery(e.target.value);

    searchSongs_debounced(e.target.value);

  };

  // Handles updaing variables after the searchSongsResponse is updated
  // during searchSongs_debounced
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

  // Handles displaying the dropdown when clicking on the search bar,
  // if it was previously hidden
  const handleSearchBarClick = (e) => {
    // Prevents the behavior to be done clicking outside the dropdown
    e.stopPropagation();

    console.log("Clicked searchbar");
    setHideSearchResults(false);
  };

  // Handle selecting a song from the dropdown
  const handleDropdownSelectSong = (song, e) => {
    // Prevents the behavior to be done clicking outside the dropdown
    e.stopPropagation();

    console.log(`Selected: ${song.title}`);
    setSearchQuery(song.title);
    setSelectedSong(song);
    setSearchResults(null);
  };

  // Hides the search results dropdown.
  // Run when clicking outside the dropdown due to the useEffect
  const handleClickOutsideDropdown = () => {
    setHideSearchResults(true);
  };

  const handleSubmitSong = async () => {

    setSubmitButtonError("Submitting song...");

    let response_json = await submitSong(selectedSong);

    if (response_json.status === 200) {
      setSelectedSong(null);
      setSearchQuery("");
      setSubmitButtonError("");
    }else {
      setSubmitButtonError(response_json.response)
    }
    
  }

  const handleSubmitURL = async () => {

    setSubmitButtonError("Submitting URL...");

    let response_json = await submitURLSong(URLTextboxInput);

    console.log(response_json)

    if (response_json.status === 200) {
      setSubmitButtonError("")
      setURLTextboxInput("")
    }else {
      setSubmitButtonError(response_json.response);
    }
  }

  return (
    <div className="songSubmission">
      <div className="searchContainer">

        {/* The input field for searching for songs */}
        <input
          className="searchBar"
          data-testid="SearchBar"
          placeholder="Search for songs..."
          value={searchQuery}
          onClick={handleSearchBarClick} // Handles showing the dropdown if it was previously hidden
          onChange={handleSearchBarKeystroke} // Handling searching with each keystroke
          onKeyDown={handleSearchBarKeyDown} // Handles if a song was selected but we want to re-search
        />

        {/* The conditionally rendering dropdown menu for selecting songs */}
        {!hideSearchResults && searchResults && (
          <div className="dropdownContainer">
            {searchResults.map((item, index) => (
              <div
                className="dropdownItem"
                data-testid={"Result" + index} // Give each item a numbered testid for testing purposes
                key={index}
                onClick={(e) => handleDropdownSelectSong(item, e)}
              >
                <div className="itemTitle">{item.title}</div>
                <div className="itemSubtitle">
                  {item.artist} - {item.album}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* The button to submit the song that has been selected from the dropdown */}
        <button
          data-testid="SubmitButton"
          className="submitButton"
          onClick={handleSubmitSong}
        >
          Submit Song
        </button>
      </div>

      <div className="searchContainer">
        {/* The input field for submitting song URLs to be added to the queue */}
        <input
          className="searchBar"
          data-testid="URLTextBox"
          placeholder="Paste a song URL..."
          value={URLTextboxInput}
          onChange={(e) => setURLTextboxInput(e.target.value)}
        />

        {/* The button to submit the song URL that was passed into the URL textbox */}
        <button
          data-testid="URLSubmitButton"
          className="submitButton"
          onClick={handleSubmitURL}
        >
          Submit URL
        </button>
      </div>
      {/* The field where errors related to the search bar and URL textbox will be displayed */}
      {searchBarError && (
        <div className="errorMessage" data-testid="SearchBarError">{searchBarError}</div>
      )}

      {/* The field where errors related to song submission will be displayed */}
      {submitButtonError && (
        <div className="errorMessage" data-testid="SubmitButtonError">{submitButtonError}</div>
      )}

    </div>
  );
}
