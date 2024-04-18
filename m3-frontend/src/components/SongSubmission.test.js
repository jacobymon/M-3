import React from 'react';
import { render, screen, fireEvent, getByTestId } from '@testing-library/react';
import '@testing-library/jest-dom';
import { searchSongs, submitSong, submitURLSong, SongSubmission } from "./SongSubmission";
import axios from "axios";

// import jest from "jest"
// const MyComponent = require('./myComponent');
// const axios = require('axios');
jest.mock("axios");

const data = {
  status: 200,
  results: [
    {
      id: 1,
      uri: 'URI 1',
      s_len: 'Length 1',
      title: 'Title 1',
      artist: 'Artist 1',
      album: "Album 1"
    },
    {
      id: 2,
      uri: 'URI 2',
      s_len: 'Length 2',
      title: 'Title 2',
      artist: 'Artist 2',
      album: "Album 2"
    },
    {
      id: 3,
      uri: 'URI 3',
      s_len: 'Length 3',
      title: 'Title 3',
      artist: 'Artist 3',
      album: "Album 3"
    },
    {
      id: 4,
      uri: 'URI 4',
      s_len: 'Length 4',
      title: 'Title 4',
      artist: 'Artist 4',
      album: "Album 4"
    },
    {
      id: 5,
      uri: 'URI 5',
      s_len: 'Length 5',
      title: 'Title 5',
      artist: 'Artist 5',
      album: "Album 5"
    },
  ]
};

const selected_song = {
  id: 2,
  uri: 'URI 2',
  s_len: 'Length 2',
  title: 'Title 2',
  artist: 'Artist 2',
  album: "Album 2"
};

const song_url = "Valid Song URL"
        



// May be good to have things return status and message, 
// if necessary, as JSON so that both either can be used depending on case


describe('Search Bar', () => {

  // Search Bar Related Tests
  it('test-auto-search', async () => {
    
    axios.get.mockResolvedValue(data); // Setup mock to resolve with `data`

    let expected_result = {
      status: 200,
      response: data.results
    }

    await expect(searchSongs("T")).resolves.toEqual(expected_result);
    await expect(searchSongs("Th")).resolves.toEqual(expected_result);
    await expect(searchSongs("The")).resolves.toEqual(expected_result);
  });

  it('test-dropdown-select-song', async () => {

    axios.get.mockResolvedValue(data); // Setup mock to resolve with `data`

    let expected_result = {
      status: 200,
      response: data.results
    }

    await expect(searchSongs("T")).resolves.toEqual(expected_result);
    await expect(searchSongs("Th")).resolves.toEqual(expected_result);
    await expect(searchSongs("The")).resolves.toEqual(expected_result);
  });

  it('test-null-searchBar-query', async () => {
    // const errorMessage = 'Please enter a song name to search.';

    let expected_error = {
      status: 400,
      response: 'Please enter a song name to search.'
    }

    // Doesn't need to mock anything because it should catch it before it calls axios

    // axios.get.mockResolvedValue(new Error(errorMessage));

    await expect(searchSongs(null)).resolves.toEqual(expected_error);
  });

  //Backend API Related Tests
  it('test-bad-oauth', async () => {

    let expected_error = {
      status: 403,
      response: 'Bad OAuth request.'
    }

    let bad_response = {
      status: 403,
    }

    //Expect error 403 from backend (TODO)
    axios.get.mockResolvedValue(bad_response);

    await expect(searchSongs("Test bad OAuth")).resolves.toEqual(expected_error);
  });

  it('test-exceed-rate-limits', async () => {
    // const errorMessage = 'Exceeded Spotify search limit. Please wait a few seconds before retrying.';

    // //Expect error 429 from backend (TODO)
    // axios.get.mockResolvedValue(new Error(errorMessage));

    // await expect(searchSongs("Test Exceed Rate Limit")).resolves.toEqual(errorMessage);

    let expected_error = {
      status: 429,
      response: 'Exceeded Spotify search limit. Please wait a few seconds before retrying.'
    }

    let bad_response = {
      status: 429,
    }

    //Expect error 403 from backend (TODO)
    axios.get.mockResolvedValue(bad_response);

    await expect(searchSongs("Test Exceed Rate Limit")).resolves.toEqual(expected_error);

  });

});


