import React, { useState, useCallback } from 'react';
import axios from "axios";
import debounce from 'lodash.debounce';
// import './myComponent.css'; 

export async function searchSongs(searchbar_query) {
  // Do the API request to Backend, get the results
  // May be good to ensure that there is at least 1 character in the search_query string


  // Check results. Was there an error?
  // If there was an error, set_searchbar_error(true) and        set_searchbar_error_message(“Relevant error message”)
  if (searchbar_query === null) {
    return {
      status: 400,
      response: 'Please enter a song name to search.'
    };
  }


  // If there was no error, set_searchbar_error(false) and set_searchbar_error_message(“No error”)
  // If there was no error, process the results into something usable by the program (ie. trim the JSONs to only include song name, URI, artist, album).
  // If data cannot be found, input a neutral value (ie. “Unknown”)
  // Do set_search_results(processed_data) to set the values of what should appear in the dropdown

  // axios.get("http://localhost:8080/return_results?search_string=" + searchbar_query)
  

  try {
    const response = await axios.get("http://172.28.99.52:8080/return_results?search_string=" + searchbar_query);
    console.log("Successful response: " + response);
    console.log(response);
    
    return {
      status: response.status,
      response: "My Success Message"
    };

  } catch (error) {
    console.log("Error response: ", error);
    
    return {
      status: error.response ? error.response.status : 500,
      response: "My Error Message"
    };

  }

  // const response = await axios.get('https://jsonplaceholder.typicode.com/albums');
  // console.log("searchSongs(\"" + searchbar_query + "\")");
  // // console.log("status: " + response.status);

  // let ret = {
  //   status: response.status,
  //   response: response.results,
  // }
  // return ret;
  // return response.results[0].title;
  
}

export async function submitSong(selected_song) {
  // Check that the selected_song is not null. If it is, set error messages:
   // set_submit_error(true), set_submit_error_message(“No song has been selected”)
   // Return early
  if (selected_song === null) {
    return {
      status: 400,
      response: "No song was selected."
    }
  }


    console.log("submitSong(" + selected_song + ")");


    try {
      const response = await axios.post("https://jsonplaceholder.typicode.com/albums", selected_song);
      console.log("Successful response: " + response);
      console.log(response);
      
      return {
        status: response.status,
        response: "My Success Message"
      };

    } catch (error) {
      console.log("Error response: ", error);
      console.log(error);
      
      return {
        status: error.response ? error.response.status : 500,
        response: "My Error Message"
      };

    }

}

export async function submitURLSong(url_textbox_input) {
  // Check that the URL Textbox is not null. If it is, set error messages:
  // set_submit_error(true), set_submit_error_message(“No URL has been provided”)
  // Return early


  // Attempt to make an API call to the backend to submit the song
  // Example
  // axios.post("http://127.0.0.1:5000/api?songJSON=" + url_textbox_input)
  //   .then(response => {
  //     // Do something with the backend response
  //   })
  //   .catch(error => {
  //     // Handle error
  //     // set_submit_error(true)
  //     // Examine the “error” value to determine what went wrong
  //     // For common errors (ie. Not Found, Timeout), provide adequate feedback
  //     // ie. set_submit_error_message(“Unable to connect to host”)
  //     // or set_submit_error_message(“Your request timed out. Please try again.”)
  //     console.error('Error fetching data:', error);
  //   });
  console.log("Here" + url_textbox_input)

  try {
    const response = await axios.post("http://172.28.99.52:8080/return_results_from_url?spotify_url=" + url_textbox_input);
    console.log("Successful response: " + response);
    console.log(response);
    return {
      status: response.status,
      response: "My Success Message"
    };

  } catch (error) {
    console.log("Error response: ", error);
    console.log(error);
    
    return {
      status: error.response ? error.response.status : 500,
      response: "My Error Message"
    };

  }

  // const response = await axios.post('https://jsonplaceholder.typicode.com/albums', url_textbox_input);
  //   console.log("submitURLSong(" + url_textbox_input + ")");

    // return response.status;
}


export function SongSubmission({ data }) {
  const [searchBarError, setSearchBarError] = useState(null);
  const [submitButtonError, setSubmitButtonError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [URLTextboxInput, setURLTextboxInput] = useState("");


  // const debouncedSearchBar = useCallback(
  //   debounce((newValue) => setSearchQuery(newValue), 1000),
  //   []  // Dependencies array is empty, so the debounced function is created only once
  // );

  const searchSongs_debounced = useCallback(
    debounce((searchInput) => searchSongs(searchInput), 500),
    []  // Dependencies array is empty, so the debounced function is created only once
  );

  const handleSearchBarKeystroke = (e) => {
    setSearchQuery(e.target.value)
    console.log("Pre Search")
    searchSongs_debounced(e.target.value);
    console.log("Post Search")
  }


  return (
    <div>
      <h1>M-3</h1>
      
      <div>
        <input data-testid="SearchBar" placeholder="Search for songs..." onChange={handleSearchBarKeystroke}/>
        <input data-testid="URLTextBox" placeholder="Paste a song URL..." onChange={(e) => setURLTextboxInput(e.target.value)}/>
      </div>
      <div>
        <button data-testid="SubmitButton" onClick={() => submitSong("I submit songs")}>
          Submit Song
        </button>
        <button data-testid="URLSubmitButton" onClick={() => submitURLSong(URLTextboxInput)}>
          Submit Song URL
        </button>
      </div>

      
      <p>{searchQuery}</p>
      <p>{URLTextboxInput}</p>
      <p data-testid={"Result" + 0} onClick={() => console.log("I am the 0 result")}>Hello</p>
      <p data-testid="Result1" onClick={() => console.log("I am the 1 result")}>Hello</p>
      <p data-testid="Result2" onClick={() => console.log("I am the 2 result")}>Hello</p>
      <p data-testid="Result3" onClick={() => console.log("I am the 3 result")}>Hello</p>
      <p data-testid="Result4" onClick={() => console.log("I am the 4 result")}>Hello</p>
      { searchBarError && 
        <div data-testid="SearchBarError">
          Hello there
        </div>
      }
      { submitButtonError && 
        <div data-testid="SubmitButtonError">
          Hello there again
        </div>
      }
    </div>
    
  );

};