describe('Submit Button', () => {

  // Submit Button Related Tests
  it('test-valid-song', async () => {

    const data = {
      status: 200,
    };

    let expected_result = {
      status: 200,
      response: null
    }
    
    axios.post.mockResolvedValue(data); // Setup mock to resolve with `data`

    await expect(submitSong(selected_song)).resolves.toEqual(expected_result);

  });

  it('test-song-null', async () => {


    // const data = {
    //   status: 200,
    // };

    let expected_error = {
      status: 400,
      response: "No song was selected."
    }
    
    // axios.post.mockResolvedValue(data); // Setup mock to resolve with `data`

    await expect(submitSong(null)).resolves.toEqual(expected_error);

  });

  it('test-song-no-title', async () => {

    const selected_song = {
      id: 2,
      uri: 'URI 2',
      s_len: 'Length 2',
      // title: 'Title 2',
      artist: 'Artist 2',
      album: "Album 2"
    };

    const data = {
      status: 400,
    };

    let expected_error = {
      status: 400,
      response: "Could not find the title of the selected song."
    }
    
    // axios.post.mockResolvedValue(data); // Setup mock to resolve with `data`

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);

  });

  it('test-song-no-uri', async () => {

    const selected_song = {
      id: 2,
      // uri: 'URI 2',
      s_len: 'Length 2',
      title: 'Title 2',
      artist: 'Artist 2',
      album: "Album 2"
    };

    const data = {
      status: 400,
    };
    
    let expected_error = {
      status: 400,
      response: "Could not find the song’s URI."
    }
    
    // axios.post.mockResolvedValue(data); // Setup mock to resolve with `data`

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);

  });

  it('test-song-no-artist', async () => {

    const selected_song = {
      id: 2,
      uri: 'URI 2',
      s_len: 'Length 2',
      title: 'Title 2',
      // artist: 'Artist 2',
      album: "Album 2"
    };

    let expected_error = {
      status: 400,
      response: "Could not find the song’s artist."
    }
    
    // axios.post.mockResolvedValue(data); // Setup mock to resolve with `data`

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);

  });

  it('test-song-no-album', async () => {

    const selected_song = {
      id: 2,
      uri: 'URI 2',
      s_len: 'Length 2',
      title: 'Title 2',
      artist: 'Artist 2',
      // album: "Album 2"
    };

    let expected_error = {
      status: 400,
      response: "Could not find the song’s album."
    }
    
    // axios.post.mockResolvedValue(data); // Setup mock to resolve with `data`

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);

  });
  


  //Backend API Related Tests
  it('test-timeout', async () => {

    const data = {
      status: 408,
    };

    let expected_error = {
      status: 408,
      response: "Song submission timed out. Please try again."
    }

    //Expect error 408 from backend (TODO)
    axios.post.mockResolvedValue(data);

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);
  });

  it('test-not-found', async () => {

    const data = {
      status: 404,
    };

    let expected_error = {
      status: 404,
      response: "Could not find host machine. Please try again."
    }

    //Expect error 404 from backend (TODO)
    axios.post.mockResolvedValue(data);

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);

  });

  it('test-internal-server-error', async () => {

    const data = {
      status: 500,
    };

    let expected_error = {
      status: 500,
      response: "An internal server error has occurred. Please try again."
    }

    //Expect error 500 from backend (TODO)
    axios.post.mockResolvedValue(data);

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);
  });

  it('test-generic-api-error', async () => {

    const data = {
      status: 599,  // Any error code that is not already handled
    };

    let expected_error = {
      status: 500,
      response: "An API error has occurred."
    }

    //Expect error 400 or 500 from backend (TODO)
    axios.post.mockResolvedValue(data);

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);
  });

});


describe('URL Textbox', () => {

  // URL Textbox Related Tests
  it('test-url-submit', async () => {

    const data = {
      status: 200,
    };

    let expected_result = {
      status: 200,
      response: null
    }
    
    axios.post.mockResolvedValue(data); // Setup mock to resolve with `data`

    await expect(submitURLSong(song_url)).resolves.toEqual(expected_result);
    
  });

  it('test-bad-url-submit', async () => {

    const data = {
      status: 404,  // Any error code that is not already handled
    };

    let expected_error = {
      status: 404,
      response: "No song was found for that URL."
    }

    //Expect error 400 or 500 from backend (TODO)
    axios.post.mockResolvedValue(data);

    await expect(submitURLSong("Bad Song URL")).resolves.toEqual(expected_error);
    
  });

  it('test-null-url-submit', async () => {

    const errorMessage = 'No URL was provided.';

    let expected_error = {
      status: 404,
      response: "No URL was provided."
    }

    await expect(submitURLSong(null)).resolves.toEqual(expected_error);
    
  });



  //Backend API Related Tests
  it('test-timeout', async () => {

    const data = {
      status: 408,
    };

    let expected_error = {
      status: 408,
      response: "URL Song submission timed out. Please try again."
    }

    //Expect error 408 from backend (TODO)
    axios.post.mockResolvedValue(data);

    await expect(submitURLSong("URL Timeout")).resolves.toEqual(expected_error);
  });

  it('test-not-found', async () => {

    const data = {
      status: 404,
    };

    let expected_error = {
      status: 404,
      response: "Could not find host machine. Please try again."
    }

    //Expect error 404 from backend (TODO)
    axios.post.mockResolvedValue(data);

    await expect(submitURLSong("Host Machine not Found")).resolves.toEqual(expected_error);
  });

  it('test-internal-server-error', async () => {

    const data = {
      status: 500,
    };

    let expected_error = {
      status: 500,
      response: "An internal server error has occurred. Please try again."
    }

    //Expect error 500 from backend (TODO)
    axios.post.mockResolvedValue(data);

    await expect(submitURLSong("URL Internal Server Error")).resolves.toEqual(expected_error);

  });

  it('test-generic-api-error', async () => {

    const data = {
      status: 599,  // Any error code that is not already handled
    };

    let expected_error = {
      status: 500,
      response: "An API error has occurred."
    }

    //Expect error 500 from backend (TODO)
    axios.post.mockResolvedValue(data);

    await expect(submitURLSong("URL API Error")).resolves.toEqual(expected_error);

  });

});

describe('Full System', () => {

  it('test-search-and-submit', async () => {

    const { getByTestId } = render(<SongSubmission />);

    // Expect no errors to start
    let searchBarError = screen.queryByTestId("SearchBarError");
    expect(searchBarError).not.toBeInTheDocument();

    let submitButtonError = screen.queryByTestId("SubmitBarError");
    expect(submitButtonError).not.toBeInTheDocument();

    const searchBar = getByTestId("SearchBar");
    expect(searchBar).toHaveValue('');

    axios.get.mockResolvedValue(data); // Setup mock to resolve with `data`

    let expected_search_result = {
      status: 200,
      response: data.results
    }

    // Entering text into the textbox and simulating if we had gotten the data
    fireEvent.change(searchBar, { target: { value: "T"}});
    await expect(searchSongs("T")).resolves.toEqual(expected_search_result);
    fireEvent.change(searchBar, { target: { value: "Th"}});
    await expect(searchSongs("Th")).resolves.toEqual(expected_search_result);
    fireEvent.change(searchBar, { target: { value: "The"}});

    let search_results = await searchSongs("The");
    expect(search_results).toEqual(expected_search_result);
    
    // Check that there are Result0 - Result4
    expect(getByTestId("Result0")).toBeInTheDocument();
    expect(getByTestId("Result1")).toBeInTheDocument();
    expect(getByTestId("Result2")).toBeInTheDocument();
    expect(getByTestId("Result3")).toBeInTheDocument();
    expect(getByTestId("Result4")).toBeInTheDocument();


    const firstResult = getByTestId("Result0");
    fireEvent.click(firstResult);
    let selected_song = search_results.response[0];

    // Check that the search bar's value now contains the song's name
    expect(searchBar).toHaveValue(selected_song.title);

    // Check that Result0 - Result 4 are gone
    // Commented out for testing testing purposes
    expect(getByTestId("Result0")).not.toBeInTheDocument();
    expect(getByTestId("Result1")).not.toBeInTheDocument();
    expect(getByTestId("Result2")).not.toBeInTheDocument();
    expect(getByTestId("Result3")).not.toBeInTheDocument();
    expect(getByTestId("Result4")).not.toBeInTheDocument();


    const submitButton = getByTestId("SubmitButton");

    const submit_data = {
      status: 200,
    };

    let expected_submit_result = {
      status: 200,
      response: null
    }
    
    axios.post.mockResolvedValue(submit_data); // Setup mock to resolve with `data`

    fireEvent.click(submitButton);
    await expect(submitSong(selected_song)).resolves.toEqual(expected_submit_result);
    
    
    
    // Check that the search bar is now empty
    expect(searchBar).toHaveValue('');
  
    // Check that there are no errors after everything is done
    searchBarError = screen.queryByTestId("SearchBarError");
    expect(searchBarError).not.toBeInTheDocument();

    submitButtonError = screen.queryByTestId("SubmitBarError");
    expect(submitButtonError).not.toBeInTheDocument();





    // fireEvent.click(getByText("Clickable"));
    // Setup: Set searchBar_query to an empty String, set selected_song to null, set search_results to an empty array, set all errors to null.
    // Test: “Click” the search bar, enter “T,” then “h,” then “e,” then “click” the first entry in search_results to move it into selected_song, then “click” the submit button
    // Results: Success (200) response from the backend/a mock. All errors are still null. Selected_song should be set to null, search_query an empty string, and search_results should be made an empty array.
    // Notes: If this test is done correctly, it should only succeed if all other tests that expect success succeed. This can be used as a general warning light if something is wrong and that we should investigate specific test cases.

  });

  it('test-URL-and-submit', async () => {

    const { getByTestId } = render(<SongSubmission />);

    // Expect no errors to start
    let searchBarError = screen.queryByTestId("SearchBarError");
    expect(searchBarError).not.toBeInTheDocument();

    let submitButtonError = screen.queryByTestId("SubmitBarError");
    expect(submitButtonError).not.toBeInTheDocument();

    const URLTestBox = getByTestId("URLTextBox");
    expect(URLTestBox).toHaveValue('');

    // Entering text into the textbox
    fireEvent.change(URLTestBox, { target: { value: "Valid URL"}});

    const URLSubmitButton = getByTestId("URLSubmitButton");

    const submit_data = {
      status: 200,
    };

    let expected_submit_result = {
      status: 200,
      response: null
    }
    
    axios.post.mockResolvedValue(submit_data); // Setup mock to resolve with `data`

    fireEvent.click(URLSubmitButton);
    await expect(submitURLSong(selected_song)).resolves.toEqual(expected_submit_result);
    
    
    // Check that the search bar is now empty
    expect(URLTestBox).toHaveValue('');
  
    // Check that there are no errors after everything is done
    searchBarError = screen.queryByTestId("SearchBarError");
    expect(searchBarError).not.toBeInTheDocument();

    submitButtonError = screen.queryByTestId("SubmitBarError");
    expect(submitButtonError).not.toBeInTheDocument();



    // Setup: Set url_textbox_input to an empty String, set selected_song to null, set search_results to an empty array, set all errors to null.
    // Test: “Click” the url text box bar, enter a valid Spotify song URL then “click” the URL submit button
    // Results: Success (200) response from the backend/a mock. All errors are still null. url_textbox_input should be set to null.
    // Notes: If this test is done correctly, it should only succeed if all other tests that expect success succeed. This can be used as a general warning light if something is wrong and that we should investigate specific test cases.

  });

});
